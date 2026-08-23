"""Session-independent lifecycle worker for persisted customer projects.

The worker advances only after the supplied stage adapter returns observable evidence.
Provider calls are injected, keeping orchestration independent from Firebase/Vercel/GitHub.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Any


STAGES = ("INTAKE", "BUILDING", "VERIFYING", "READY", "DELIVERED")


@dataclass(frozen=True)
class StageResult:
    passed: bool
    evidence: Mapping[str, Any]
    error: str | None = None


class LifecycleWorker:
    def __init__(self, load: Callable[[str], dict], persist: Callable[[str, dict], None], adapters: Mapping[str, Callable[[dict], StageResult]]):
        self.load = load
        self.persist = persist
        self.adapters = adapters

    def advance(self, project_id: str, stop_after: str = "DELIVERED") -> dict:
        if stop_after not in STAGES:
            raise ValueError(f"invalid stop_after: {stop_after}")
        project = dict(self.load(project_id))
        current = str(project.get("lifecycleState", "INTAKE")).upper()
        if current not in STAGES:
            raise ValueError(f"invalid lifecycle state: {current}")
        stop_index = STAGES.index(stop_after)
        start_index = STAGES.index(current)

        for index in range(start_index, stop_index + 1):
            stage = STAGES[index]
            adapter = self.adapters.get(stage)
            if adapter is None:
                if stage == "INTAKE":
                    self._advance(project, stage, {"intake": "received"})
                    continue
                self._block(project, f"no adapter registered for {stage}")
                break
            try:
                result = adapter(dict(project))
            except Exception as exc:
                self._block(project, f"{stage}: {type(exc).__name__}: {exc}")
                break
            if not result.passed:
                self._block(project, result.error or f"{stage} failed")
                break
            self._advance(project, stage, dict(result.evidence))
        return project

    def _advance(self, project: dict, stage: str, evidence: dict) -> None:
        project["lifecycleState"] = stage
        project["deliveryEvidence"] = {**dict(project.get("deliveryEvidence") or {}), stage: evidence}
        project["nextCustomerAction"] = {
            "INTAKE": "Factory build starting",
            "BUILDING": "Factory verification starting",
            "VERIFYING": "Project is ready for delivery",
            "READY": "Delivery handoff starting",
            "DELIVERED": "Delivery completed",
        }[stage]
        self.persist(str(project["projectId"]), project)

    def _block(self, project: dict, reason: str) -> None:
        project["factoryStatus"] = "BLOCKED"
        project["factoryBlocker"] = reason
        project["nextCustomerAction"] = "Factory requires attention before continuing"
        self.persist(str(project["projectId"]), project)
