from project_factory.dashboard_evidence import dashboard_evidence_from_manifest


def test_dashboard_evidence_from_manifest():
    result = dashboard_evidence_from_manifest({
        "project": {"name": "Demo", "brief": "A site"},
        "version": "2.1.0",
        "delivery": {
            "mode": "managed",
            "repository": "customer/demo",
            "hosting_target": "vercel",
            "production_url": "https://demo.example.com",
        },
        "verification": {
            "quality_gate": "PASS",
            "deployment": "VERIFIED",
            "health_check": "PASS",
        },
        "ownership": {"owner": "customer"},
        "events": [{"label": "deployed"}],
    })
    assert result["projectName"] == "Demo"
    assert result["deliveryModel"] == "managed"
    assert result["state"] == "MANAGED"
    assert result["productionUrl"] == "https://demo.example.com"
    assert result["qualityGate"] == "PASS"
    assert result["healthCheck"] == "PASS"
