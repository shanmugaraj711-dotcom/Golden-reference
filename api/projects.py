"""Project Factory lifecycle API backed by Cloud Firestore."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

STATES = ["INTAKE", "BUILDING", "VERIFYING", "READY", "DELIVERED"]
VERIFICATION_KEYS = ("qualityGate", "deployment", "healthCheck")
OWNERSHIP_KEYS = ("repository", "hosting", "handoff")


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
    h.end_headers(); h.wfile.write(body)


def read_project(store, project_id):
    snap = store.collection("projects").document(project_id).get()
    return snap.to_dict() if snap.exists else None


def latest_project(store, customer_id=""):
    q = store.collection("projects")
    if customer_id: q = q.where("customerId", "==", customer_id)
    docs = list(q.order_by("createdAt", direction="DESCENDING").limit(1).stream())
    return docs[0].to_dict() if docs else None


def normalise(project):
    project.setdefault("lifecycleState", "INTAKE")
    project.setdefault("currentVersion", "0.1.0")
    project.setdefault("previewUrl", "")
    project.setdefault("repository", "")
    project.setdefault("hostingTarget", "")
    project.setdefault("productionUrl", "")
    project.setdefault("verification", {k: "PENDING" for k in VERIFICATION_KEYS})
    project.setdefault("ownership", {k: "PENDING" for k in OWNERSHIP_KEYS})
    project.setdefault("maintenance", {"status": "NOT_ENROLLED", "currentVersion": project["currentVersion"], "recentChanges": []})
    project.setdefault("nextCustomerAction", "Factory intake received")
    return project


def create(data):
    customer = str(data.get("customerId", "")).strip(); name = str(data.get("projectName", "")).strip(); brief = str(data.get("brief", "")).strip(); model = str(data.get("deliveryModel", "")).strip()
    if not customer or not name or not brief: raise ValueError("customerId, projectName and brief are required")
    if model not in {"transfer", "deploy", "managed"}: raise ValueError("deliveryModel must be transfer, deploy, or managed")
    now = datetime.now(timezone.utc).isoformat()
    project = {"customerId": customer, "projectId": f"proj_{uuid4().hex}", "projectName": name, "brief": brief, "deliveryModel": model, "lifecycleState": "INTAKE", "currentVersion": "0.1.0", "previewUrl": "", "repository": "", "hostingTarget": "", "productionUrl": "", "verification": {k: "PENDING" for k in VERIFICATION_KEYS}, "ownership": {k: "PENDING" for k in OWNERSHIP_KEYS}, "maintenance": {"status": "NOT_ENROLLED", "currentVersion": "0.1.0", "recentChanges": []}, "nextCustomerAction": "Factory intake received", "createdAt": now, "updatedAt": now}
    db().collection("projects").document(project["projectId"]).create(project)
    return project


def update_project(data):
    project_id = str(data.get("projectId", "")).strip()
    if not project_id: raise ValueError("projectId is required")
    store = db(); ref = store.collection("projects").document(project_id); existing = read_project(store, project_id)
    if not existing: raise LookupError("project not found")
    existing = normalise(existing)
    patch = {}
    if "lifecycleState" in data:
        state = str(data["lifecycleState"]).upper()
        if state not in STATES: raise ValueError("lifecycleState must be INTAKE, BUILDING, VERIFYING, READY, or DELIVERED")
        patch["lifecycleState"] = state
        patch["nextCustomerAction"] = {"INTAKE":"Factory intake received","BUILDING":"Factory build in progress","VERIFYING":"Factory verification in progress","READY":"Project is ready for customer delivery","DELIVERED":"Delivery completed"}[state]
    for field in ("repository", "hostingTarget", "previewUrl", "productionUrl", "currentVersion"):
        if field in data: patch[field] = str(data[field])
    for group, keys in (("verification", VERIFICATION_KEYS), ("ownership", OWNERSHIP_KEYS)):
        if group in data:
            values = data[group]
            if not isinstance(values, dict): raise ValueError(f"{group} must be an object")
            merged = dict(existing.get(group) or {})
            for key in keys:
                if key in values: merged[key] = str(values[key]).upper()
            patch[group] = merged
    if "maintenance" in data:
        if not isinstance(data["maintenance"], dict): raise ValueError("maintenance must be an object")
        merged = dict(existing.get("maintenance") or {})
        merged.update(data["maintenance"]); patch["maintenance"] = merged
    if "recentChange" in data:
        maintenance = dict(existing.get("maintenance") or {})
        changes = list(maintenance.get("recentChanges") or []); changes.append(str(data["recentChange"])); maintenance["recentChanges"] = changes[-20:]; patch["maintenance"] = maintenance
    patch["updatedAt"] = datetime.now(timezone.utc).isoformat()
    ref.update(patch)
    updated = dict(existing); updated.update(patch)
    return normalise(updated)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query); project_id = (params.get("id") or [""])[0].strip(); customer_id = (params.get("customerId") or [""])[0].strip()
        try:
            store = db(); project = read_project(store, project_id) if project_id else latest_project(store, customer_id)
            if not project: reply(self, 404, {"status":"not_found","error":"project not found"}); return
            reply(self, 200, {"status":"ok","project":normalise(project),"lifecycleStates":STATES})
        except Exception as exc:
            reply(self, 503 if "firebase_admin" in str(exc) or "FIREBASE" in str(exc) else 500, {"status":"error","error":f"{type(exc).__name__}: {exc}"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0")); data = json.loads(self.rfile.read(length) or b"{}")
            if data.get("action") == "update":
                reply(self, 200, {"status":"updated","project":update_project(data)}); return
            project = create(data); reply(self, 201, {"status":"created","project":project})
        except LookupError as exc: reply(self, 404, {"status":"not_found","error":str(exc)})
        except ValueError as exc: reply(self, 400, {"status":"invalid_request","error":str(exc)})
        except Exception as exc: reply(self, 503, {"status":"persistence_error","error":f"{type(exc).__name__}: {exc}"})

    def log_message(self, format, *args): return
