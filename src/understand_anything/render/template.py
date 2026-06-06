"""Self-contained interactive HTML template (vanilla canvas renderer, inlined data + JS)."""

from __future__ import annotations

import json

_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>__TITLE__</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  html,body { margin:0; height:100%; overflow:hidden; background:#0b1220;
    font-family: ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; color:#e2e8f0; }
  #cv { display:block; position:fixed; inset:0; }
  .card { background:rgba(15,23,42,0.92); border:1px solid #1e293b; border-radius:12px;
    backdrop-filter: blur(6px); box-shadow:0 8px 30px rgba(0,0,0,0.4); }
  #topbar { position:fixed; top:14px; left:14px; right:14px; display:flex; align-items:center;
    gap:14px; padding:10px 14px; z-index:5; }
  #topbar .title { font-weight:700; font-size:15px; white-space:nowrap; }
  #topbar .sub { color:#94a3b8; font-size:12px; white-space:nowrap; }
  #search { flex:1; min-width:120px; background:#0b1220; border:1px solid #334155; color:#e2e8f0;
    padding:7px 11px; border-radius:8px; font-size:13px; outline:none; }
  #search:focus { border-color:#60a5fa; }
  #topbar .hint { color:#64748b; font-size:11px; white-space:nowrap; }
  #legend { position:fixed; left:14px; bottom:14px; max-width:280px; max-height:46vh; overflow:auto;
    padding:10px 12px; z-index:5; font-size:12px; }
  #legend h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:#94a3b8; }
  .lg { display:flex; align-items:center; gap:8px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  .lg:hover { background:#1e293b; }
  .lg.off { opacity:.4; }
  .sw { width:11px; height:11px; border-radius:3px; flex:none; }
  .lg .nm { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .lg .ct { color:#64748b; }
  #panel { position:fixed; right:14px; top:64px; width:330px; max-height:78vh; overflow:auto;
    padding:16px; z-index:6; }
  #panel.hidden,#tour.hidden,#tourstart.hidden { display:none; }
  #panel .ptype { display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.05em;
    padding:2px 7px; border-radius:99px; background:#1e293b; color:#cbd5e1; }
  #panel h3 { margin:8px 0 4px; font-size:15px; word-break:break-word; }
  #panel .path { color:#7dd3fc; font-size:11px; font-family:ui-monospace,monospace; word-break:break-all; }
  #panel .summary { color:#cbd5e1; font-size:13px; line-height:1.5; margin:10px 0; }
  #panel .nbh { font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; margin:12px 0 6px; }
  #panel .nb { font-size:12px; padding:4px 7px; border-radius:6px; cursor:pointer; color:#cbd5e1;
    font-family:ui-monospace,monospace; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #panel .nb:hover { background:#1e293b; color:#fff; }
  #panel .close { position:absolute; top:10px; right:12px; cursor:pointer; color:#64748b; font-size:16px; }
  #types { position:fixed; left:14px; top:64px; max-width:210px; max-height:40vh; overflow:auto;
    padding:10px 12px; z-index:5; font-size:12px; }
  #types h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:#94a3b8; }
  #mm { position:fixed; right:14px; bottom:14px; width:200px; height:140px; z-index:5; padding:0;
    cursor:crosshair; }
  #tour { position:fixed; right:14px; bottom:170px; width:330px; padding:14px 16px; z-index:6; }
  #tour h4 { margin:0 0 4px; font-size:14px; }
  #tour .desc { font-size:13px; color:#cbd5e1; line-height:1.5; margin:6px 0 12px; }
  .tourbtns { display:flex; gap:8px; align-items:center; }
  button { background:#1e293b; color:#e2e8f0; border:1px solid #334155; border-radius:8px;
    padding:6px 12px; font-size:12px; cursor:pointer; }
  button:hover { background:#334155; }
  #tcount { flex:1; text-align:center; color:#94a3b8; font-size:12px; }
  #tourstart { position:fixed; right:14px; bottom:170px; z-index:5; }
  #tip { position:fixed; pointer-events:none; z-index:9; max-width:300px; padding:8px 10px; font-size:12px;
    display:none; }
  #tip .tn { font-weight:600; } #tip .tt { color:#94a3b8; font-size:11px; } #tip .ts { color:#cbd5e1; margin-top:3px; }
</style>
</head>
<body>
<canvas id="cv"></canvas>
<div id="topbar" class="card">
  <span class="title">__PROJECT_NAME__</span>
  <span class="sub">__SUBTITLE__</span>
  <input id="search" placeholder="Search…" autocomplete="off"/>
  <span class="hint">scroll zoom · drag pan · click node</span>
</div>
<div id="legend" class="card"></div>
<div id="types" class="card"></div>
<canvas id="mm" class="card"></canvas>
<div id="panel" class="card hidden"></div>
<div id="tip" class="card"></div>
<button id="tourstart">▶ Guided tour</button>
<div id="tour" class="card hidden">
  <h4 id="ttitle"></h4>
  <div class="desc" id="tdesc"></div>
  <div class="tourbtns">
    <button id="tprev">‹</button><span id="tcount"></span><button id="tnext">›</button>
    <button id="tclose">Done</button>
  </div>
</div>
<script>
const DATA = __DATA_JSON__;
const N=DATA.nodes, E=DATA.edges, L=DATA.layers, TOUR=DATA.tour;
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const nbr=N.map(()=>new Set());
for(const [a,b] of E){ nbr[a].add(b); nbr[b].add(a); }
let DPR=1, scale=1, ox=0, oy=0;
const hidden=new Set();
const hiddenTypes=new Set();
let hover=-1, sel=-1, matched=null, focusSet=null, tIdx=-1;
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const radius=n=>3.5+Math.min(11,Math.sqrt(n.deg)*2.2);

function bounds(){let a=1e9,b=1e9,c=-1e9,d=-1e9;for(const n of N){if(n.x<a)a=n.x;if(n.y<b)b=n.y;if(n.x>c)c=n.x;if(n.y>d)d=n.y;}return[a,b,c,d];}
function fit(){const[a,b,c,d]=bounds();const w=(c-a)||1,h=(d-b)||1,pad=90;
  scale=Math.max(0.05,Math.min(2,Math.min((innerWidth-pad*2)/w,(innerHeight-160)/h)));
  ox=innerWidth/2-(a+c)/2*scale; oy=(innerHeight+50)/2-(b+d)/2*scale;}
function resize(){DPR=window.devicePixelRatio||1;cv.width=innerWidth*DPR;cv.height=innerHeight*DPR;
  cv.style.width=innerWidth+'px';cv.style.height=innerHeight+'px';mmInit();draw();}
const SX=x=>x*scale+ox, SY=y=>y*scale+oy;
const vis=i=>!hidden.has(N[i].layer)&&!hiddenTypes.has(N[i].type);
function dim(i){ if(matched&&!matched.has(i))return true; if(focusSet&&!focusSet.has(i))return true;
  if(hover>=0&&i!==hover&&!nbr[hover].has(i))return true; return false; }

function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle='#0b1220'; ctx.fillRect(0,0,innerWidth,innerHeight);
  ctx.lineWidth=1;
  for(const [a,b] of E){ if(!vis(a)||!vis(b))continue;
    const lit=hover>=0&&(a===hover||b===hover);
    ctx.strokeStyle = lit?'rgba(96,165,250,0.6)':((dim(a)&&dim(b))?'rgba(148,163,184,0.045)':'rgba(148,163,184,0.16)');
    ctx.beginPath(); ctx.moveTo(SX(N[a].x),SY(N[a].y)); ctx.lineTo(SX(N[b].x),SY(N[b].y)); ctx.stroke(); }
  for(let i=0;i<N.length;i++){ if(!vis(i))continue; const n=N[i]; const r=radius(n)*(i===sel?1.6:1);
    ctx.globalAlpha=dim(i)?0.12:1; ctx.fillStyle=n.color;
    ctx.beginPath(); ctx.arc(SX(n.x),SY(n.y),r,0,6.2832); ctx.fill();
    if(i===sel||i===hover){ctx.lineWidth=2;ctx.strokeStyle='#e2e8f0';ctx.stroke();}
    ctx.globalAlpha=1; }
  ctx.fillStyle='#cbd5e1'; ctx.font='11px ui-monospace,monospace';
  for(let i=0;i<N.length;i++){ if(!vis(i)||dim(i))continue; const n=N[i];
    if(i===sel||i===hover||(scale>0.62&&n.deg>=3)||scale>1.15)
      ctx.fillText(n.name, SX(n.x)+radius(n)+3, SY(n.y)+3); }
  drawMinimap();
}
function pick(mx,my){let best=-1,bd=1e9;for(let i=0;i<N.length;i++){if(!vis(i))continue;
  const dx=SX(N[i].x)-mx,dy=SY(N[i].y)-my,d=dx*dx+dy*dy,rr=radius(N[i])+6;
  if(d<rr*rr&&d<bd){bd=d;best=i;}}return best;}

const tip=document.getElementById('tip');
function tooltip(i,e){ if(i<0){tip.style.display='none';return;} const n=N[i];
  tip.innerHTML='<div class="tn">'+esc(n.name)+'</div><div class="tt">'+esc(n.type)+(n.path?' · '+esc(n.path):'')+'</div>'+(n.summary?'<div class="ts">'+esc(n.summary)+'</div>':'');
  tip.style.display='block'; tip.style.left=Math.min(e.clientX+14,innerWidth-310)+'px'; tip.style.top=(e.clientY+14)+'px'; }

const panel=document.getElementById('panel');
function select(i){ sel=i; if(i<0){panel.classList.add('hidden');draw();return;} const n=N[i];
  const neigh=[...nbr[i]].sort((a,b)=>N[b].deg-N[a].deg).slice(0,40);
  let html='<span class="close" onclick="select(-1)">✕</span><span class="ptype">'+esc(n.type)+'</span>'+
    '<h3>'+esc(n.name)+'</h3>'+(n.path?'<div class="path">'+esc(n.path)+'</div>':'')+
    '<div class="summary">'+esc(n.summary||'No summary.')+'</div>'+
    (n.layer>=0?'<div class="nbh">Layer</div><div class="nb" style="cursor:default">●&nbsp;'+esc(L[n.layer].name)+'</div>':'')+
    '<div class="nbh">Connections ('+nbr[i].size+')</div>';
  for(const j of neigh) html+='<div class="nb" data-i="'+j+'">'+esc(N[j].name)+'</div>';
  panel.innerHTML=html; panel.classList.remove('hidden');
  panel.querySelectorAll('.nb[data-i]').forEach(el=>el.onclick=()=>select(+el.dataset.i));
  draw(); }

// search
document.getElementById('search').addEventListener('input',e=>{
  const q=e.target.value.trim().toLowerCase();
  if(!q){matched=null;} else { matched=new Set();
    for(let i=0;i<N.length;i++){const n=N[i];
      if(n.name.toLowerCase().includes(q)||(n.path||'').toLowerCase().includes(q)||(n.summary||'').toLowerCase().includes(q)||n.type.includes(q)) matched.add(i);} }
  draw();
});

// legend
const legend=document.getElementById('legend');
(function(){ let h='<h4>'+L.length+' layers · '+N.length+' nodes</h4>';
  L.forEach((l,i)=>{ h+='<div class="lg" data-i="'+i+'"><span class="sw" style="background:'+l.color+'"></span><span class="nm">'+esc(l.name)+'</span><span class="ct">'+l.count+'</span></div>'; });
  legend.innerHTML=h;
  legend.querySelectorAll('.lg').forEach(el=>el.onclick=()=>{const i=+el.dataset.i;
    if(hidden.has(i)){hidden.delete(i);el.classList.remove('off');}else{hidden.add(i);el.classList.add('off');}draw();});
})();

// node-type filters
const typesEl=document.getElementById('types');
(function(){ const counts={}; for(const n of N) counts[n.type]=(counts[n.type]||0)+1;
  const order=Object.keys(counts).sort((a,b)=>counts[b]-counts[a]);
  let h='<h4>'+order.length+' node types</h4>';
  for(const t of order) h+='<div class="lg" data-t="'+t+'"><span class="sw" style="background:#64748b"></span><span class="nm">'+esc(t)+'</span><span class="ct">'+counts[t]+'</span></div>';
  typesEl.innerHTML=h;
  typesEl.querySelectorAll('.lg').forEach(el=>el.onclick=()=>{const t=el.dataset.t;
    if(hiddenTypes.has(t)){hiddenTypes.delete(t);el.classList.remove('off');}else{hiddenTypes.add(t);el.classList.add('off');}draw();});
})();

// minimap (overview + viewport box, click to recenter)
const mm=document.getElementById('mm'), mmx=mm.getContext('2d');
const MM={w:200,h:140,s:1,ox:0,oy:0};
function mmInit(){ const [a,b,c,d]=bounds(); const gw=(c-a)||1, gh=(d-b)||1, p=8;
  mm.width=MM.w*DPR; mm.height=MM.h*DPR; mm.style.width=MM.w+'px'; mm.style.height=MM.h+'px';
  MM.s=Math.min((MM.w-2*p)/gw,(MM.h-2*p)/gh);
  MM.ox=p-a*MM.s+(MM.w-2*p-gw*MM.s)/2; MM.oy=p-b*MM.s+(MM.h-2*p-gh*MM.s)/2; }
const mmPt=(x,y)=>[x*MM.s+MM.ox, y*MM.s+MM.oy];
function drawMinimap(){ if(!mm.width)return; mmx.setTransform(DPR,0,0,DPR,0,0);
  mmx.fillStyle='#060b16'; mmx.fillRect(0,0,MM.w,MM.h);
  for(let i=0;i<N.length;i++){ if(!vis(i))continue; const n=N[i]; const q=mmPt(n.x,n.y);
    mmx.globalAlpha=dim(i)?0.2:0.9; mmx.fillStyle=n.color; mmx.fillRect(q[0]-1,q[1]-1,2.2,2.2); }
  mmx.globalAlpha=1;
  const p0=mmPt((0-ox)/scale,(0-oy)/scale), p1=mmPt((innerWidth-ox)/scale,(innerHeight-oy)/scale);
  mmx.strokeStyle='#e2e8f0'; mmx.lineWidth=1; mmx.strokeRect(p0[0],p0[1],p1[0]-p0[0],p1[1]-p0[1]); }
mm.addEventListener('mousedown',e=>{ const r=mm.getBoundingClientRect();
  const wx=((e.clientX-r.left)-MM.ox)/MM.s, wy=((e.clientY-r.top)-MM.oy)/MM.s;
  ox=innerWidth/2-wx*scale; oy=innerHeight/2-wy*scale; draw(); });

// camera interactions
let drag=false,lx,ly,moved=false;
cv.addEventListener('mousedown',e=>{drag=true;moved=false;lx=e.clientX;ly=e.clientY;});
window.addEventListener('mousemove',e=>{
  if(drag){ox+=e.clientX-lx;oy+=e.clientY-ly;lx=e.clientX;ly=e.clientY;moved=true;draw();return;}
  const h=pick(e.clientX,e.clientY); if(h!==hover){hover=h;cv.style.cursor=h>=0?'pointer':'grab';draw();}
  tooltip(h,e); });
window.addEventListener('mouseup',e=>{ if(drag&&!moved){const h=pick(e.clientX,e.clientY); if(h>=0)select(h); else select(-1);} drag=false; });
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0016);
  ox=e.clientX-(e.clientX-ox)*f; oy=e.clientY-(e.clientY-oy)*f; scale*=f; draw();},{passive:false});

// tour
function centerOn(idxs){ if(!idxs.length)return; let a=1e9,b=1e9,c=-1e9,d=-1e9;
  idxs.forEach(i=>{const n=N[i];a=Math.min(a,n.x);b=Math.min(b,n.y);c=Math.max(c,n.x);d=Math.max(d,n.y);});
  scale=Math.max(0.4,Math.min(1.4,scale)); ox=innerWidth/2-(a+c)/2*scale; oy=innerHeight/2-(b+d)/2*scale; }
function showStep(){ const s=TOUR[tIdx]; focusSet=new Set(s.nodeIds); s.nodeIds.forEach(i=>nbr[i].forEach(j=>focusSet.add(j)));
  document.getElementById('ttitle').textContent=(tIdx+1)+'. '+s.title;
  document.getElementById('tdesc').textContent=s.description;
  document.getElementById('tcount').textContent=(tIdx+1)+' / '+TOUR.length;
  if(s.nodeIds.length){sel=s.nodeIds[0];select(sel);} centerOn(s.nodeIds); draw(); }
function startTour(){ if(!TOUR.length)return; tIdx=0; document.getElementById('tour').classList.remove('hidden');
  document.getElementById('tourstart').classList.add('hidden'); showStep(); }
function endTour(){ tIdx=-1; focusSet=null; document.getElementById('tour').classList.add('hidden');
  document.getElementById('tourstart').classList.remove('hidden'); draw(); }
document.getElementById('tourstart').onclick=startTour;
document.getElementById('tprev').onclick=()=>{if(tIdx>0){tIdx--;showStep();}};
document.getElementById('tnext').onclick=()=>{if(tIdx<TOUR.length-1){tIdx++;showStep();}else endTour();};
document.getElementById('tclose').onclick=endTour;
if(!TOUR.length) document.getElementById('tourstart').classList.add('hidden');
window.addEventListener('keydown',e=>{ if(e.key==='Escape'){select(-1);if(tIdx>=0)endTour();}
  if(tIdx>=0&&e.key==='ArrowRight')document.getElementById('tnext').click();
  if(tIdx>=0&&e.key==='ArrowLeft')document.getElementById('tprev').click(); });

window.select=select;
window.addEventListener('resize',resize);
fit(); resize();
</script>
</body>
</html>
"""


def render_interactive_html(view_model: dict) -> str:
    data_json = json.dumps(view_model, ensure_ascii=False).replace("</", "<\\/")
    project = view_model.get("project", {})
    name = project.get("name", "project")
    stats = view_model.get("stats", {})
    subtitle = f"{stats.get('nodes', 0)} nodes · {stats.get('edges', 0)} edges · {len(view_model.get('layers', []))} layers"
    return (
        _HTML
        .replace("__DATA_JSON__", data_json)
        .replace("__PROJECT_NAME__", _h(name))
        .replace("__SUBTITLE__", _h(subtitle))
        .replace("__TITLE__", _h(f"{name} · Knowledge Graph"))
    )


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
