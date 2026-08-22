"""Project Factory lifecycle API backed by Cloud Firestore."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

STATES=["INTAKE","BUILDING","VERIFYING","READY","DELIVERED"]
VK=("qualityGate","deployment","healthCheck")
OK=("repository","hosting","handoff")

def db():
 import firebase_admin
 from firebase_admin import credentials,firestore
 try: app=firebase_admin.get_app("golden-reference-firestore")
 except ValueError:
  raw=os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON","").strip()
  if not raw: raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
  info=json.loads(raw); app=firebase_admin.initialize_app(credentials.Certificate(info),{"projectId":info.get("project_id")},name="golden-reference-firestore")
 return firestore.client(app=app)

def reply(h,status,payload):
 body=json.dumps(payload).encode(); h.send_response(status); h.send_header("Content-Type","application/json; charset=utf-8"); h.send_header("Cache-Control","no-store"); h.send_header("Content-Length",str(len(body))); h.end_headers(); h.wfile.write(body)

def read(store,pid):
 s=store.collection("projects").document(pid).get(); return s.to_dict() if s.exists else None

def normalise(p):
 p.setdefault("lifecycleState","INTAKE"); p.setdefault("currentVersion","0.1.0"); p.setdefault("previewUrl",""); p.setdefault("repository",""); p.setdefault("hostingTarget",""); p.setdefault("productionUrl","")
 p.setdefault("verification",{k:"PENDING" for k in VK}); p.setdefault("ownership",{k:"PENDING" for k in OK}); p.setdefault("maintenance",{"status":"NOT_ENROLLED","currentVersion":p["currentVersion"],"recentChanges":[]}); p.setdefault("nextCustomerAction","Factory intake received"); p.setdefault("lifecycleHistory",[]); p.setdefault("deliveryEvidence",{}); p.setdefault("approvals",[]); p.setdefault("changeRequests",[]); return p

def identity(h):
 """Verify Firebase ID token when production auth is enabled.

  During migration, auth is opt-in with FIREBASE_AUTH_REQUIRED=true so existing
  internal smoke tests continue to work until the customer frontend sends tokens.
 """
 required=os.environ.get("FIREBASE_AUTH_REQUIRED","false").lower()=="true"
 raw=h.headers.get("Authorization","")
 if not raw.startswith("Bearer "):
  if required: raise PermissionError("authentication required")
  return {"uid":"internal","customerId":"*","internal":True}
 import firebase_admin
 from firebase_admin import auth
 token=auth.verify_id_token(raw[7:].strip())
 return {"uid":token.get("uid"),"customerId":token.get("customerId") or token.get("customer_id") or token.get("uid"),"internal":False}

def authorize(user,p):
 if user.get("internal"): return
 if str(user.get("customerId")) != str(p.get("customerId")): raise PermissionError("project access denied")

def update(data,user):
 pid=str(data.get("projectId","")).strip()
 if not pid: raise ValueError("projectId is required")
 store=db(); ref=store.collection("projects").document(pid); p=read(store,pid)
 if not p: raise LookupError("project not found")
 p=normalise(p); authorize(user,p); patch={}; old=str(p["lifecycleState"]).upper(); state=str(data.get("lifecycleState",old)).upper()
 if state not in STATES: raise ValueError("invalid lifecycleState")
 if STATES.index(state)<STATES.index(old): raise ValueError("lifecycleState cannot move backwards")
 if state=="READY" and not all(str(p["verification"].get(k,"PENDING")).upper()=="PASSED" for k in VK): raise ValueError("READY requires qualityGate, deployment and healthCheck to be PASSED")
 if state=="DELIVERED":
  if old!="READY": raise ValueError("DELIVERED requires READY")
  if not all(str(p["ownership"].get(k,"PENDING")).upper() in ("READY","CONNECTED","PASSED") for k in OK): raise ValueError("DELIVERED requires repository, hosting and handoff evidence")
 patch["lifecycleState"]=state
 patch["nextCustomerAction"]={"INTAKE":"Factory intake received","BUILDING":"Factory build in progress","VERIFYING":"Factory verification in progress","READY":"Project is ready for customer delivery","DELIVERED":"Delivery completed"}[state]
 for f in ("repository","hostingTarget","previewUrl","productionUrl","currentVersion"):
  if f in data: patch[f]=str(data[f])
 for group,keys in (("verification",VK),("ownership",OK)):
  if isinstance(data.get(group),dict):
   merged=dict(p.get(group) or {}); merged.update({k:str(data[group][k]).upper() for k in keys if k in data[group]}); patch[group]=merged
 if isinstance(data.get("maintenance"),dict):
  merged=dict(p.get("maintenance") or {}); merged.update(data["maintenance"]); patch["maintenance"]=merged
 evidence=dict(p.get("deliveryEvidence") or {})
 if isinstance(data.get("deliveryEvidence"),dict): evidence.update(data["deliveryEvidence"]); patch["deliveryEvidence"]=evidence
 if "recentChange" in data:
  m=dict(p.get("maintenance") or {}); changes=list(m.get("recentChanges") or []); changes.append(str(data["recentChange"])); m["recentChanges"]=changes[-20:]; patch["maintenance"]=m
 now=datetime.now(timezone.utc).isoformat(); history=list(p.get("lifecycleHistory") or [])
 if state!=old: history.append({"from":old,"to":state,"at":now}); patch["lifecycleHistory"]=history[-50:]
 patch["updatedAt"]=now; ref.update(patch); p.update(patch); return normalise(p)

def approval(data,user):
 pid=str(data.get("projectId","")).strip(); decision=str(data.get("decision","")).upper()
 if not pid: raise ValueError("projectId is required")
 if decision not in {"APPROVED","REJECTED"}: raise ValueError("decision must be APPROVED or REJECTED")
 store=db(); ref=store.collection("projects").document(pid); p=read(store,pid)
 if not p: raise LookupError("project not found")
 p=normalise(p); authorize(user,p)
 now=datetime.now(timezone.utc).isoformat(); item={"id":f"apr_{uuid4().hex}","decision":decision,"version":str(data.get("version") or p["currentVersion"]),"comment":str(data.get("comment") or ""),"customerId":p["customerId"],"userId":user.get("uid"),"createdAt":now}; arr=list(p.get("approvals") or []); arr.append(item); patch={"approvals":arr[-50:],"updatedAt":now}
 if decision=="APPROVED" and p["lifecycleState"]=="READY": patch["nextCustomerAction"]="Delivery approved; Factory can complete handoff"
 if decision=="REJECTED": patch["nextCustomerAction"]="Customer requested changes before delivery"
 ref.update(patch); p.update(patch); return item,normalise(p)

def change_request(data,user):
 pid=str(data.get("projectId","")).strip(); text=str(data.get("request","")).strip()
 if not pid or not text: raise ValueError("projectId and request are required")
 store=db(); ref=store.collection("projects").document(pid); p=read(store,pid)
 if not p: raise LookupError("project not found")
 p=normalise(p); authorize(user,p)
 now=datetime.now(timezone.utc).isoformat(); item={"id":f"cr_{uuid4().hex}","request":text,"status":"OPEN","version":str(data.get("version") or p["currentVersion"]),"customerId":p["customerId"],"userId":user.get("uid"),"createdAt":now}; arr=list(p.get("changeRequests") or []); arr.append(item); patch={"changeRequests":arr[-50:],"nextCustomerAction":"Factory review required change request","updatedAt":now}; ref.update(patch); p.update(patch); return item,normalise(p)

def create(data):
 c=str(data.get("customerId","")).strip(); n=str(data.get("projectName","")).strip(); b=str(data.get("brief","")).strip(); m=str(data.get("deliveryModel","")).strip()
 if not c or not n or not b: raise ValueError("customerId, projectName and brief are required")
 if m not in {"transfer","deploy","managed"}: raise ValueError("invalid deliveryModel")
 now=datetime.now(timezone.utc).isoformat(); p={"customerId":c,"projectId":f"proj_{uuid4().hex}","projectName":n,"brief":b,"deliveryModel":m,"lifecycleState":"INTAKE","currentVersion":"0.1.0","previewUrl":"","repository":"","hostingTarget":"","productionUrl":"","verification":{k:"PENDING" for k in VK},"ownership":{k:"PENDING" for k in OK},"maintenance":{"status":"NOT_ENROLLED","currentVersion":"0.1.0","recentChanges":[]},"nextCustomerAction":"Factory intake received","lifecycleHistory":[],"deliveryEvidence":{},"approvals":[],"changeRequests":[],"createdAt":now,"updatedAt":now}; db().collection("projects").document(p["projectId"]).create(p); return p

class handler(BaseHTTPRequestHandler):
 def do_GET(self):
  try:
   user=identity(self); q=parse_qs(urlparse(self.path).query); pid=(q.get("id") or [""])[0].strip(); cid=(q.get("customerId") or [""])[0].strip(); store=db(); p=read(store,pid) if pid else None
   if not p and cid:
    if not user.get("internal") and str(user.get("customerId"))!=cid: raise PermissionError("project access denied")
    docs=list(store.collection("projects").where("customerId","==",cid).order_by("createdAt",direction="DESCENDING").limit(1).stream()); p=docs[0].to_dict() if docs else None
   if not p: reply(self,404,{"status":"not_found","error":"project not found"}); return
   authorize(user,p); reply(self,200,{"status":"ok","project":normalise(p),"lifecycleStates":STATES})
  except PermissionError as e: reply(self,401,{"status":"unauthorized","error":str(e)})
  except Exception as e: reply(self,503 if "firebase_admin" in str(e) or "FIREBASE" in str(e) else 500,{"status":"error","error":f"{type(e).__name__}: {e}"})
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(n) or b"{}"); user=identity(self); action=str(data.get("action") or "").lower()
   if action=="update": reply(self,200,{"status":"updated","project":update(data,user)}); return
   if action in {"approve","approval"}:
    item,p=approval(data,user); reply(self,200,{"status":"recorded","approval":item,"project":p}); return
   if action in {"change_request","request_change","change-request"}:
    item,p=change_request(data,user); reply(self,201,{"status":"created","changeRequest":item,"project":p}); return
   if not user.get("internal") and str(user.get("customerId"))!=str(data.get("customerId")): raise PermissionError("customer ownership mismatch")
   reply(self,201,{"status":"created","project":create(data)})
  except PermissionError as e: reply(self,401,{"status":"unauthorized","error":str(e)})
  except LookupError as e: reply(self,404,{"status":"not_found","error":str(e)})
  except ValueError as e: reply(self,400,{"status":"invalid_request","error":str(e)})
  except Exception as e: reply(self,503,{"status":"persistence_error","error":f"{type(e).__name__}: {e}"})
 def log_message(self,format,*args): return
