"""Founder/admin session authentication.

The Vercel FACTORY_ADMIN_KEY is used only to establish a short-lived,
HTTP-only session. The secret is never returned to the browser or stored.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler

SESSION_TTL = 60 * 60


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def sign(payload: str) -> str:
    secret = os.environ.get("FOUNDER_SESSION_SECRET", "").encode()
    if not secret:
        raise RuntimeError("FOUNDER_SESSION_SECRET is not configured")
    return b64(hmac.new(secret, payload.encode(), hashlib.sha256).digest())


def verify_admin_key(handler: BaseHTTPRequestHandler) -> None:
    expected = os.environ.get("FACTORY_ADMIN_KEY", "").strip()
    supplied = handler.headers.get("X-Factory-Admin-Key", "").strip()
    if not expected:
        raise RuntimeError("FACTORY_ADMIN_KEY is not configured")
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise PermissionError("founder/admin authentication required")


def issue_session() -> str:
    payload = b64(json.dumps({"role": "founder", "exp": int(time.time()) + SESSION_TTL}, separators=(",", ":")).encode())
    return f"{payload}.{sign(payload)}"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            verify_admin_key(self)
            token = issue_session()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", f"factory_session={token}; Path=/; Max-Age={SESSION_TTL}; HttpOnly; Secure; SameSite=Strict")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "authenticated", "role": "founder", "sessionTtl": SESSION_TTL}).encode())
        except PermissionError as exc:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "unauthorized", "error": str(exc)}).encode())
        except Exception as exc:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "auth_unavailable", "error": str(exc)}).encode())

    def log_message(self, format, *args):
        return
