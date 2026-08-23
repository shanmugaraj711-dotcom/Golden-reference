"""Production-facing run contract: persist every observable stage transition."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class LiveRun:
    project_id: str
    run_id: str
    start_step: int = 1
    end_step: int = 10
    status: str = "RUNNING"
    current_step: int = 1
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def transition(self, step: int, status: str, detail: str = "") -> dict[str, Any]:
        if not self.start_step <= step <= self.end_step:
            raise ValueError("step is outside the selected execution range")
        if step < self.current_step:
            raise ValueError("live run cannot move backwards")
        self.current_step = step
        self.status = status
        event = {
            "projectId": self.project_id,
            "runId": self.run_id,
            "step": step,
            "status": status,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.evidence.append(event)
        return event

    def complete(self, detail: str = "delivery verified") -> dict[str, Any]:
        return self.transition(self.end_step, "DELIVERED", detail)


def execute_live(run: LiveRun, worker: Callable[[int], tuple[bool, str]]) -> LiveRun:
    """Execute only the admin-selected range; stop and persist on first failure."""
    for step in range(run.start_step, run.end_step + 1):
        run.transition(step, "RUNNING", f"step {step} started")
        ok, detail = worker(step)
        if not ok:
            run.transition(step, "BLOCKED", detail)
            return run
        run.transition(step, "PASSED", detail)
    run.complete()
    return run
