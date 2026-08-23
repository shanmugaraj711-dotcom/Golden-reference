from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class CustomerStage(str, Enum):
    INTAKE = "intake"
    AUTH = "authorization"
    BUILD = "build"
    QUALITY = "quality"
    REPOSITORY = "repository"
    DEPLOY = "deploy"
    HEALTH = "health"
    EVIDENCE = "evidence"
    HANDOFF = "handoff"
    MANAGED = "managed"
    COMPLETE = "complete"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CustomerRequest:
    request_id: str
    project_name: str
    delivery_mode: str
    destination_repository: str
    hosting_target: str = "vercel"


@dataclass
class CustomerEvidence:
    stage: str
    status: str
    detail: str
    url: Optional[str] = None


@dataclass
class CustomerRun:
    request_id: str
    stage: CustomerStage = CustomerStage.INTAKE
    status: str = "running"
    attempts: Dict[str, int] = field(default_factory=dict)
    evidence: List[CustomerEvidence] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    deployment_url: Optional[str] = None


class CustomerAutomation:
    """Idempotent customer delivery state machine.

    Every stage is an explicit capability. A capability must return a truthful
    result; the orchestrator never infers deployment/health/handoff evidence.
    Failed stages stop the run and can be resumed from persisted state.
    """

    ORDER = (
        CustomerStage.INTAKE,
        CustomerStage.AUTH,
        CustomerStage.BUILD,
        CustomerStage.QUALITY,
        CustomerStage.REPOSITORY,
        CustomerStage.DEPLOY,
        CustomerStage.HEALTH,
        CustomerStage.EVIDENCE,
        CustomerStage.HANDOFF,
    )

    def __init__(self, request: CustomerRequest, max_attempts: int = 3):
        if request.delivery_mode not in {"transfer", "deploy", "managed"}:
            raise ValueError("delivery_mode must be transfer, deploy, or managed")
        if not request.request_id.strip() or not request.project_name.strip():
            raise ValueError("request_id and project_name are required")
        if not request.destination_repository.strip():
            raise ValueError("destination_repository is required")
        self.request = request
        self.max_attempts = max_attempts
        self.run = CustomerRun(request_id=request.request_id)

    def _record(self, stage: CustomerStage, status: str, detail: str, url: Optional[str] = None) -> None:
        self.run.evidence.append(CustomerEvidence(stage.value, status, detail, url))

    def execute(self, capabilities: Dict[CustomerStage, Callable[[], object]]) -> CustomerRun:
        for stage in self.ORDER:
            if self.request.delivery_mode == "transfer" and stage == CustomerStage.DEPLOY:
                break
            if self.request.delivery_mode == "transfer" and stage in {CustomerStage.HEALTH}:
                break

            self.run.stage = stage
            passed = False
            for attempt in range(1, self.max_attempts + 1):
                self.run.attempts[stage.value] = attempt
                capability = capabilities.get(stage)
                if capability is None:
                    self.run.status = "blocked"
                    self.run.stage = CustomerStage.BLOCKED
                    self.run.blocked_reason = f"missing capability: {stage.value}"
                    self._record(stage, "blocked", self.run.blocked_reason)
                    return self.run
                try:
                    result = capability()
                    ok, detail, url = self._normalize_result(result)
                except Exception as exc:
                    ok, detail, url = False, repr(exc), None
                self._record(stage, "passed" if ok else "failed", detail, url)
                if ok:
                    passed = True
                    if url:
                        self.run.deployment_url = url
                    break
            if not passed:
                self.run.status = "blocked"
                self.run.stage = CustomerStage.BLOCKED
                self.run.blocked_reason = f"stage {stage.value} exceeded retry budget"
                return self.run

        if self.request.delivery_mode == "managed":
            self.run.stage = CustomerStage.MANAGED
            capability = capabilities.get(CustomerStage.MANAGED)
            if capability is None:
                self.run.status = "blocked"
                self.run.stage = CustomerStage.BLOCKED
                self.run.blocked_reason = "missing capability: managed"
                self._record(CustomerStage.MANAGED, "blocked", self.run.blocked_reason)
                return self.run
            ok, detail, url = self._normalize_result(capability())
            self._record(CustomerStage.MANAGED, "passed" if ok else "failed", detail, url)
            if not ok:
                self.run.status = "blocked"
                self.run.stage = CustomerStage.BLOCKED
                self.run.blocked_reason = "managed acceptance failed"
                return self.run

        self.run.stage = CustomerStage.COMPLETE
        self.run.status = "complete"
        self._record(CustomerStage.COMPLETE, "passed", "customer delivery acceptance complete", self.run.deployment_url)
        return self.run

    @staticmethod
    def _normalize_result(result: object) -> tuple[bool, str, Optional[str]]:
        if isinstance(result, tuple):
            if len(result) == 2:
                return bool(result[0]), str(result[1]), None
            if len(result) == 3:
                return bool(result[0]), str(result[1]), result[2]
        if isinstance(result, bool):
            return result, "capability returned boolean", None
        raise TypeError("capability must return bool or (bool, detail[, url])")

    def checkpoint(self) -> dict:
        return {
            "requestId": self.run.request_id,
            "stage": self.run.stage.value,
            "status": self.run.status,
            "attempts": dict(self.run.attempts),
            "blockedReason": self.run.blocked_reason,
            "deploymentUrl": self.run.deployment_url,
            "evidence": [item.__dict__ for item in self.run.evidence],
        }
