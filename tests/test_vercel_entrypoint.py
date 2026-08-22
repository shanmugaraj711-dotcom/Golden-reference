from api.index import build_response


def test_health_endpoint_does_not_require_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    status, payload = build_response("")

    assert status == 200
    assert payload["service"] == "project-factory"
    assert payload["status"] == "ok"
    assert payload["geminiConfigured"] is False
    assert payload["spendCeiling"] == 0
