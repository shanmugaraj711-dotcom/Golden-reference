from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_customer_dashboard_exposes_delivery_actions():
    html = (ROOT / "dashboard" / "index.html").read_text()
    assert 'id="approvalForm"' in html
    assert 'id="changeRequestForm"' in html
    assert 'id="customerHistory"' in html


def test_customer_dashboard_uses_project_api_for_actions():
    js = (ROOT / "dashboard" / "app.js").read_text()
    assert "action:'approve'" in js
    assert "action:'change_request'" in js
    assert "p.approvals" in js
    assert "p.changeRequests" in js
