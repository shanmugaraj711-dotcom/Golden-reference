"""Founder/admin session authentication using the production admin secret."""
from __future__ import annotations
import base64,hashlib,hmac,json,os,time
from http.server import BaseHTTPRequestHandler
SESSION_TTL=60*60
def b64(value): return base64.urlsafe_b64encode(value).decode().rstrip("=")
def signing_secret():
    secret=os.environ.get("FOUNDER_SESSION_SECRET","").strip() or os.environ.get("FACTORY_ADMIN_KEY","").strip()
    if not secret: raise RuntimeError("FACTORY_ADMIN_KEY is not configured")
    return secret.encode()
def sign(payload): return b64(hmac.new(signing_secret(),payload.encode(),hashlib.sha256).digest())
def verify_admin_key(handler):
    expected=os.environ.get("FACTORY_ADMIN_KEY","").strip(); supplied=handler.headers.get("X-Factory-Admin-Key","").strip()
    if not expected: raise RuntimeError("FACTORY_ADMIN_KEY is not configured")
    if not supplied or not hmac.compare_digest(supplied,expected): raise PermissionError("founder/admin authentication required")
def issue_session():
    payload=b64(json.dumps({"role":"founder","exp":int(time.time())+SESSION_TTL},separators=(",",":")).encode()); return f"{payload}.{sign(payload)}"
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            verify_admin_key(self); token=issue_session(); self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Cache-Control","no-store"); self.send_header("Set-Cookie",f"factory_session={token}; Path=/; Max-Age={SESSION_TTL}; HttpOnly; Secure; SameSite=Strict"); self.end_headers(); self.wfile.write(json.dumps({"status":"authenticated","role":"founder","sessionTtl":SESSION_TTL}).encode())
        except PermissionError as exc: self.send_response(401); self.end_headers(); self.wfile.write(json.dumps({"status":"unauthorized","error":str(exc)}).encode())
        except Exception as exc: self.send_response(503); self.end_headers(); self.wfile.write(json.dumps({"status":"auth_unavailable","error":str(exc)}).encode())
    def log_message(self,format,*args): return
