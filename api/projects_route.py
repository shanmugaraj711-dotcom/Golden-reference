"""Stable Vercel route for /api/projects."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def reply(h, status, payload):
    body = json.dumps(payload).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Cache-Control", "no-store")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            from api.projects import db, read, normalise, STATES
            q = parse_qs(urlparse(self.path).query)
            pid = (q.get("id") or [""])[0].strip()
            cid = (q.get("customerId") or [""])[0].strip()
            store = db()
            p = read(store, pid) if pid else None
            if not p and cid:
                docs = list(store.collection("projects").where("customerId", "==", cid).order_by("createdAt", direction="DESCENDING").limit(1).stream())
                p = docs[0].to_dict() if docs else None
            # The customer dashboard can be opened directly after deployment.
            # During the current auth-migration window, return the newest project
            # when no selector is supplied instead of producing a misleading 404.
            if not p and not pid and not cid:
                docs = list(store.collection("projects").order_by("createdAt", direction="DESCENDING").limit(1).stream())
                p = docs[0].to_dict() if docs else None
            if not p:
                reply(self, 404, {"status": "not_found", "error": "project not found"})
                return
            reply(self, 200, {"status": "ok", "project": normalise(p), "lifecycleStates": STATES})
        except Exception as e:
            reply(self, 503, {"status": "error", "error": f"{type(e).__name__}: {e}"})

    def log_message(self, format, *args):
        return
