"""Vercel entrypoint for the Project Factory.

GET /api -> health and configuration status (never exposes the key).
GET /api?prompt=... -> one controlled Gemini inference when configured.

The API key is server-side only. Nothing secret is stored in GitHub.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Vercel executes this module from the repository root. Add the source tree
# explicitly so the factory package is available without extra dependencies.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project_factory.gemini_provider import GeminiProvider
from project_factory.model_provider import ModelRequest
from project_factory.model_router import ModelRouter, RoutingPolicy


def _response(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"},
        "body": json.dumps(payload),
    }


def _query(request) -> dict[str, list[str]]:
    if isinstance(request, dict):
        params = request.get("queryStringParameters") or {}
        prompt = params.get("prompt", "")
        return {"prompt": [prompt] if isinstance(prompt, str) else []}
    path = getattr(request, "path", "") or getattr(request, "url", "")
    return parse_qs(urlparse(path).query)


def app(request):
    provider = GeminiProvider()
    params = _query(request)
    prompt = (params.get("prompt") or [""])[0].strip()

    if not prompt:
        return _response(200, {
            "service": "project-factory",
            "status": "ok",
            "engine": "project_factory",
            "geminiConfigured": provider.available(),
            "model": provider.model,
            "spendCeiling": 0,
        })

    if not provider.available():
        return _response(503, {
            "service": "project-factory",
            "status": "blocked",
            "reason": "GEMINI_API_KEY is not configured",
        })

    try:
        result = ModelRouter(
            [provider],
            RoutingPolicy(prefer_local=False, allow_external=True, max_cost=0.0),
        ).complete(ModelRequest(
            task="factory-proof",
            instruction=prompt,
            context={"system": "You are the Project Factory proof worker. Return a concise, useful response."},
        ))
    except Exception as exc:
        return _response(502, {
            "service": "project-factory",
            "status": "model_error",
            "error": str(exc),
        })

    return _response(200, {
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
    })


handler = app
