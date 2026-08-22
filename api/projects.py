"""Vercel Firestore project API."""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


def db():
    import firebase_admin
    from firebase_admin import credentials, firestore
    try:
        app = firebase_admin.get_app("golden-reference-firestore")
    except ValueError:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        info = json.loads(raw)
        app = firebase_admin.initialize_app(credentials.Certificate(info), {"projectId": info.get("project_id")}, name="golden-reference-firestore")
    return firestore.client(app=app)


def reply(h, status, payload):
    body = json.dumps(payload).encode()
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Cache-Control", "no-store")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


def get_project(project_id, customer_id):
    store = db()
    if project_id:
        snap = store.collection("projects").document(project_id).get()
        return snap.to_dict() if snap.exists else None
    q = store.collection("projects")
    if customer_id:
        q = q.where("customerId", "==", customer_id)
    docs = list(q.order_by("createdAt", direction="DESCENDING").limit(1).stream())
    return docs[0].to_dict() if docs else None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        project_id = (params.get("id") or [""])[0].strip()
        customer_id = (params.get("customerId") or [""])[0].strip()
        try:
            project = get_project(project_id, customer_id)
            if not project:
                reply(self, 404, {"status": "not_found", "error": "project not found"})
                return
            reply(self, 200, {"status": "ok", "project": project})
        except Exception as exc:
            reply(self, 503 if "firebase_admin" in str(exc) or "FIREBASE" in str(exc) else 500, {"status": "persistence_not_configured", "error": f"{type(exc).__name__}: {exc}"})

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
            project = {"customerId": customer, "projectId": f"proj_{uuid4().hex}", "projectName": name, "brief": brief, "deliveryModel": model, "lifecycleState": "INTAKE", "currentVersion": "0.1.0", "previewUrl": "", "repository": "", "hostingTarget": "", "productionUrl": "", "verification": {"qualityGate": "PENDING", "deployment": "PENDING", "healthCheck": "PENDING"}, "ownership": {"repository": "PENDING", "hosting": "PENDING", "handoff": "PENDING"}, "maintenance": {"status": "NOT_ENROLLED", "currentVersion": "0.1.0", "recentChanges": []}, "nextCustomerAction": "Factory intake received", "createdAt": now, "updatedAt": now}
            db().collection("projects").document(project["projectId"]).create(project)
            reply(self, 201, {"status": "created", "project": project})
        except ValueError as exc:
            reply(self, 400, {"status": "invalid_request", "error": str(exc)})
        except Exception as exc:
            reply(self, 503, {"status": "persistence_not_configured", "error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format, *args):
        return
