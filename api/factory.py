"""Persistent admin control plane for the customer factory.

Commands are stored with the project in Firestore so the workflow is not tied to
an open browser/chat session. Execution workers can claim the latest command and
checkpoint progress independently.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from firebase_admin import credentials, firestore
import firebase_admin

STEPS = tuple(range(1, 11))
ACTIONS = {"start", "revise", "pause", "resume", "approve", "claim", "checkpoint"}


def db():
    try:
        app = firebase_admin.get_app("golden-reference-factory")
    except ValueError:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        info = json.loads(raw)
        app = firebase_admin.initialize_app(
            credentials.Certificate(info),
            {"projectId": info.get("project_id")},
            name="golden-reference-factory",
        )
    return firestore.client(app=app)


def reply(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def require_admin(handler):
    expected = os.environ.get("FACTORY_ADMIN_KEY", "").strip()
    supplied = handler.headers.get("X-Factory-Admin-Key", "").strip()
    if not expected:
        raise PermissionError("FACTORY_ADMIN_KEY is not configured")
    if supplied != expected:
        raise PermissionError("factory admin authorization required")


def project_ref(project_id: str):
    return db().collection("projects").document(project_id)


def validate_range(start: int, end: int):
    if start not in STEPS or end not in STEPS or start > end:
        raise ValueError("startStep/endStep must be a valid range from 1 to 10")


def load(project_id: str):
    snap = project_ref(project_id).get()
    if not snap.exists:
        raise LookupError("project not found")
    return snap.to_dict() or {}


def next_version(current: str) -> str:
    parts = str(current or "0.1.0").split(".")
    try:
        major, minor, patch = (int(parts[i]) for i in range(3))
    except (ValueError, IndexError):
        return "0.2.0"
    return f"{major}.{minor + 1}.0" if patch >= 0 else "0.2.0"


def control_state(project_id: str, project: dict):
    state = dict(project.get("factoryControl") or {})
    state.setdefault("status", "IDLE")
    state.setdefault("currentStage", 1)
    state.setdefault("startStep", 1)
    state.setdefault("endStep", 10)
    state.setdefault("outputTarget", "web")
    state.setdefault("version", str(project.get("currentVersion", "0.1.0")))
    state.setdefault("queue", [])
    state.setdefault("history", [])
    return {"projectId": project_id, **state}


def command(project_id: str, data: dict):
    ref = project_ref(project_id)
    project = load(project_id)
    action = str(data.get("action") or "").lower().strip()
    if action not in ACTIONS:
        raise ValueError(f"unsupported action: {action or 'missing'}")

    state = control_state(project_id, project)
    now = datetime.now(timezone.utc).isoformat()
    queue = list(state.get("queue") or [])
    history = list(state.get("history") or [])

    if action in {"start", "revise"}:
        start = int(data.get("startStep", 1))
        end = int(data.get("endStep", 10))
        validate_range(start, end)
        instruction = str(data.get("instruction") or "").strip()
        if not instruction:
            raise ValueError("instruction is required")
        target = str(data.get("outputTarget") or "web").strip().lower()
        version = next_version(str(project.get("currentVersion", "0.1.0"))) if action == "revise" else str(project.get("currentVersion", "0.1.0"))
        item = {
            "id": f"cmd_{uuid4().hex}",
            "action": action,
            "instruction": instruction,
            "startStep": start,
            "endStep": end,
            "outputTarget": target,
            "version": version,
            "status": "QUEUED",
            "createdAt": now,
        }
        queue.append(item)
        state.update({"status": "QUEUED", "currentStage": start, "startStep": start, "endStep": end, "outputTarget": target, "version": version, "queue": queue[-20:], "lastCommand": item, "updatedAt": now})
        if action == "revise":
            state["revisionOf"] = str(project.get("currentVersion", "0.1.0"))
        ref.update({"factoryControl": state, "updatedAt": now})
        return state

    if action == "pause":
        state.update({"status": "PAUSED", "pauseReason": str(data.get("reason") or "admin pause"), "updatedAt": now})
    elif action == "resume":
        if state.get("status") != "PAUSED":
            raise ValueError("factory is not paused")
        state.update({"status": "RUNNING", "updatedAt": now})
    elif action == "approve":
        state.update({"status": "APPROVED", "approvedAt": now, "updatedAt": now})
    elif action == "claim":
        pending = next((item for item in reversed(queue) if item.get("status") == "QUEUED"), None)
        if not pending:
            raise LookupError("no queued factory command")
        pending["status"] = "RUNNING"
        pending["claimedAt"] = now
        state.update({"status": "RUNNING", "lastCommand": pending, "queue": queue, "updatedAt": now})
    elif action == "checkpoint":
        stage = int(data.get("stage", 1))
        validate_range(stage, stage)
        start = int(state.get("startStep", 1))
        end = int(state.get("endStep", 10))
        if stage < start or stage > end:
            raise ValueError(f"checkpoint stage must be between {start} and {end}")
        evidence = data.get("evidence") if isinstance(data.get("evidence"), dict) else {}
        state.update({"status": "RUNNING", "currentStage": stage, "evidence": evidence, "updatedAt": now})
        if state.get("lastCommand"):
            last = dict(state["lastCommand"])
            if stage == int(last.get("endStep", end)):
                last["status"] = "COMPLETED"
                last["completedAt"] = now
                state["lastCommand"] = last
                state["status"] = "COMPLETED"
                queue = [{**q, "status": "COMPLETED" if q.get("id") == last.get("id") else q.get("status", "QUEUED")} for q in queue]
                state["queue"] = queue

    history.append({"action": action, "at": now, "stage": state.get("currentStage"), "status": state.get("status")})
    state["history"] = history[-50:]
    ref.update({"factoryControl": state, "updatedAt": now})
    return state


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            require_admin(self)
            q = parse_qs(urlparse(self.path).query)
            project_id = (q.get("projectId") or [""])[0].strip()
            if not project_id:
                raise ValueError("projectId is required")
            project = load(project_id)
            reply(self, 200, {"status": "ok", "factory": control_state(project_id, project)})
        except PermissionError as exc:
            reply(self, 401, {"status": "unauthorized", "error": str(exc)})
        except LookupError as exc:
            reply(self, 404, {"status": "not_found", "error": str(exc)})
        except ValueError as exc:
            reply(self, 400, {"status": "invalid_request", "error": str(exc)})
        except Exception as exc:
            reply(self, 503, {"status": "persistence_error", "error": f"{type(exc).__name__}: {exc}"})

    def do_POST(self):
        try:
            require_admin(self)
            size = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(size) or b"{}")
            project_id = str(data.get("projectId") or "").strip()
            if not project_id:
                raise ValueError("projectId is required")
            reply(self, 200, {"status": "updated", "factory": command(project_id, data)})
        except PermissionError as exc:
            reply(self, 401, {"status": "unauthorized", "error": str(exc)})
        except LookupError as exc:
            reply(self, 404, {"status": "not_found", "error": str(exc)})
        except ValueError as exc:
            reply(self, 400, {"status": "invalid_request", "error": str(exc)})
        except Exception as exc:
            reply(self, 503, {"status": "persistence_error", "error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format, *args):
        return
