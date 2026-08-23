"""Admin controls for bounded, resumable factory execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .customer_workflow import CustomerWorkflow, WorkflowVersion


@dataclass
class AdminCommand:
    action: str
    start_step: int = 1
    end_step: int = 10
    output_target: str = "web"
    instruction: str = ""


def execute_command(flow: CustomerWorkflow, command: AdminCommand) -> WorkflowVersion | None:
    action = command.action.lower()
    if action == "start":
        return flow.start(command.instruction, start_step=command.start_step, end_step=command.end_step, output_target=command.output_target)
    if action == "revise":
        return flow.revise(command.instruction, start_step=command.start_step, end_step=command.end_step, output_target=command.output_target)
    if action == "pause":
        flow.pause(command.instruction or "admin pause")
        return flow.active
    if action == "resume":
        return flow.resume()
    if action == "approve":
        return flow.approve()
    raise ValueError(f"unsupported admin action: {command.action}")


def dashboard_state(flow: CustomerWorkflow) -> dict[str, Any]:
    active = flow.active
    return {
        "projectId": flow.project_id,
        "currentVersion": flow.current_version,
        "active": active.__dict__ if active else None,
        "history": [item.__dict__ for item in flow.history],
        "controls": ["start", "revise", "pause", "resume", "approve"],
        "stageRange": {"min": 1, "max": 10},
    }
