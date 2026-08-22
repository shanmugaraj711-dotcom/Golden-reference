from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# "transfer" = build in the Factory environment, then hand the project to the customer.
# "managed" = Factory retains operational ownership and provides ongoing maintenance.
# "decide_later" = build in a controlled environment and defer the ownership decision.
DeliveryMode = Literal["transfer", "managed", "decide_later"]


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
    if request.mode not in ("transfer", "managed", "decide_later"):
        raise ValueError("mode must be transfer, managed, or decide_later")
    if not request.source_artifact.strip():
        raise ValueError("source_artifact is required")
    if request.deploy_target not in ("vercel", "none"):
        raise ValueError("deploy_target must be vercel or none")

    mode = request.mode
    return DeliveryPlan(
        project_name=request.project_name.strip(),
        mode=mode,
        repository_required=True,
        vercel_required=request.deploy_target == "vercel",
        customer_transfer_required=mode == "transfer",
        maintenance_expected=mode == "managed",
        handoff_required=mode == "transfer",
        decision_deferred=mode == "decide_later",
        source_artifact=request.source_artifact.strip(),
    )
