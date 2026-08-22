from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Ownership = Literal["customer", "managed"]


@dataclass(frozen=True)
class DeliveryRequest:
    project_name: str
    ownership: Ownership
    source_artifact: str
    deploy_target: str


@dataclass(frozen=True)
class DeliveryPlan:
    project_name: str
    ownership: Ownership
    repository_required: bool
    vercel_required: bool
    customer_transfer_required: bool
    source_artifact: str


def plan_delivery(request: DeliveryRequest) -> DeliveryPlan:
    if not request.project_name.strip():
        raise ValueError("project_name is required")
    if request.ownership not in ("customer", "managed"):
        raise ValueError("ownership must be customer or managed")
    if not request.source_artifact.strip():
        raise ValueError("source_artifact is required")
    if request.deploy_target not in ("vercel", "none"):
        raise ValueError("deploy_target must be vercel or none")

    return DeliveryPlan(
        project_name=request.project_name.strip(),
        ownership=request.ownership,
        repository_required=True,
        vercel_required=request.deploy_target == "vercel",
        customer_transfer_required=request.ownership == "customer",
        source_artifact=request.source_artifact.strip(),
    )
