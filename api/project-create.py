"""Dedicated Firestore project-create endpoint."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from uuid import uuid4


def send_json(request, status, payload):
    body = json.dumps(payload).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Cache-Control", "no-store")
    request.send_header("Content-Length", str(len(body)))
    request.end_headers()
    request.wfile.write(body)


def get_db():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        try:
            app = firebase_admin.get_app("golden-reference-firestore")
        except ValueError:
            raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
            if not raw:
                raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
            info = json.loads(raw)
            app = firebase_admin.initialize_app(
                credentials.Certificate(info),
                {"projectId": info.get("project_id")},
                name="golden-reference-firestore",
            )
        return firestore.client(app=app)
    except Exception as exc:
        raise RuntimeError(f"Firestore initialization failed: {type(exc).__name__}: {exc}") from exc


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            customer = str(data.get("customerId", "")).strip()
            name = str(data.get("projectName", "")).strip()
            brief = str(data.get("brief", "")).strip()
            model = str(data.get("deliveryModel", "")).strip()
            if not customer or not name or not brief:
                raise ValueError("customerId, projectName and brief are required")
            if model not in {"transfer", "deploy", "managed"}:
                raise ValueError("deliveryModel must be transfer, deploy, or managed")
            now = datetime.now(timezone.utc).isoformat()
            record = {
                "customerId": customer,
                "projectId": f"proj_{uuid4().hex}",
                "projectName": name,
                "brief": brief,
                "deliveryModel": model,
                "lifecycleState": "INTAKE",
                "currentVersion": "0.1.0",
                "repository": "",
                "hostingTarget": "",
                "productionUrl": "",
                "createdAt": now,
                "updatedAt": now,
            }
            get_db().collection("projects").document(record["projectId"]).create(record)
            send_json(self, 201, {"status": "created", "project": record})
        except ValueError as exc:
            send_json(self, 400, {"status": "invalid_request", "error": str(exc)})
        except json.JSONDecodeError as exc:
            send_json(self, 400, {"status": "invalid_json", "error": str(exc)})
        except RuntimeError as exc:
            send_json(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            send_json(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})

    def do_GET(self):
        send_json(self, 405, {"status": "method_not_allowed", "error": "POST required"})

    def log_message(self, format, *args):
        return
