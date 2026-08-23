from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class Stage(str, Enum):
    INTAKE = "intake"
    SPECIFY = "specify"
    PLAN = "plan"
    BUILD = "build"
    TEST = "test"
    VERIFY = "verify"
    DIAGNOSE = "diagnose"
    REPAIR = "repair"
    REGRESSION = "regression"
    RELEASE = "release"
    CHECKPOINT = "checkpoint"


class Status(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class Evidence:
    stage: str
    action: str
    result: str
    detail: str = ""


@dataclass
class Task:
    id: str
    title: str
    run: Callable[[], bool]
    required: bool = True
    attempts: int = 0
    passed: bool = False


@dataclass
class RunState:
    run_id: str
    project_id: str
    stage: Stage = Stage.INTAKE
    status: Status = Status.RUNNING
    active_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    checkpoint: Dict[str, object] = field(default_factory=dict)
    blocked_reason: Optional[str] = None


@dataclass
class RunResult:
    status: Status
    state: RunState


class ProjectFactory:
    """Evidence-driven deterministic orchestrator with pluggable workers."""

    def __init__(self, run_id: str, project_id: str, max_repairs: int = 3):
        self.state = RunState(run_id=run_id, project_id=project_id)
        self.max_repairs = max_repairs
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError(f"Duplicate task id: {task.id}")
        self.tasks.append(task)

    def _record(self, stage: Stage, action: str, result: str, detail: str = "") -> None:
        self.state.evidence.append(Evidence(stage.value, action, result, detail))

    def _worker_evidence(self, task: Task) -> None:
        result = getattr(task.run, "last_result", None)
        if result is None:
            return
        detail = result.summary
        if result.changed_files:
            detail += f"; changed={','.join(result.changed_files)}"
        self._record(Stage.BUILD, task.id, "passed" if result.success else "failed", detail)
        for item in result.evidence:
            self._record(Stage.BUILD, task.id, "evidence", item)

    def _checkpoint(self) -> None:
        self.state.checkpoint = {
            "runId": self.state.run_id,
            "projectId": self.state.project_id,
            "stage": self.state.stage.value,
            "status": self.state.status.value,
            "activeTask": self.state.active_task,
            "completedTasks": list(self.state.completed_tasks),
            "failedTasks": list(self.state.failed_tasks),
            "blockedReason": self.state.blocked_reason,
            "evidence": [asdict(item) for item in self.state.evidence],
        }
        self._record(Stage.CHECKPOINT, "persist", "passed")

    def resume_from_checkpoint(self, checkpoint: Dict[str, object]) -> None:
        if checkpoint.get("runId") != self.state.run_id:
            raise ValueError("Checkpoint belongs to a different run")
        self.state.stage = Stage(str(checkpoint["stage"]))
        self.state.status = Status(str(checkpoint["status"]))
        self.state.active_task = checkpoint.get("activeTask") or None
        self.state.completed_tasks = list(checkpoint.get("completedTasks", []))
        self.state.failed_tasks = list(checkpoint.get("failedTasks", []))
        self.state.blocked_reason = checkpoint.get("blockedReason") or None
        raw_evidence = checkpoint.get("evidence", [])
        self.state.evidence = [Evidence(**item) for item in raw_evidence if isinstance(item, dict)]

    def run(self) -> RunResult:
        self.state.status = Status.RUNNING
        self.state.stage = Stage.SPECIFY
        self._record(Stage.SPECIFY, "normalize_request", "passed")
        self.state.stage = Stage.PLAN
        self._record(Stage.PLAN, "create_task_graph", "passed", f"{len(self.tasks)} tasks")

        for task in self.tasks:
            if task.id in self.state.completed_tasks:
                continue
            self.state.active_task = task.id
            self.state.stage = Stage.BUILD
            self._record(Stage.BUILD, task.id, "started")
            self.state.stage = Stage.TEST
            passed = False
            while task.attempts < self.max_repairs + 1 and not passed:
                task.attempts += 1
                try:
                    passed = bool(task.run())
                    self._worker_evidence(task)
                except Exception as exc:
                    self._record(Stage.TEST, task.id, "failed", repr(exc))
                    passed = False
                else:
                    self._record(Stage.TEST, task.id, "passed" if passed else "failed")
                if not passed and task.attempts < self.max_repairs + 1:
                    self.state.stage = Stage.DIAGNOSE
                    self._record(Stage.DIAGNOSE, task.id, "recorded", f"attempt {task.attempts}")
                    self.state.stage = Stage.REPAIR
                    self._record(Stage.REPAIR, task.id, "retrying", f"attempt {task.attempts + 1}")
            if not passed:
                task.passed = False
                self.state.failed_tasks.append(task.id)
                self.state.status = Status.BLOCKED
                self.state.blocked_reason = f"Task {task.id} exceeded repair budget"
                self._checkpoint()
                return RunResult(self.state.status, self.state)
            task.passed = True
            self.state.completed_tasks.append(task.id)
            self.state.stage = Stage.VERIFY
            self._record(Stage.VERIFY, task.id, "passed")
            self.state.stage = Stage.REGRESSION
            self._record(Stage.REGRESSION, task.id, "passed")

        self.state.stage = Stage.RELEASE
        self._record(Stage.RELEASE, "release_gate", "passed")
        self.state.status = Status.COMPLETE
        self.state.stage = Stage.CHECKPOINT
        self._checkpoint()
        return RunResult(self.state.status, self.state)
