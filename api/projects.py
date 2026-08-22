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
 p.setdefault("verification",{k:"PENDING" for k in VK}); p.setdefault("ownership",{k:"PENDING" for k in OK}); p.setdefault("maintenance",{"status":"NOT_ENROLLED","currentVersion":p["currentVersion"],"recentChanges":[]}); p.setdefault("nextCustomerAction","Factory intake received"); return p

def update(data):
 pid=str(data.get("projectId","")).strip()
 if not pid: raise ValueError("projectId is required")
 store=db(); ref=store.collection("projects").document(pid); p=read(store,pid)
 if not p: raise LookupError("project not found")
 p=normalise(p); patch={}
 state=str(data.get("lifecycleState",p["lifecycleState"])).upper()
 if state not in STATES: raise ValueError("invalid lifecycleState")
 patch["lifecycleState"]=state
 patch["nextCustomerAction"]={"INTAKE":"Factory intake received","BUILDING":"Factory build in progress","VERIFYING":"Factory verification in progress","READY":"Project is ready for customer delivery","DELIVERED":"Delivery completed"}[state]
 for f in ("repository","hostingTarget","previewUrl","productionUrl","currentVersion"):
  if f in data: patch[f]=str(data[f])
 for group,keys in (("verification",VK),("ownership",OK)):
  if isinstance(data.get(group),dict):
   merged=dict(p.get(group) or {}); merged.update({k:str(data[group][k]).upper() for k in keys if k in data[group]}); patch[group]=merged
 if isinstance(data.get("maintenance"),dict):
  merged=dict(p.get("maintenance") or {}); merged.update(data["maintenance"]); patch["maintenance"]=merged
 if "recentChange" in data:
  m=dict(p.get("maintenance") or {}); changes=list(m.get("recentChanges") or []); changes.append(str(data["recentChange"])); m["recentChanges"]=changes[-20:]; patch["maintenance"]=m
 patch["updatedAt"]=datetime.now(timezone.utc).isoformat(); ref.update(patch); p.update(patch); return normalise(p)

def create(data):
 c=str(data.get("customerId","")).strip(); n=str(data.get("projectName","")).strip(); b=str(data.get("brief","")).strip(); m=str(data.get("deliveryModel","")).strip()
 if not c or not n or not b: raise ValueError("customerId, projectName and brief are required")
 if m not in {"transfer","deploy","managed"}: raise ValueError("invalid deliveryModel")
 now=datetime.now(timezone.utc).isoformat(); p={"customerId":c,"projectId":f"proj_{uuid4().hex}","projectName":n,"brief":b,"deliveryModel":m,"lifecycleState":"INTAKE","currentVersion":"0.1.0","previewUrl":"","repository":"","hostingTarget":"","productionUrl":"","verification":{k:"PENDING" for k in VK},"ownership":{k:"PENDING" for k in OK},"maintenance":{"status":"NOT_ENROLLED","currentVersion":"0.1.0","recentChanges":[]},"nextCustomerAction":"Factory intake received","createdAt":now,"updatedAt":now}; db().collection("projects").document(p["projectId"]).create(p); return p

class handler(BaseHTTPRequestHandler):
 def do_GET(self):
  q=parse_qs(urlparse(self.path).query); pid=(q.get("id") or [""])[0].strip(); cid=(q.get("customerId") or [""])[0].strip()
  try:
   store=db(); p=read(store,pid) if pid else None
   if not p and cid:
    docs=list(store.collection("projects").where("customerId","==",cid).order_by("createdAt",direction="DESCENDING").limit(1).stream()); p=docs[0].to_dict() if docs else None
   if not p: reply(self,404,{"status":"not_found","error":"project not found"}); return
   reply(self,200,{"status":"ok","project":normalise(p),"lifecycleStates":STATES})
  except Exception as e: reply(self,503 if "firebase_admin" in str(e) or "FIREBASE" in str(e) else 500,{"status":"error","error":f"{type(e).__name__}: {e}"})
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(n) or b"{}")
   if data.get("action")=="update": reply(self,200,{"status":"updated","project":update(data)}); return
   reply(self,201,{"status":"created","project":create(data)})
  except LookupError as e: reply(self,404,{"status":"not_found","error":str(e)})
  except ValueError as e: reply(self,400,{"status":"invalid_request","error":str(e)})
  except Exception as e: reply(self,503,{"status":"persistence_error","error":f"{type(e).__name__}: {e}"})
 def log_message(self,format,*args): return
