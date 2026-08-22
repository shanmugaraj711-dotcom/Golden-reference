"""Vercel entrypoint for the Project Factory.

The health/model endpoint and the project-record endpoint are intentionally
handled here as a routing-safe fallback. This keeps /api/projects working even
when Vercel normalizes Python function routes through /api/index.py.
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
from project_factory.firestore_store import create_project, get_project
from project_factory.project_record import new_project_record


def send_json(request: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Cache-Control", "no-store")
    request.send_header("Content-Length", str(len(body)))
    request.end_headers()
    request.wfile.write(body)


def is_projects_path(path: str) -> bool:
    return path.rstrip("/") == "/api/projects"


def create_project_from_request(request: BaseHTTPRequestHandler):
    try:
        length = int(request.headers.get("Content-Length", "0"))
        data = json.loads(request.rfile.read(length) or b"{}")
        record = new_project_record(
            str(data.get("customerId", "")),
            str(data.get("projectName", "")),
            str(data.get("brief", "")),
            str(data.get("deliveryModel", "")),
        )
        create_project(record)
        send_json(request, 201, {"status": "created", "project": record})
    except (ValueError, json.JSONDecodeError) as exc:
        send_json(request, 400, {"status": "invalid_request", "error": str(exc)})
    except RuntimeError as exc:
        send_json(request, 503, {"status": "persistence_not_configured", "error": str(exc)})
    except Exception as exc:
        send_json(request, 500, {"status": "error", "error": str(exc)})


def get_project_from_request(request: BaseHTTPRequestHandler):
    project_id = (parse_qs(urlparse(request.path).query).get("id") or [""])[0]
    if not project_id:
        send_json(request, 400, {"status": "invalid_request", "error": "id is required"})
        return
    try:
        project = get_project(project_id)
        if project is None:
            send_json(request, 404, {"status": "not_found", "projectId": project_id})
            return
        send_json(request, 200, {"status": "ok", "project": project})
    except RuntimeError as exc:
        send_json(request, 503, {"status": "persistence_not_configured", "error": str(exc)})
    except Exception as exc:
        send_json(request, 500, {"status": "error", "error": str(exc)})


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
        return 503, {"service": "project-factory", "status": "blocked", "reason": "GEMINI_API_KEY is not configured"}
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
        return 502, {"service": "project-factory", "status": "model_error", "error": str(exc)}
    return 200, {
        "service": "project-factory", "status": "ok", "provider": result.provider,
        "model": result.model, "output": result.output,
        "usage": {"inputTokens": result.input_tokens, "outputTokens": result.output_tokens},
        "estimatedCost": result.estimated_cost,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if is_projects_path(self.path):
            get_project_from_request(self)
            return
        query = parse_qs(urlparse(self.path).query)
        prompt = (query.get("prompt") or [""])[0].strip()
        status, payload = build_response(prompt)
        send_json(self, status, payload)

    def do_POST(self):
        if is_projects_path(self.path):
            create_project_from_request(self)
            return
        self.do_GET()

    def log_message(self, format, *args):
        return
