from __future__ import annotations

from typing import Any, Mapping


def dashboard_evidence_from_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a Factory delivery manifest into the customer dashboard contract."""
    delivery = manifest.get("delivery") or {}
    verification = manifest.get("verification") or {}
    ownership = manifest.get("ownership") or {}
    project = manifest.get("project") or {}

    mode = delivery.get("mode") or manifest.get("delivery_mode") or "transfer"
    state = manifest.get("state") or ("MANAGED" if mode == "managed" else "LIVE" if delivery.get("production_url") else "HANDED_OFF")

    return {
        "projectName": project.get("name") or manifest.get("project_name") or "Unnamed project",
        "brief": project.get("brief") or manifest.get("brief") or "",
        "deliveryModel": mode,
        "version": manifest.get("version") or "1.0.0",
        "state": state,
        "nextAction": manifest.get("next_action") or ("View the live project" if state in {"LIVE", "MANAGED"} else "Review delivery"),
        "repository": delivery.get("repository") or manifest.get("repository") or "",
        "hostingTarget": delivery.get("hosting_target") or manifest.get("hosting_target") or "",
        "productionUrl": delivery.get("production_url") or manifest.get("production_url") or "",
        "qualityGate": verification.get("quality_gate") or manifest.get("quality_gate") or "PENDING",
        "deployment": verification.get("deployment") or manifest.get("deployment") or "PENDING",
        "healthCheck": verification.get("health_check") or manifest.get("health_check") or "PENDING",
        "ownership": ownership.get("owner") or manifest.get("owner") or "",
        "maintenance": "Managed" if mode == "managed" else "Not enrolled",
        "events": manifest.get("events") or [],
    }
