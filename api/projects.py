"""Self-contained Firestore persistence probe for Project Factory."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


def _send(request, status, payload):
    body = json.dumps(payload).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Cache-Control", "no-store")
    request.send_header("Content-Length", str(len(body)))
    request.end_headers()
    request.wfile.write(body)


def _db():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except Exception as exc:
        raise RuntimeError(f"firebase_admin import failed: {type(exc).__name__}: {exc}") from exc

    try:
        app = firebase_admin.get_app("golden-reference-firestore")
    except ValueError:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        try:
            service_account = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"FIREBASE_SERVICE_ACCOUNT_JSON invalid JSON: {exc}") from exc
        try:
            app = firebase_admin.initialize_app(
                credentials.Certificate(service_account),
                {"projectId": service_account.get("project_id")},
                name="golden-reference-firestore",
            )
        except Exception as exc:
            raise RuntimeError(f"Firebase initialization failed: {type(exc).__name__}: {exc}") from exc
    try:
        return firestore.client(app=app)
    except Exception as exc:
        raise RuntimeError(f"Firestore client failed: {type(exc).__name__}: {exc}") from exc


def _record(data):
    customer = str(data.get("customerId", "")).strip()
    name = str(data.get("projectName", "")).strip()
    brief = str(data.get("brief", "")).strip()
    model = str(data.get("deliveryModel", "")).strip()
    if not customer or not name or not brief:
        raise ValueError("customerId, projectName and brief are required")
    if model not in {"transfer", "deploy", "managed"}:
        raise ValueError("deliveryModel must be transfer, deploy, or managed")
    now = datetime.now(timezone.utc).isoformat()
    return {
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
        "verification": {"qualityGate": "PENDING", "deployment": "PENDING", "healthCheck": "PENDING"},
        "ownership": {"owner": customer},
        "maintenance": "Managed" if model == "managed" else "Not enrolled",
        "events": [{"time": now, "state": "INTAKE", "label": "Project created"}],
        "createdAt": now,
        "updatedAt": now,
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            record = _record(data)
            _db().collection("projects").document(record["projectId"]).create(record)
            _send(self, 201, {"status": "created", "project": record})
        except (ValueError, json.JSONDecodeError) as exc:
            _send(self, 400, {"status": "invalid_request", "error": str(exc)})
        except RuntimeError as exc:
            _send(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            _send(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})

    def do_GET(self):
        project_id = (parse_qs(urlparse(self.path).query).get("id") or [""])[0].strip()
        if not project_id:
            _send(self, 400, {"status": "invalid_request", "error": "id is required"})
            return
        try:
            snap = _db().collection("projects").document(project_id).get()
            if not snap.exists:
                _send(self, 404, {"status": "not_found", "projectId": project_id})
                return
            _send(self, 200, {"status": "ok", "project": snap.to_dict()})
        except RuntimeError as exc:
            _send(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
        except Exception as exc:
            _send(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format, *args):
        return
