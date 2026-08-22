"""Single Vercel Python entrypoint for Project Factory API.

Vercel's api/index.py is the stable catch-all entrypoint. Keep routing here
instead of relying on legacy vercel.json routes, which can shadow sibling
Python functions.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


def send_json(request, status, payload):
    body = json.dumps(payload).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Cache-Control", "no-store")
    request.send_header("Content-Length", str(len(body)))
    request.end_headers()
    request.wfile.write(body)


def firestore_db():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except Exception as exc:
        raise RuntimeError(
            f"firebase_admin unavailable: {type(exc).__name__}: {exc}"
        ) from exc

    try:
        app = firebase_admin.get_app("golden-reference-firestore")
    except ValueError:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        try:
            info = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"FIREBASE_SERVICE_ACCOUNT_JSON invalid JSON: {exc}") from exc
        try:
            app = firebase_admin.initialize_app(
                credentials.Certificate(info),
                {"projectId": info.get("project_id")},
                name="golden-reference-firestore",
            )
        except Exception as exc:
            raise RuntimeError(
                f"Firebase initialization failed: {type(exc).__name__}: {exc}"
            ) from exc

    try:
        return firestore.client(app=app)
    except Exception as exc:
        raise RuntimeError(
            f"Firestore client failed: {type(exc).__name__}: {exc}"
        ) from exc


def create_project(data):
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
        "verification": {
            "qualityGate": "PENDING",
            "deployment": "PENDING",
            "healthCheck": "PENDING",
        },
        "createdAt": now,
        "updatedAt": now,
    }
    firestore_db().collection("projects").document(record["projectId"]).create(record)
    return record


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in {"/api", "/"}:
            send_json(self, 200, {
                "service": "project-factory",
                "status": "ok",
                "engine": "project_factory",
            })
            return

        if path == "/api/projects":
            project_id = (parse_qs(urlparse(self.path).query).get("id") or [""])[0].strip()
            if not project_id:
                send_json(self, 400, {"status": "invalid_request", "error": "id is required"})
                return
            try:
                snap = firestore_db().collection("projects").document(project_id).get()
                if not snap.exists:
                    send_json(self, 404, {"status": "not_found", "projectId": project_id})
                    return
                send_json(self, 200, {"status": "ok", "project": snap.to_dict()})
            except RuntimeError as exc:
                send_json(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
            except Exception as exc:
                send_json(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            return

        send_json(self, 404, {"status": "not_found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in {"/api", "/"}:
            send_json(self, 200, {
                "service": "project-factory",
                "status": "ok",
                "engine": "project_factory",
            })
            return

        if path == "/api/projects":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length) or b"{}")
                record = create_project(data)
                send_json(self, 201, {"status": "created", "project": record})
            except (ValueError, json.JSONDecodeError) as exc:
                send_json(self, 400, {"status": "invalid_request", "error": str(exc)})
            except RuntimeError as exc:
                send_json(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
            except Exception as exc:
                send_json(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            return

        send_json(self, 404, {"status": "not_found", "path": path})

    def log_message(self, format, *args):
        return
