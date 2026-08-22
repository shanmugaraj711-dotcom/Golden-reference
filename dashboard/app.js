const help={
  transfer:'Validated project package plus ownership handoff.',
  deploy:'Live deployment plus customer handoff.',
  managed:'Live deployment with ongoing maintenance and version tracking.'
};

const esc=(value)=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const params=new URLSearchParams(location.search);
const projectId=params.get('projectId')||params.get('id');
const customerId=params.get('customerId');
const endpoint=projectId?`/api/projects?id=${encodeURIComponent(projectId)}`:customerId?`/api/projects?customerId=${encodeURIComponent(customerId)}`:'/api/projects';

const setText=(id,value)=>{const el=document.getElementById(id);if(el)el.textContent=value??'—'};
const setLink=(id,url)=>{const el=document.getElementById(id);if(!el)return;if(url){el.href=url;el.hidden=false}else el.hidden=true};

function stateLabel(state){return String(state||'').replaceAll('_',' ')}
function timeline(state){
  const states=['INTAKE','PLANNING','GENERATING','REVIEW','APPROVED','DELIVERING','VERIFYING','LIVE','HANDED_OFF','MANAGED'];
  const current=states.indexOf(state);
  document.getElementById('timeline').innerHTML=states.map((s,i)=>`<div class="${i<current?'done':i===current?'current':''}">${esc(stateLabel(s))}</div>`).join('');
}
function progress(state){
  const states=['INTAKE','PLANNING','GENERATING','REVIEW','APPROVED','DELIVERING','VERIFYING','LIVE','HANDED_OFF','MANAGED'];
  const i=Math.max(0,states.indexOf(state));
  const pct=Math.round(((i+1)/states.length)*100);
  document.getElementById('progressBar').style.width=`${pct}%`;
  setText('progressText',`${i+1} / ${states.length} lifecycle stages reached`);
}

async function loadProject(){
  try{
    const response=await fetch(endpoint,{cache:'no-store'});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
    const p=data.project||{};
    const v=p.verification||{};
    const o=p.ownership||{};
    const m=p.maintenance||{};
    setText('status','LIVE');
    document.getElementById('status').className='pill live';
    setText('projectName',p.projectName||'Unnamed project');
    setText('projectMeta',`Version ${p.currentVersion||'—'} · ${stateLabel(p.deliveryModel||'—')}`);
    setText('deliveryModel',stateLabel(p.deliveryModel||'—'));
    setText('modeHelp',help[p.deliveryModel]||'Factory delivery state.');
    setText('nextAction',p.nextCustomerAction||'No customer action recorded.');
    setText('qualityGate',v.qualityGate||'PENDING');
    setText('deployment',v.deployment||'PENDING');
    setText('healthCheck',v.healthCheck||'PENDING');
    setText('deliveryTitle',p.productionUrl?'Production delivery available':'Delivery evidence in progress');
    setText('deliveryEvidence',`Repository: ${p.repository||'PENDING'} · Hosting: ${p.hostingTarget||'PENDING'} · Production: ${p.productionUrl||'PENDING'}`);
    setText('repoOwnership',o.repository||'PENDING');
    setText('hostingOwnership',o.hosting||'PENDING');
    setText('handoffOwnership',o.handoff||'PENDING');
    setText('maintenanceStatus',m.status||'NOT_ENROLLED');
    setText('maintenanceVersion',`Current version: ${m.currentVersion||p.currentVersion||'—'}`);
    setText('recentChanges',m.recentChanges?.length?`Recent changes: ${m.recentChanges.join(', ')}`:'No recent changes recorded.');
    setText('projectId',p.projectId||'—');
    setText('brief',p.brief||'—');
    setLink('preview',p.previewUrl);
    setLink('production',p.productionUrl);
    progress(p.lifecycleState);
    timeline(p.lifecycleState);
  }catch(error){
    setText('status','ERROR');
    document.getElementById('status').className='pill';
    setText('projectName','Project unavailable');
    setText('projectMeta',error.message);
    setText('progressText','Unable to load Factory state');
  }
}
loadProject();
setInterval(loadProject,30000);
