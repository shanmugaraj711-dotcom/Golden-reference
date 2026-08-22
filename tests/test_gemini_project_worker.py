from __future__ import annotations

import json
from pathlib import Path

import scripts.gemini_project_worker as worker


def test_safe_path_rejects_escape():
    for value in ("../secret", "/tmp/file", ".git/config"):
        try:
            worker.safe_path(value)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe path accepted: {value}")


def test_worker_writes_model_files(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    monkeypatch.setenv("FACTORY_WORKSPACE", str(tmp_path / "generated"))
    monkeypatch.setenv("FACTORY_REQUEST", "make a tiny web page")
    monkeypatch.setattr(worker, "call_gemini", lambda _: {
        "project_name": "fixture-site",
        "files": [
            {"path": "index.html", "content": "<h1>Factory</h1>"},
            {"path": "assets/app.js", "content": "console.log('ok')"},
        ],
    })
    assert worker.main() == 0
    assert (tmp_path / "generated" / "index.html").read_text() == "<h1>Factory</h1>"
    assert (tmp_path / "generated" / "assets" / "app.js").exists()
