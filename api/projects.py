"""V3 project-record API backed by Golden Reference Firestore."""
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

from project_factory.firestore_store import create_project, get_project
from project_factory.project_record import new_project_record


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            record = new_project_record(
                str(data.get("customerId", "")),
                str(data.get("projectName", "")),
                str(data.get("brief", "")),
                str(data.get("deliveryModel", "")),
            )
            create_project(record)
            self._send(201, {"status": "created", "project": record})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"status": "invalid_request", "error": str(exc)})
        except RuntimeError as exc:
            self._send(503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            self._send(500, {"status": "error", "error": str(exc)})

    def do_GET(self):
        project_id = (parse_qs(urlparse(self.path).query).get("id") or [""])[0]
        if not project_id:
            self._send(400, {"status": "invalid_request", "error": "id is required"})
            return
        try:
            project = get_project(project_id)
            if project is None:
                self._send(404, {"status": "not_found", "projectId": project_id})
                return
            self._send(200, {"status": "ok", "project": project})
        except RuntimeError as exc:
            self._send(503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            self._send(500, {"status": "error", "error": str(exc)})

    def log_message(self, format, *args):
        return
