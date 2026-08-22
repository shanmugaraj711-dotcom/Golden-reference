"""Vercel entrypoint for the Project Factory.

GET /api -> health and configuration status.
GET /api?prompt=... -> one controlled Gemini inference when configured.

The API key is server-side only and is never stored in GitHub.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project_factory.gemini_provider import GeminiProvider
from project_factory.model_provider import ModelRequest
from project_factory.model_router import ModelRouter, RoutingPolicy


def build_response(prompt: str) -> tuple[int, dict]:
    provider = GeminiProvider()

    if not prompt:
        return 200, {
            "service": "project-factory",
            "status": "ok",
            "engine": "project_factory",
            "geminiConfigured": provider.available(),
            "model": provider.model,
            "spendCeiling": 0,
        }

    if not provider.available():
        return 503, {
            "service": "project-factory",
            "status": "blocked",
            "reason": "GEMINI_API_KEY is not configured",
        }

    try:
        result = ModelRouter(
            [provider],
            RoutingPolicy(prefer_local=False, allow_external=True, max_cost=0.0),
        ).complete(ModelRequest(
            task="factory-proof",
            instruction=prompt,
            context={
                "system": "You are the Project Factory proof worker. Return a concise, useful response."
            },
        ))
    except Exception as exc:
        return 502, {
            "service": "project-factory",
            "status": "model_error",
            "error": str(exc),
        }

    return 200, {
        "service": "project-factory",
        "status": "ok",
        "provider": result.provider,
        "model": result.model,
        "output": result.output,
        "usage": {
            "inputTokens": result.input_tokens,
            "outputTokens": result.output_tokens,
        },
        "estimatedCost": result.estimated_cost,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        prompt = (query.get("prompt") or [""])[0].strip()
        status, payload = build_response(prompt)
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        return
