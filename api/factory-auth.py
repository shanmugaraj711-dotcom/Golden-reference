"""Session-oriented founder authentication boundary.

This endpoint deliberately does not store passwords or secrets in source. It
expects the identity provider to assert a verified founder identity through
OIDC headers supplied by the hosting/auth layer, then issues a short-lived,
HTTP-only session cookie backed by a signed token secret.
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


def verified_identity(handler: BaseHTTPRequestHandler) -> str:
    """Accept only an identity asserted by the configured auth gateway."""
    subject = handler.headers.get("X-Verified-User", "").strip()
    role = handler.headers.get("X-Verified-Role", "").strip().lower()
    founder = os.environ.get("FOUNDER_IDENTITY", "").strip()
    if not subject or not founder or not hmac.compare_digest(subject, founder):
        raise PermissionError("founder authentication required")
    if role not in {"founder", "admin"}:
        raise PermissionError("founder/admin role required")
    return subject


def issue_session(subject: str) -> str:
    payload = b64(json.dumps({"sub": subject, "role": "founder", "exp": int(time.time()) + SESSION_TTL}, separators=(",", ":")).encode())
    return f"{payload}.{sign(payload)}"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            subject = verified_identity(self)
            token = issue_session(subject)
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
