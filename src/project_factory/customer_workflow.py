"""Customer-facing 10-step workflow with explicit admin range/override control."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStep(str, Enum):
    INTAKE = "intake"
    REQUIREMENTS = "requirements"
    PLAN = "plan"
    BUILD = "build"
    TEST = "test"
    REPAIR = "repair"
    QUALITY = "quality"
    PACKAGE = "package"
    DEPLOY = "deploy"
    DELIVER = "deliver"


STEPS: tuple[WorkflowStep, ...] = tuple(WorkflowStep)


@dataclass
class WorkflowVersion:
    version: int
    input_text: str
    output_target: str = "web"
    started_at_step: int = 1
    end_at_step: int = 10
    status: str = "pending"
    feedback: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CustomerWorkflow:
    project_id: str
    current_version: int = 0
    active: WorkflowVersion | None = None
    history: list[WorkflowVersion] = field(default_factory=list)

    def start(self, input_text: str, *, start_step: int = 1, end_step: int = 10,
              output_target: str = "web", feedback: str | None = None) -> WorkflowVersion:
        self._validate_range(start_step, end_step)
        self.current_version += 1
        run = WorkflowVersion(
            version=self.current_version,
            input_text=input_text.strip(),
            output_target=output_target,
            started_at_step=start_step,
            end_at_step=end_step,
            feedback=feedback,
            status="running",
        )
        if not run.input_text:
            raise ValueError("customer input is required")
        self.active = run
        self.history.append(run)
        return run

    def revise(self, feedback: str, *, start_step: int, end_step: int | None = None,
               output_target: str | None = None) -> WorkflowVersion:
        """Create a new version from targeted customer feedback; never mutates Vn."""
        if not feedback.strip():
            raise ValueError("feedback is required")
        previous = self.active or (self.history[-1] if self.history else None)
        if previous is None:
            raise ValueError("cannot revise before the first workflow run")
        return self.start(
            feedback,
            start_step=start_step,
            end_step=end_step if end_step is not None else previous.end_at_step,
            output_target=output_target or previous.output_target,
            feedback=feedback,
        )

    def pause(self, reason: str = "admin pause") -> None:
        if self.active is None:
            raise ValueError("no active workflow")
        self.active.status = "paused"
        self.active.metadata["pauseReason"] = reason

    def resume(self) -> WorkflowVersion:
        if self.active is None:
            raise ValueError("no active workflow")
        if self.active.status != "paused":
            raise ValueError("workflow is not paused")
        self.active.status = "running"
        return self.active

    def approve(self) -> WorkflowVersion:
        if self.active is None:
            raise ValueError("no active workflow")
        self.active.status = "approved"
        return self.active

    @staticmethod
    def _validate_range(start_step: int, end_step: int) -> None:
        if not 1 <= start_step <= 10 or not 1 <= end_step <= 10:
            raise ValueError("workflow steps must be between 1 and 10")
        if start_step > end_step:
            raise ValueError("start step cannot be after end step")


def step_slice(start_step: int, end_step: int) -> tuple[WorkflowStep, ...]:
    CustomerWorkflow._validate_range(start_step, end_step)
    return STEPS[start_step - 1:end_step]
