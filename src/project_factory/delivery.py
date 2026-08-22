from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Customer-facing V2 models:
# transfer = build, validate, and hand the project to the customer.
# deploy = build, validate, and deliver a live deployed project.
# managed = build, deploy, retain operational ownership, and maintain.
# decide_later is retained as a backward-compatible internal option.
DeliveryMode = Literal["transfer", "deploy", "managed", "decide_later"]


@dataclass(frozen=True)
class DeliveryRequest:
    project_name: str
    mode: DeliveryMode
    source_artifact: str
    deploy_target: str


@dataclass(frozen=True)
class DeliveryPlan:
    project_name: str
    mode: DeliveryMode
    repository_required: bool
    vercel_required: bool
    customer_transfer_required: bool
    maintenance_expected: bool
    handoff_required: bool
    decision_deferred: bool
    source_artifact: str


def plan_delivery(request: DeliveryRequest) -> DeliveryPlan:
    if not request.project_name.strip():
        raise ValueError("project_name is required")
    if request.mode not in ("transfer", "deploy", "managed", "decide_later"):
        raise ValueError("mode must be transfer, deploy, managed, or decide_later")
    if not request.source_artifact.strip():
        raise ValueError("source_artifact is required")
    if request.deploy_target not in ("vercel", "none"):
        raise ValueError("deploy_target must be vercel or none")

    mode = request.mode
    return DeliveryPlan(
        project_name=request.project_name.strip(),
        mode=mode,
        repository_required=True,
        vercel_required=(request.deploy_target == "vercel" and mode in ("deploy", "managed")),
        customer_transfer_required=mode == "transfer",
        maintenance_expected=mode == "managed",
        handoff_required=mode in ("transfer", "deploy"),
        decision_deferred=mode == "decide_later",
        source_artifact=request.source_artifact.strip(),
    )
