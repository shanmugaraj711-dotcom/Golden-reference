"""Single Vercel Python entrypoint for Project Factory API."""
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
        raise RuntimeError(f"firebase_admin unavailable: {type(exc).__name__}: {exc}") from exc

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
            raise RuntimeError(f"Firebase initialization failed: {type(exc).__name__}: {exc}") from exc
    return firestore.client(app=app)


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
        "previewUrl": "",
        "repository": "",
        "hostingTarget": "",
        "productionUrl": "",
        "verification": {"qualityGate": "PENDING", "deployment": "PENDING", "healthCheck": "PENDING"},
        "ownership": {"repository": "PENDING", "hosting": "PENDING", "handoff": "PENDING"},
        "maintenance": {"status": "NOT_ENROLLED", "currentVersion": "0.1.0", "recentChanges": []},
        "nextCustomerAction": "Factory intake received",
        "createdAt": now,
        "updatedAt": now,
    }
    firestore_db().collection("projects").document(record["projectId"]).create(record)
    return record


def read_project(db, project_id):
    snap = db.collection("projects").document(project_id).get()
    if not snap.exists:
        return None
    return snap.to_dict()


def read_latest(db, customer_id=""):
    query = db.collection("projects")
    if customer_id:
        query = query.where("customerId", "==", customer_id)
    docs = list(query.order_by("createdAt", direction="DESCENDING").limit(1).stream())
    return docs[0].to_dict() if docs else None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in {"/api", "/"}:
            send_json(self, 200, {"service": "project-factory", "status": "ok", "engine": "project_factory"})
            return
        if path == "/api/projects":
            params = parse_qs(urlparse(self.path).query)
            project_id = (params.get("id") or [""])[0].strip()
            customer_id = (params.get("customerId") or [""])[0].strip()
            try:
                db = firestore_db()
                project = read_project(db, project_id) if project_id else read_latest(db, customer_id)
                if not project:
                    send_json(self, 404, {"status": "not_found", "error": "project not found"})
                    return
                send_json(self, 200, {"status": "ok", "project": project})
            except RuntimeError as exc:
                send_json(self, 503, {"status": "persistence_not_configured", "error": str(exc)})
            except Exception as exc:
                send_json(self, 500, {"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            return
        send_json(self, 404, {"status": "not_found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path in {"/api", "/"}:
            send_json(self, 200, {"service": "project-factory", "status": "ok", "engine": "project_factory"})
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
