from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProductType = Literal["web", "api", "android", "ios", "saas", "automation", "other"]
CustomerDeliveryMode = Literal["transfer", "deploy", "managed"]


@dataclass(frozen=True)
class ProjectIntake:
    customer_id: str
    project_name: str
    brief: str
    product_type: ProductType
    delivery_mode: CustomerDeliveryMode
    acceptance_criteria: tuple[str, ...] = ()


def normalize_intake(payload: dict) -> ProjectIntake:
    """Validate and normalize customer intake before a Factory run is created."""
    customer_id = str(payload.get("customer_id", "")).strip()
    project_name = str(payload.get("project_name", "")).strip()
    brief = str(payload.get("brief", "")).strip()
    product_type = str(payload.get("product_type", "web")).strip().lower()
    delivery_mode = str(payload.get("delivery_mode", "transfer")).strip().lower()

    if not customer_id:
        raise ValueError("customer_id is required")
    if not project_name:
        raise ValueError("project_name is required")
    if not brief:
        raise ValueError("brief is required")
    if product_type not in {"web", "api", "android", "ios", "saas", "automation", "other"}:
        raise ValueError("unsupported product_type")
    if delivery_mode not in {"transfer", "deploy", "managed"}:
        raise ValueError("delivery_mode must be transfer, deploy, or managed")

    raw_criteria = payload.get("acceptance_criteria") or []
    if not isinstance(raw_criteria, (list, tuple)):
        raise ValueError("acceptance_criteria must be a list")
    criteria = tuple(str(item).strip() for item in raw_criteria if str(item).strip())

    return ProjectIntake(
        customer_id=customer_id,
        project_name=project_name,
        brief=brief,
        product_type=product_type,
        delivery_mode=delivery_mode,
        acceptance_criteria=criteria,
    )
