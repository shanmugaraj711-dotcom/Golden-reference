from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


def new_project_record(customer_id: str, project_name: str, brief: str, delivery_model: str) -> dict[str, Any]:
    if not customer_id.strip():
        raise ValueError("customer_id is required")
    if not project_name.strip():
        raise ValueError("project_name is required")
    if not brief.strip():
        raise ValueError("brief is required")
    if delivery_model not in {"transfer", "deploy", "managed"}:
        raise ValueError("invalid delivery_model")
    now = datetime.now(timezone.utc).isoformat()
    return {
        "customerId": customer_id,
        "projectId": f"proj_{uuid4().hex}",
        "projectName": project_name.strip(),
        "brief": brief.strip(),
        "deliveryModel": delivery_model,
        "lifecycleState": "INTAKE",
        "currentVersion": "0.1.0",
        "repository": "",
        "hostingTarget": "",
        "productionUrl": "",
        "verification": {
            "qualityGate": "PENDING",
            "deployment": "PENDING",
            "healthCheck": "PENDING",
        },
        "ownership": {"owner": customer_id},
        "maintenance": "Managed" if delivery_model == "managed" else "Not enrolled",
        "events": [{"time": now, "state": "INTAKE", "label": "Project created"}],
        "createdAt": now,
        "updatedAt": now,
    }


def apply_dashboard_evidence(record: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Merge immutable delivery evidence into a project record without changing ownership."""
    result = dict(record)
    result["lifecycleState"] = evidence.get("state", result.get("lifecycleState"))
    result["currentVersion"] = evidence.get("version", result.get("currentVersion"))
    result["repository"] = evidence.get("repository", result.get("repository"))
    result["hostingTarget"] = evidence.get("hostingTarget", result.get("hostingTarget"))
    result["productionUrl"] = evidence.get("productionUrl", result.get("productionUrl"))
    result["verification"] = {
        "qualityGate": evidence.get("qualityGate", "PENDING"),
        "deployment": evidence.get("deployment", "PENDING"),
        "healthCheck": evidence.get("healthCheck", "PENDING"),
    }
    result["updatedAt"] = datetime.now(timezone.utc).isoformat()
    result["events"] = [*record.get("events", []), *evidence.get("events", [])]
    return result
