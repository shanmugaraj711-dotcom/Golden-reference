from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

SYSTEM = """You are the Project Factory code-generation worker. Return ONLY valid JSON with this shape: {\"project_name\": string, \"files\": [{\"path\": string, \"content\": string}]}. Build a small, runnable project from the user's request. Never include markdown fences. Paths must be relative, must not start with /, must not contain .., and must not be .git paths. Prefer dependency-free HTML/CSS/JS for web fixtures unless the request requires another stack."""


def call_gemini(request: str) -> dict:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    payload = {
        "contents": [{"parts": [{"text": SYSTEM + "\n\nUSER REQUEST:\n" + request}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {detail[:1000]}") from exc
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def safe_path(value: str) -> Path:
    p = Path(value)
    if p.is_absolute() or ".." in p.parts or ".git" in p.parts:
        raise ValueError(f"unsafe generated path: {value}")
    if not re.fullmatch(r"[A-Za-z0-9._/ -]+", value):
        raise ValueError(f"invalid generated path: {value}")
    return p


def main() -> int:
    request = os.environ.get("FACTORY_REQUEST") or "Create a simple responsive landing page for a local coffee shop with hero, menu, hours, and contact section."
    workspace = Path(os.environ.get("FACTORY_WORKSPACE", "generated-project")).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    result = call_gemini(request)
    files = result.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("model returned no files")
    written = []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
            raise ValueError("invalid file object returned by model")
        path = safe_path(item["path"])
        target = workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["content"], encoding="utf-8")
        written.append(str(path))
    print(json.dumps({"status": "generated", "project": result.get("project_name", "generated-project"), "files": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
