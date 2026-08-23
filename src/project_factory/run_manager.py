"""Persistent customer-factory run state and fail-closed stage transitions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class RunStage(str, Enum):
    INTAKE = "INTAKE"
    PLAN = "PLAN"
    BUILD = "BUILD"
    TEST = "TEST"
    REPAIR = "REPAIR"
    REPOSITORY = "REPOSITORY"
    DEPLOY = "DEPLOY"
    HEALTH = "HEALTH"
    EVIDENCE = "EVIDENCE"
    HANDOFF = "HANDOFF"
    MANAGED = "MANAGED"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


@dataclass
class FactoryRun:
    run_id: str
    customer_id: str
    project_id: str
    stage: RunStage = RunStage.INTAKE
    status: str = "RUNNING"
    completed_stages: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    blocker: str | None = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def checkpoint(self, stage: RunStage, evidence: dict[str, Any] | None = None) -> None:
        if stage == RunStage.COMPLETE and not self._ready_for_complete():
            raise ValueError("cannot complete a run before deployment, health, evidence and handoff are proven")
        if stage not in self.completed_stages:
            self.completed_stages.append(stage.value)
        self.stage = stage
        self.status = "COMPLETE" if stage == RunStage.COMPLETE else "RUNNING"
        self.blocker = None
        if evidence:
            self.evidence.update(evidence)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def block(self, reason: str) -> None:
        self.stage = RunStage.BLOCKED
        self.status = "BLOCKED"
        self.blocker = reason
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def resume(self) -> None:
        if self.status != "BLOCKED":
            return
        self.status = "RUNNING"
        self.stage = RunStage(self.completed_stages[-1]) if self.completed_stages else RunStage.INTAKE
        self.blocker = None
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def attempt(self, stage: RunStage, max_attempts: int = 3) -> bool:
        count = self.attempts.get(stage.value, 0) + 1
        self.attempts[stage.value] = count
        if count > max_attempts:
            self.block(f"retry budget exhausted for {stage.value}")
            return False
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True

    def _ready_for_complete(self) -> bool:
        required = {RunStage.REPOSITORY.value, RunStage.DEPLOY.value, RunStage.HEALTH.value, RunStage.EVIDENCE.value, RunStage.HANDOFF.value}
        return required.issubset(set(self.completed_stages))

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "customerId": self.customer_id,
            "projectId": self.project_id,
            "stage": self.stage.value,
            "status": self.status,
            "completedStages": self.completed_stages,
            "evidence": self.evidence,
            "attempts": self.attempts,
            "blocker": self.blocker,
            "updatedAt": self.updated_at,
        }


def new_run(customer_id: str, project_id: str) -> FactoryRun:
    return FactoryRun(run_id=f"run_{uuid4().hex}", customer_id=customer_id, project_id=project_id)
