"""Firestore-backed Project Factory API."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def _send(request: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Cache-Control", "no-store")
    request.send_header("Content-Length", str(len(body)))
    request.end_headers()
    request.wfile.write(body)


def _imports():
    # Lazy imports keep Vercel function startup failures visible as JSON instead
    # of FUNCTION_INVOCATION_FAILED when an optional dependency/config is wrong.
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from project_factory.firestore_store import create_project, get_project
    from project_factory.project_record import new_project_record
    return create_project, get_project, new_project_record


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            create_project, _, new_project_record = _imports()
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            record = new_project_record(
                str(data.get("customerId", "")),
                str(data.get("projectName", "")),
                str(data.get("brief", "")),
                str(data.get("deliveryModel", "")),
            )
            create_project(record)
            _send(self, 201, {"status": "created", "project": record})
        except (ValueError, json.JSONDecodeError) as exc:
            _send(self, 400, {"status": "invalid_request", "error": str(exc)})
        except RuntimeError as exc:
            _send(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            _send(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})

    def do_GET(self):
        project_id = (parse_qs(urlparse(self.path).query).get("id") or [""])[0]
        if not project_id:
            _send(self, 400, {"status": "invalid_request", "error": "id is required"})
            return
        try:
            _, get_project, _ = _imports()
            project = get_project(project_id)
            if project is None:
                _send(self, 404, {"status": "not_found", "projectId": project_id})
                return
            _send(self, 200, {"status": "ok", "project": project})
        except RuntimeError as exc:
            _send(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            _send(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format, *args):
        return
