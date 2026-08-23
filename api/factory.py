"""Persistent admin control plane for the customer factory."""
from __future__ import annotations
import base64,hashlib,hmac,json,os,time
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs,urlparse
from uuid import uuid4
from firebase_admin import credentials,firestore
import firebase_admin
STEPS=tuple(range(1,11)); ACTIONS={"start","revise","pause","resume","approve","claim","checkpoint"}
def db():
    try: app=firebase_admin.get_app("golden-reference-factory")
    except ValueError:
        raw=os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON","").strip()
        if not raw: raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        info=json.loads(raw); app=firebase_admin.initialize_app(credentials.Certificate(info),{"projectId":info.get("project_id")},name="golden-reference-factory")
    return firestore.client(app=app)
def reply(handler,status,payload):
    body=json.dumps(payload).encode(); handler.send_response(status); handler.send_header("Content-Type","application/json; charset=utf-8"); handler.send_header("Cache-Control","no-store"); handler.send_header("Content-Length",str(len(body))); handler.end_headers(); handler.wfile.write(body)
def b64decode(v): return base64.urlsafe_b64decode(v+"="*(-len(v)%4))
def signing_secret(): return (os.environ.get("FOUNDER_SESSION_SECRET","").strip() or os.environ.get("FACTORY_ADMIN_KEY","").strip()).encode()
def session_valid(handler):
    secret=signing_secret()
    if not secret:return False
    raw=handler.headers.get("Cookie",""); token=next((x.split("=",1)[1] for x in raw.split(";") if x.strip().startswith("factory_session=")),"")
    if "." not in token:return False
    payload,sig=token.rsplit(".",1); expected=base64.urlsafe_b64encode(hmac.new(secret,payload.encode(),hashlib.sha256).digest()).decode().rstrip("=")
    if not hmac.compare_digest(sig,expected):return False
    try:
        d=json.loads(b64decode(payload)); return d.get("role")=="founder" and int(d.get("exp",0))>int(time.time())
    except Exception:return False
def require_admin(handler):
    if session_valid(handler):return
    expected=os.environ.get("FACTORY_ADMIN_KEY","").strip(); supplied=handler.headers.get("X-Factory-Admin-Key","").strip()
    if not expected:raise PermissionError("FACTORY_ADMIN_KEY is not configured")
    if not supplied or not hmac.compare_digest(supplied,expected):raise PermissionError("factory admin authorization required")
def project_ref(pid):return db().collection("projects").document(pid)
def validate_range(start,end):
    if start not in STEPS or end not in STEPS or start>end:raise ValueError("startStep/endStep must be a valid range from 1 to 10")
def load(pid):
    s=project_ref(pid).get()
    if not s.exists:raise LookupError("project not found")
    return s.to_dict() or {}
def next_version(cur):
    p=str(cur or "0.1.0").split(".")
    try:major,minor,patch=(int(p[i]) for i in range(3))
    except (ValueError,IndexError):return "0.2.0"
    return f"{major}.{minor+1}.0" if patch>=0 else "0.2.0"
def control_state(pid,project):
    s=dict(project.get("factoryControl") or {}); s.setdefault("status","IDLE"); s.setdefault("currentStage",1); s.setdefault("startStep",1); s.setdefault("endStep",10); s.setdefault("outputTarget","web"); s.setdefault("version",str(project.get("currentVersion","0.1.0"))); s.setdefault("queue",[]); s.setdefault("history",[]); return {"projectId":pid,**s}
def command(pid,data):
    ref=project_ref(pid); project=load(pid); action=str(data.get("action") or "").lower().strip()
    if action not in ACTIONS:raise ValueError(f"unsupported action: {action or 'missing'}")
    state=control_state(pid,project); now=datetime.now(timezone.utc).isoformat(); queue=list(state.get("queue") or []); history=list(state.get("history") or [])
    if action in {"start","revise"}:
        start=int(data.get("startStep",1)); end=int(data.get("endStep",10)); validate_range(start,end); instruction=str(data.get("instruction") or "").strip()
        if not instruction:raise ValueError("instruction is required")
        target=str(data.get("outputTarget") or "web").strip().lower(); version=next_version(str(project.get("currentVersion","0.1.0"))) if action=="revise" else str(project.get("currentVersion","0.1.0")); item={"id":f"cmd_{uuid4().hex}","action":action,"instruction":instruction,"startStep":start,"endStep":end,"outputTarget":target,"version":version,"status":"QUEUED","createdAt":now}; queue.append(item); state.update({"status":"QUEUED","currentStage":start,"startStep":start,"endStep":end,"outputTarget":target,"version":version,"queue":queue[-20:],"lastCommand":item,"updatedAt":now}); ref.update({"factoryControl":state,"updatedAt":now}); return state
    if action=="pause":state.update({"status":"PAUSED","pauseReason":str(data.get("reason") or "admin pause"),"updatedAt":now})
    elif action=="resume":
        if state.get("status")!="PAUSED":raise ValueError("factory is not paused")
        state.update({"status":"RUNNING","updatedAt":now})
    elif action=="approve":state.update({"status":"APPROVED","approvedAt":now,"updatedAt":now})
    elif action=="claim":
        pending=next((x for x in reversed(queue) if x.get("status")=="QUEUED"),None)
        if not pending:raise LookupError("no queued factory command")
        pending["status"]="RUNNING"; pending["claimedAt"]=now; state.update({"status":"RUNNING","lastCommand":pending,"queue":queue,"updatedAt":now})
    elif action=="checkpoint":
        stage=int(data.get("stage",1)); validate_range(stage,stage); start=int(state.get("startStep",1)); end=int(state.get("endStep",10))
        if stage<start or stage>end:raise ValueError(f"checkpoint stage must be between {start} and {end}")
        state.update({"status":"RUNNING","currentStage":stage,"evidence":data.get("evidence") if isinstance(data.get("evidence"),dict) else {},"updatedAt":now})
    history.append({"action":action,"at":now,"stage":state.get("currentStage"),"status":state.get("status")}); state["history"]=history[-50:]; ref.update({"factoryControl":state,"updatedAt":now}); return state
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            require_admin(self);q=parse_qs(urlparse(self.path).query);pid=(q.get("projectId") or [""])[0].strip()
            if not pid:raise ValueError("projectId is required")
            reply(self,200,{"status":"ok","factory":control_state(pid,load(pid))})
        except PermissionError as e:reply(self,401,{"status":"unauthorized","error":str(e)})
        except LookupError as e:reply(self,404,{"status":"not_found","error":str(e)})
        except ValueError as e:reply(self,400,{"status":"invalid_request","error":str(e)})
        except Exception as e:reply(self,503,{"status":"persistence_error","error":f"{type(e).__name__}: {e}"})
    def do_POST(self):
        try:
            require_admin(self);n=int(self.headers.get("Content-Length","0"));data=json.loads(self.rfile.read(n) or b"{}");pid=str(data.get("projectId") or "").strip()
            if not pid:raise ValueError("projectId is required")
            reply(self,200,{"status":"updated","factory":command(pid,data)})
        except PermissionError as e:reply(self,401,{"status":"unauthorized","error":str(e)})
        except LookupError as e:reply(self,404,{"status":"not_found","error":str(e)})
        except ValueError as e:reply(self,400,{"status":"invalid_request","error":str(e)})
        except Exception as e:reply(self,503,{"status":"persistence_error","error":f"{type(e).__name__}: {e}"})
    def log_message(self,format,*args):return
