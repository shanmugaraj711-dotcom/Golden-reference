from project_factory.dashboard_evidence import dashboard_evidence_from_manifest


def manifest(mode, production_url=""):
    return {
        "project": {"name": f"{mode}-demo", "brief": "acceptance"},
        "version": "1.0.0",
        "delivery": {
            "mode": mode,
            "repository": f"customer/{mode}-demo",
            "hosting_target": "vercel" if mode != "transfer" else "",
            "production_url": production_url,
        },
        "verification": {
            "quality_gate": "PASS",
            "deployment": "VERIFIED" if mode != "transfer" else "HANDED_OFF",
            "health_check": "PASS" if mode != "transfer" else "NOT_REQUIRED",
        },
        "ownership": {"owner": "customer"},
        "events": [{"label": "validated"}, {"label": "delivered"}],
    }


def test_transfer_acceptance_contract():
    result = dashboard_evidence_from_manifest(manifest("transfer"))
    assert result["deliveryModel"] == "transfer"
    assert result["qualityGate"] == "PASS"
    assert result["deployment"] == "HANDED_OFF"


def test_deploy_acceptance_contract():
    result = dashboard_evidence_from_manifest(manifest("deploy", "https://deploy.example.com"))
    assert result["deliveryModel"] == "deploy"
    assert result["productionUrl"] == "https://deploy.example.com"
    assert result["healthCheck"] == "PASS"


def test_managed_acceptance_contract():
    result = dashboard_evidence_from_manifest(manifest("managed", "https://managed.example.com"))
    assert result["deliveryModel"] == "managed"
    assert result["state"] == "MANAGED"
    assert result["healthCheck"] == "PASS"
