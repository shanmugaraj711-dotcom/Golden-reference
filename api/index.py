"""Single Vercel Python entrypoint for Project Factory API and customer dashboard."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def send_json(request, status, payload):
    body=json.dumps(payload).encode("utf-8")
    request.send_response(status); request.send_header("Content-Type","application/json; charset=utf-8"); request.send_header("Cache-Control","no-store"); request.send_header("Content-Length",str(len(body))); request.end_headers(); request.wfile.write(body)

def send_html(request, html):
    body=html.encode("utf-8"); request.send_response(200); request.send_header("Content-Type","text/html; charset=utf-8"); request.send_header("Cache-Control","no-store"); request.send_header("Content-Length",str(len(body))); request.end_headers(); request.wfile.write(body)

def firestore_db():
    from project_factory_firestore import firestore_db as get_db
    return get_db()

def dashboard_html(project_id=""):
    safe_id=json.dumps(project_id)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Project Factory — Customer Delivery</title><style>:root{{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f5f7fb}}*{{box-sizing:border-box}}body{{margin:0}}.shell{{max-width:1100px;margin:auto;padding:36px 20px 60px}}.top{{display:flex;justify-content:space-between;align-items:flex-start}}.eyebrow,.label{{font-size:12px;letter-spacing:.12em;font-weight:800;color:#667085}}h1{{margin:4px 0 6px;font-size:34px}}h2{{font-size:28px;margin:8px 0}}h3{{margin:5px 0 8px}}p{{color:#667085;line-height:1.5}}.pill{{padding:8px 12px;border-radius:999px;background:#e8f7ee;color:#177245;font-size:12px;font-weight:800}}.hero,.card{{background:white;border:1px solid #e6e9ef;border-radius:18px;box-shadow:0 5px 20px #1720330a}}.hero{{padding:28px;margin:24px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0}}.card{{padding:22px}}.progress{{height:10px;background:#edf0f5;border-radius:99px;margin:15px 0 10px;overflow:hidden}}.progress span{{display:block;height:100%;width:10%;background:#2463eb;border-radius:99px}}ul{{padding-left:20px;line-height:2}}b{{float:right}}code{{word-break:break-all}}.delivery{{margin:16px 0}}.steps{{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px}}.step{{padding:9px 12px;border-radius:10px;background:#f0f2f6;font-size:13px}}.done{{background:#e8f7ee;color:#177245}}footer{{text-align:center;color:#98a2b3;font-size:12px;margin-top:30px}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><main class="shell"><header class="top"><div><div class="eyebrow">PROJECT FACTORY</div><h1>Customer Delivery</h1><p>Live project state and delivery evidence.</p></div><span id="status" class="pill">CONNECTING</span></header><section class="hero"><div class="label">PROJECT</div><h2 id="name">Loading project…</h2><p id="meta">Reading Firestore</p></section><section class="grid"><article class="card"><div class="label">PROGRESS</div><div class="progress"><span id="bar"></span></div><strong id="progress">Loading…</strong><p id="next">—</p></article><article class="card"><div class="label">DELIVERY MODEL</div><h3 id="model">—</h3><p id="mode">—</p></article><article class="card"><div class="label">VERIFICATION</div><ul><li>Quality gate <b id="quality">—</b></li><li>Deployment <b id="deployment">—</b></li><li>Health check <b id="health">—</b></li></ul></article></section><section class="card delivery"><div class="label">DELIVERY EVIDENCE</div><h3 id="delivery">Loading…</h3><p id="evidence">—</p></section><section class="grid"><article class="card"><div class="label">OWNERSHIP</div><ul><li>Repository <b id="repo">—</b></li><li>Hosting <b id="hosting">—</b></li><li>Handoff <b id="handoff">—</b></li></ul></article><article class="card"><div class="label">MAINTENANCE</div><h3 id="maint">—</h3><p id="version">—</p><p id="changes">—</p></article><article class="card"><div class="label">PROJECT ID</div><code id="pid">—</code><p id="brief">—</p></article></section><section class="card"><div class="label">PROJECT TIMELINE</div><div id="timeline" class="steps"></div></section><footer>Credentials and provider secrets are never displayed in the customer dashboard.</footer></main><script>
const projectId={safe_id}; const set=(id,v)=>document.getElementById(id).textContent=String(v??"—");
async function load(){{try{{const q=projectId?"?id="+encodeURIComponent(projectId):"";const r=await fetch("/api/projects"+q,{{cache:"no-store"}});const d=await r.json();if(!r.ok)throw Error(d.error||"Project unavailable");const p=d.project||{{}},v=p.verification||{{}},o=p.ownership||{{}},m=p.maintenance||{{}};const states=["INTAKE","BUILDING","VERIFYING","READY","DELIVERED"],i=Math.max(0,states.indexOf(p.lifecycleState||"INTAKE"));set("status","LIVE");set("name",p.projectName);set("meta",(p.currentVersion||"")+" • "+(p.deliveryModel||""));set("progress",(p.lifecycleState||"INTAKE")+" • "+(i+1)+"/5");document.getElementById("bar").style.width=((i+1)*20)+"%";set("next",p.nextCustomerAction||"Factory intake received");set("model",p.deliveryModel);set("mode",p.productionUrl||p.previewUrl||"Delivery evidence pending");set("quality",v.qualityGate);set("deployment",v.deployment);set("health",v.healthCheck);set("delivery",p.productionUrl||p.previewUrl||"Delivery not yet published");set("evidence",p.repository?"Repository: "+p.repository:"Factory evidence will appear here as delivery advances.");set("repo",o.repository);set("hosting",o.hosting);set("handoff",o.handoff);set("maint",m.status);set("version",m.currentVersion);set("changes",Array.isArray(m.recentChanges)?m.recentChanges.join(" • "):"");set("pid",p.projectId);set("brief",p.brief);document.getElementById("timeline").innerHTML=states.map((s,n)=>`<span class="step ${{n<=i?"done":""}}">${{s}}</span>`).join("")}}catch(e){{set("status","ERROR");set("name","Unable to load project");set("meta",e.message)}}}}load();setInterval(load,30000);
</script></body></html>'''

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path.rstrip("/") or "/"
        if path=="/": send_html(self,dashboard_html((parse_qs(parsed.query).get("projectId") or [""])[0].strip())); return
        if path=="/api": send_json(self,200,{"service":"project-factory","status":"ok","engine":"project_factory"}); return
        if path=="/api/projects":
            try:
                from api.projects import db,read,normalise
                q=parse_qs(parsed.query); pid=(q.get("id") or [""])[0].strip(); cid=(q.get("customerId") or [""])[0].strip(); store=db(); p=read(store,pid) if pid else None
                if not p and cid:
                    docs=list(store.collection("projects").where("customerId","==",cid).order_by("createdAt",direction="DESCENDING").limit(1).stream()); p=docs[0].to_dict() if docs else None
                if not p: send_json(self,404,{"status":"not_found","error":"project not found"}); return
                send_json(self,200,{"status":"ok","project":normalise(p),"lifecycleStates":["INTAKE","BUILDING","VERIFYING","READY","DELIVERED"]})
            except Exception as e: send_json(self,503 if "firebase" in str(e).lower() else 500,{"status":"error","error":f"{type(e).__name__}: {e}"})
            return
        send_json(self,404,{"status":"not_found","path":path})
    def do_POST(self):
        path=urlparse(self.path).path.rstrip("/") or "/"
        if path=="/api": send_json(self,200,{"service":"project-factory","status":"ok","engine":"project_factory"}); return
        if path=="/api/projects":
            try:
                length=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(length) or b"{}")
                from api.projects import create,update
                if data.get("action")=="update": send_json(self,200,{"status":"updated","project":update(data)}); return
                send_json(self,201,{"status":"created","project":create(data)})
            except ValueError as e: send_json(self,400,{"status":"invalid_request","error":str(e)})
            except LookupError as e: send_json(self,404,{"status":"not_found","error":str(e)})
            except Exception as e: send_json(self,503,{"status":"persistence_error","error":f"{type(e).__name__}: {e}"})
            return
        send_json(self,404,{"status":"not_found","path":path})
    def log_message(self,format,*args): return
