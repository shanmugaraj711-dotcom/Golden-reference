from __future__ import annotations

import json
import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

_APP_NAME = "golden-reference-firestore"


def _client():
    try:
        app = firebase_admin.get_app(_APP_NAME)
    except ValueError:
        raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        try:
            service_account = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is invalid JSON") from exc
        app = firebase_admin.initialize_app(
            credentials.Certificate(service_account),
            {"projectId": service_account.get("project_id")},
            name=_APP_NAME,
        )
    return firestore.client(app=app)


def create_project(record: dict[str, Any]) -> dict[str, Any]:
    project_id = str(record["projectId"])
    _client().collection("projects").document(project_id).create(record)
    return record


def get_project(project_id: str) -> dict[str, Any] | None:
    snapshot = _client().collection("projects").document(project_id).get()
    if not snapshot.exists:
        return None
    return snapshot.to_dict()


def update_project(project_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    ref = _client().collection("projects").document(project_id)
    ref.update(fields)
    snapshot = ref.get()
    return snapshot.to_dict()
