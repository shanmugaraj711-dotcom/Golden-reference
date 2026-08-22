from project_factory.project_record import apply_dashboard_evidence, new_project_record


def test_new_project_record():
    record = new_project_record("cust_1", "Demo", "Build a site", "deploy")
    assert record["customerId"] == "cust_1"
    assert record["projectName"] == "Demo"
    assert record["deliveryModel"] == "deploy"
    assert record["lifecycleState"] == "INTAKE"
    assert record["ownership"]["owner"] == "cust_1"


def test_evidence_updates_delivery_without_changing_owner():
    record = new_project_record("cust_1", "Demo", "Build a site", "managed")
    updated = apply_dashboard_evidence(record, {
        "state": "MANAGED",
        "version": "1.1.0",
        "repository": "cust/demo",
        "hostingTarget": "vercel",
        "productionUrl": "https://demo.example.com",
        "qualityGate": "PASS",
        "deployment": "VERIFIED",
        "healthCheck": "PASS",
        "events": [{"label": "v1.1 deployed"}],
    })
    assert updated["ownership"]["owner"] == "cust_1"
    assert updated["lifecycleState"] == "MANAGED"
    assert updated["currentVersion"] == "1.1.0"
    assert updated["verification"]["healthCheck"] == "PASS"
    assert len(updated["events"]) == 2
