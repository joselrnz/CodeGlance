"""Self-contained interactive HTML template — canvas renderer with cards, layer containers,
directional edges, a source-code panel and a project overview. Data + JS are inlined."""

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
  html,body { margin:0; height:100%; overflow:hidden; background:#0b1220; color:#e8edf5;
    font-family: ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  #cv { display:block; position:fixed; inset:0; }
  .card { background:rgba(17,24,38,0.94); border:1px solid #243049; border-radius:12px;
    backdrop-filter: blur(6px); box-shadow:0 10px 34px rgba(0,0,0,0.45); }
  #topbar { position:fixed; top:14px; left:14px; right:14px; display:flex; align-items:center;
    gap:14px; padding:10px 14px; z-index:5; }
  #topbar .title { font-weight:700; font-size:15px; white-space:nowrap; }
  #topbar .sub { color:#93a1b5; font-size:12px; white-space:nowrap; }
  #search { flex:1; min-width:120px; background:#0b1220; border:1px solid #334155; color:#e8edf5;
    padding:7px 11px; border-radius:8px; font-size:13px; outline:none; }
  #search:focus { border-color:#60a5fa; }
  #topbar .hint { color:#64748b; font-size:11px; white-space:nowrap; }
  .leg { position:fixed; left:14px; max-width:230px; overflow:auto; padding:10px 12px; z-index:5; font-size:12px; }
  #types { top:64px; max-height:34vh; } #legend { bottom:14px; max-height:40vh; }
  .leg h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:#93a1b5; }
  .lg { display:flex; align-items:center; gap:8px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  .lg:hover { background:#1e293b; } .lg.off { opacity:.4; }
  .sw { width:11px; height:11px; border-radius:3px; flex:none; }
  .lg .nm { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .lg .ct { color:#64748b; }
  #panel { position:fixed; right:14px; top:64px; width:360px; max-height:calc(100vh - 84px); overflow:auto;
    padding:16px; z-index:6; }
  #panel .close { position:absolute; top:10px; right:12px; cursor:pointer; color:#64748b; font-size:16px; }
  #panel .ptype { display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.05em;
    padding:2px 7px; border-radius:99px; border:1px solid; }
  #panel .cx { font-size:10px; color:#94a3b8; } .cx-simple{color:#5a9e6f} .cx-moderate{color:#fbbf24} .cx-complex{color:#fb7185}
  #panel h3 { margin:8px 0 4px; font-size:16px; word-break:break-word; }
  #panel .path { color:#7dd3fc; font-size:11px; font-family:ui-monospace,monospace; word-break:break-all; }
  #panel .summary { color:#cbd5e1; font-size:13px; line-height:1.5; margin:10px 0; }
  .ov-h { font-size:11px; color:#93a1b5; text-transform:uppercase; letter-spacing:.05em; margin:14px 0 6px; }
  .ov-title { font-size:18px; font-weight:700; } .ov-desc { color:#cbd5e1; font-size:12px; line-height:1.5; margin-top:4px; }
  .ov-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:12px; }
  .stat { background:#0b1220; border:1px solid #243049; border-radius:8px; padding:8px 10px; }
  .stat .v { font-size:20px; font-weight:700; } .stat .k { font-size:11px; color:#93a1b5; }
  .pills { display:flex; flex-wrap:wrap; gap:5px; } .pill { font-size:11px; background:#1e293b; color:#cbd5e1;
    padding:2px 8px; border-radius:99px; }
  .bar { display:flex; align-items:center; gap:7px; font-size:11px; margin:3px 0; }
  .bar .bk{width:9px;height:9px;border-radius:2px;flex:none} .bar .bl{width:74px;color:#cbd5e1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .bar .bb{flex:1;height:7px;background:#0b1220;border-radius:4px;overflow:hidden} .bar .bb>span{display:block;height:100%}
  .bar .bc{color:#64748b;width:28px;text-align:right}
  .nb { font-size:12px; padding:4px 7px; border-radius:6px; cursor:pointer; color:#cbd5e1;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .nb:hover { background:#1e293b; color:#fff; }
  .nb .et { color:#7c8aa3; font-family:ui-monospace,monospace; font-size:10px; } .muted{color:#64748b}
  pre.code { background:#0a0f1a; border:1px solid #243049; border-radius:8px; padding:10px; overflow:auto;
    max-height:320px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:11px; line-height:1.45;
    color:#cdd6e6; white-space:pre; }
  #tip { position:fixed; pointer-events:none; z-index:9; max-width:320px; padding:8px 10px; font-size:12px; display:none; }
  #tip .tn{font-weight:600} #tip .tt{color:#93a1b5;font-size:11px} #tip .ts{color:#cbd5e1;margin-top:3px}
  #mm { position:fixed; right:14px; bottom:14px; width:210px; height:140px; z-index:5; padding:0; cursor:crosshair; }
  #tour { position:fixed; right:240px; bottom:14px; width:340px; padding:14px 16px; z-index:6; }
  #tour h4 { margin:0 0 4px; font-size:14px; } #tour .desc { font-size:13px; color:#cbd5e1; line-height:1.5; margin:6px 0 12px; }
  .tourbtns { display:flex; gap:8px; align-items:center; }
  button { background:#1e293b; color:#e8edf5; border:1px solid #334155; border-radius:8px; padding:6px 12px; font-size:12px; cursor:pointer; }
  button:hover { background:#334155; } #tcount { flex:1; text-align:center; color:#93a1b5; font-size:12px; }
  #tourstart { position:fixed; right:240px; bottom:14px; z-index:5; }
  .hidden { display:none !important; }
</style>
</head>
<body>
<canvas id="cv"></canvas>
<div id="topbar" class="card">
  <span class="title">__PROJECT_NAME__</span>
  <span class="sub">__SUBTITLE__</span>
  <input id="search" placeholder="Search…" autocomplete="off"/>
  <span class="hint">scroll zoom · drag pan · click a card</span>
</div>
<div id="types" class="leg card"></div>
<div id="legend" class="leg card"></div>
<div id="panel" class="card"></div>
<div id="tip" class="card"></div>
<canvas id="mm" class="card"></canvas>
<button id="tourstart">▶ Guided tour</button>
<div id="tour" class="card hidden">
  <h4 id="ttitle"></h4><div class="desc" id="tdesc"></div>
  <div class="tourbtns"><button id="tprev">‹</button><span id="tcount"></span><button id="tnext">›</button><button id="tclose">Done</button></div>
</div>
<script>
const DATA = __DATA_JSON__;
const N=DATA.nodes, E=DATA.edges, L=DATA.layers, TY=DATA.types, TOUR=DATA.tour, CT=DATA.containers;
const cardW=DATA.cardW, cardH=DATA.cardH;
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const nbr=N.map(()=>new Set()), etype={};
for(const e of E){ const a=e[0],b=e[1]; nbr[a].add(b); nbr[b].add(a); etype[a+'_'+b]=e[2]; }
const edgeBetween=(i,j)=>etype[i+'_'+j]||etype[j+'_'+i]||'related';
let DPR=1, scale=1, ox=0, oy=0;
const hidden=new Set(), hiddenTypes=new Set();
let hover=-1, sel=-1, matched=null, focusSet=null, tIdx=-1;
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const SX=x=>x*scale+ox, SY=y=>y*scale+oy;
const vis=i=>!hidden.has(N[i].layer)&&!hiddenTypes.has(N[i].type);
function dim(i){ if(matched&&!matched.has(i))return true; if(focusSet&&!focusSet.has(i))return true;
  if(hover>=0&&i!==hover&&!nbr[hover].has(i))return true; return false; }

function bounds(){ if(CT.length){ let a=1e9,b=1e9,c=-1e9,d=-1e9; for(const k of CT){a=Math.min(a,k.x);b=Math.min(b,k.y);c=Math.max(c,k.x+k.w);d=Math.max(d,k.y+k.h);} return [a,b,c,d]; }
  let a=1e9,b=1e9,c=-1e9,d=-1e9; for(const n of N){a=Math.min(a,n.x);b=Math.min(b,n.y);c=Math.max(c,n.x);d=Math.max(d,n.y);} return [a,b,c,d]; }
function fit(){ const[a,b,c,d]=bounds(); const w=(c-a)||1,h=(d-b)||1,pad=70;
  scale=Math.max(0.06,Math.min(1.4,Math.min((innerWidth-pad*2)/w,(innerHeight-150)/h)));
  ox=innerWidth/2-(a+c)/2*scale; oy=(innerHeight+40)/2-(b+d)/2*scale; }
function resize(){DPR=window.devicePixelRatio||1;cv.width=innerWidth*DPR;cv.height=innerHeight*DPR;
  cv.style.width=innerWidth+'px';cv.style.height=innerHeight+'px';mmInit();draw();}
function rr(x,y,w,h,r){ r=Math.max(0,Math.min(r,w/2,h/2)); ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
  ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath(); }
function clipText(t,maxw){ if(ctx.measureText(t).width<=maxw)return t; let s=t;
  while(s.length>1 && ctx.measureText(s+'…').width>maxw) s=s.slice(0,-1); return s+'…'; }
function bp(fx,fy,cx,cy){ const dx=fx-cx,dy=fy-cy; if(!dx&&!dy)return[cx,cy];
  const sx=dx?(cardW/2)/Math.abs(dx):1e9, sy=dy?(cardH/2)/Math.abs(dy):1e9, s=Math.min(sx,sy); return [cx+dx*s,cy+dy*s]; }

function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle='#0b1220'; ctx.fillRect(0,0,innerWidth,innerHeight);
  // layer containers
  for(const c of CT){ if(hidden.has(c.layer))continue;
    const x=SX(c.x),y=SY(c.y),w=c.w*scale,h=c.h*scale;
    if(x>innerWidth||y>innerHeight||x+w<0||y+h<0)continue;
    rr(x,y,w,h,11); ctx.fillStyle='rgba(255,255,255,0.018)'; ctx.fill();
    ctx.lineWidth=1.2; ctx.strokeStyle=c.color+'66'; ctx.stroke();
    if(scale>0.28){ ctx.fillStyle=c.color; ctx.font='600 13px ui-sans-serif';
      ctx.fillText(c.name+'  ('+c.count+')', x+12, y+21); } }
  // edges
  for(const e of E){ const a=e[0],b=e[1]; if(!vis(a)||!vis(b))continue;
    const lit=(hover===a||hover===b||sel===a||sel===b);
    const A=N[a],B=N[b], p1=bp(B.x,B.y,A.x,A.y), p2=bp(A.x,A.y,B.x,B.y);
    const x1=SX(p1[0]),y1=SY(p1[1]),x2=SX(p2[0]),y2=SY(p2[1]);
    ctx.strokeStyle=lit?'rgba(96,165,250,0.8)':((dim(a)&&dim(b))?'rgba(148,163,184,0.05)':'rgba(148,163,184,0.22)');
    ctx.lineWidth=lit?2:1; ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    if(scale>0.3){ const ang=Math.atan2(y2-y1,x2-x1),s=6;
      ctx.beginPath(); ctx.moveTo(x2,y2); ctx.lineTo(x2-s*Math.cos(ang-0.42),y2-s*Math.sin(ang-0.42));
      ctx.lineTo(x2-s*Math.cos(ang+0.42),y2-s*Math.sin(ang+0.42)); ctx.closePath(); ctx.fillStyle=ctx.strokeStyle; ctx.fill(); } }
  // cards
  for(let i=0;i<N.length;i++){ if(vis(i)) drawCard(i); }
  drawMinimap();
}
function drawCard(i){ const n=N[i]; const w=cardW*scale,h=cardH*scale,x=SX(n.x)-w/2,y=SY(n.y)-h/2;
  if(x>innerWidth||y>innerHeight||x+w<0||y+h<0)return;
  ctx.globalAlpha=dim(i)?0.16:1;
  rr(x,y,w,h,7); ctx.fillStyle='#151b29'; ctx.fill();
  ctx.fillStyle=n.color; ctx.fillRect(x,y+1,Math.max(3,4*scale),h-2);
  if(i===sel){ctx.lineWidth=2;ctx.strokeStyle='#e2e8f0';} else if(i===hover){ctx.lineWidth=1.5;ctx.strokeStyle=n.color;} else {ctx.lineWidth=1;ctx.strokeStyle='rgba(148,163,184,0.16)';}
  rr(x,y,w,h,7); ctx.stroke();
  if(scale>0.3){ const pad=Math.max(8,8*scale);
    ctx.font='700 '+Math.round(7*scale+3)+'px ui-monospace,monospace'; ctx.fillStyle=n.color;
    ctx.fillText(n.type.toUpperCase(), x+pad, y+Math.round(12*scale)+4);
    ctx.font='600 '+Math.round(8*scale+4)+'px ui-sans-serif'; ctx.fillStyle='#e8edf5';
    ctx.fillText(clipText(n.name, w-pad*2), x+pad, y+h-Math.round(9*scale)-2); }
  ctx.globalAlpha=1;
}
function pick(mx,my){ const wx=(mx-ox)/scale, wy=(my-oy)/scale;
  for(let i=N.length-1;i>=0;i--){ if(!vis(i))continue; const n=N[i];
    if(Math.abs(wx-n.x)<=cardW/2 && Math.abs(wy-n.y)<=cardH/2) return i; } return -1; }

const tip=document.getElementById('tip');
function tooltip(i,e){ if(i<0){tip.style.display='none';return;} const n=N[i];
  tip.innerHTML='<div class="tn">'+esc(n.name)+'</div><div class="tt">'+esc(n.type)+(n.path?' · '+esc(n.path):'')+'</div>'+(n.summary?'<div class="ts">'+esc(n.summary)+'</div>':'');
  tip.style.display='block'; tip.style.left=Math.min(e.clientX+14,innerWidth-330)+'px'; tip.style.top=(e.clientY+14)+'px'; }

const panel=document.getElementById('panel');
function stat(k,v){ return '<div class="stat"><div class="v">'+v+'</div><div class="k">'+k+'</div></div>'; }
function overviewHTML(){ const p=DATA.project,s=DATA.stats; let h='<div class="ov-title">'+esc(p.name)+'</div>';
  if(p.description) h+='<div class="ov-desc">'+esc(p.description)+'</div>';
  h+='<div class="ov-grid">'+stat('Nodes',s.nodes)+stat('Edges',s.edges)+stat('Layers',s.layers)+stat('Types',TY.length)+'</div>';
  if(p.languages&&p.languages.length) h+='<div class="ov-h">Languages</div><div class="pills">'+p.languages.map(l=>'<span class="pill">'+esc(l)+'</span>').join('')+'</div>';
  if(p.frameworks&&p.frameworks.length) h+='<div class="ov-h">Frameworks</div><div class="pills">'+p.frameworks.map(l=>'<span class="pill">'+esc(l)+'</span>').join('')+'</div>';
  h+='<div class="ov-h">Node types</div>'; const mx=Math.max.apply(null,TY.map(t=>t.count).concat([1]));
  for(const t of TY) h+='<div class="bar"><span class="bk" style="background:'+t.color+'"></span><span class="bl">'+esc(t.type)+'</span><span class="bb"><span style="width:'+(t.count/mx*100)+'%;background:'+t.color+'"></span></span><span class="bc">'+t.count+'</span></div>';
  h+='<div class="ov-h">Most connected</div>';
  for(const n of DATA.topConnected) h+='<div class="nb" data-i="'+n.i+'">'+esc(n.name)+' <span class="muted">· '+esc(n.type)+' · '+n.deg+'</span></div>';
  return h; }
function infoHTML(i){ const n=N[i]; let h='<span class="close" onclick="select(-1)">✕</span>';
  h+='<span class="ptype" style="color:'+n.color+';border-color:'+n.color+'">'+esc(n.type)+'</span> <span class="cx cx-'+esc(n.complexity)+'">●'+esc(n.complexity)+'</span>';
  h+='<h3>'+esc(n.name)+'</h3>'; if(n.path) h+='<div class="path">'+esc(n.path)+'</div>';
  if(n.summary) h+='<div class="summary">'+esc(n.summary)+'</div>';
  if(n.tags&&n.tags.length) h+='<div class="pills">'+n.tags.map(t=>'<span class="pill">'+esc(t)+'</span>').join('')+'</div>';
  if(n.layer>=0) h+='<div class="ov-h">Layer</div><div class="nb" style="cursor:default">'+esc(L[n.layer].name)+'</div>';
  const conns=[...nbr[i]].sort((a,b)=>N[b].deg-N[a].deg);
  if(conns.length){ h+='<div class="ov-h">Connections ('+conns.length+')</div>';
    for(const j of conns.slice(0,60)) h+='<div class="nb" data-i="'+j+'"><span class="et">'+esc(edgeBetween(i,j))+'</span> '+esc(N[j].name)+'</div>'; }
  const src=DATA.sources[n.path];
  if(src) h+='<div class="ov-h">Source · '+esc(n.path)+'</div><pre class="code">'+esc(src)+'</pre>';
  return h; }
function renderPanel(){ panel.innerHTML = sel>=0 ? infoHTML(sel) : overviewHTML();
  panel.querySelectorAll('.nb[data-i]').forEach(el=>el.onclick=()=>select(+el.dataset.i)); }
function select(i){ sel=i; renderPanel(); if(i>=0) center([i],false); draw(); }
window.select=select;

document.getElementById('search').addEventListener('input',e=>{ const q=e.target.value.trim().toLowerCase();
  if(!q){matched=null;} else { matched=new Set(); for(let i=0;i<N.length;i++){const n=N[i];
    if(n.name.toLowerCase().includes(q)||(n.path||'').toLowerCase().includes(q)||(n.summary||'').toLowerCase().includes(q)||n.type.includes(q)) matched.add(i);} } draw(); });

// legends
(function(){ const el=document.getElementById('types'); let h='<h4>'+TY.length+' node types</h4>';
  for(const t of TY) h+='<div class="lg" data-t="'+esc(t.type)+'"><span class="sw" style="background:'+t.color+'"></span><span class="nm">'+esc(t.type)+'</span><span class="ct">'+t.count+'</span></div>';
  el.innerHTML=h; el.querySelectorAll('.lg').forEach(x=>x.onclick=()=>{const t=x.dataset.t;
    if(hiddenTypes.has(t)){hiddenTypes.delete(t);x.classList.remove('off');}else{hiddenTypes.add(t);x.classList.add('off');}draw();}); })();
(function(){ const el=document.getElementById('legend'); let h='<h4>'+L.length+' layers</h4>';
  L.forEach((l,i)=>{ h+='<div class="lg" data-i="'+i+'"><span class="sw" style="background:'+l.color+'"></span><span class="nm">'+esc(l.name)+'</span><span class="ct">'+l.count+'</span></div>'; });
  el.innerHTML=h; el.querySelectorAll('.lg').forEach(x=>x.onclick=()=>{const i=+x.dataset.i;
    if(hidden.has(i)){hidden.delete(i);x.classList.remove('off');}else{hidden.add(i);x.classList.add('off');}draw();}); })();

// camera
let drag=false,lx,ly,moved=false;
cv.addEventListener('mousedown',e=>{drag=true;moved=false;lx=e.clientX;ly=e.clientY;});
window.addEventListener('mousemove',e=>{ if(drag){ox+=e.clientX-lx;oy+=e.clientY-ly;lx=e.clientX;ly=e.clientY;moved=true;draw();return;}
  const h=pick(e.clientX,e.clientY); if(h!==hover){hover=h;cv.style.cursor=h>=0?'pointer':'grab';draw();} tooltip(h,e); });
window.addEventListener('mouseup',e=>{ if(drag&&!moved){const h=pick(e.clientX,e.clientY); select(h);} drag=false; });
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0016);
  ox=e.clientX-(e.clientX-ox)*f; oy=e.clientY-(e.clientY-oy)*f; scale*=f; draw();},{passive:false});

// minimap
const mm=document.getElementById('mm'), mmx=mm.getContext('2d'); const MM={w:210,h:140,s:1,ox:0,oy:0};
function mmInit(){ const[a,b,c,d]=bounds(); const gw=(c-a)||1,gh=(d-b)||1,p=8;
  mm.width=MM.w*DPR; mm.height=MM.h*DPR; mm.style.width=MM.w+'px'; mm.style.height=MM.h+'px';
  MM.s=Math.min((MM.w-2*p)/gw,(MM.h-2*p)/gh); MM.ox=p-a*MM.s+(MM.w-2*p-gw*MM.s)/2; MM.oy=p-b*MM.s+(MM.h-2*p-gh*MM.s)/2; }
const mmPt=(x,y)=>[x*MM.s+MM.ox,y*MM.s+MM.oy];
function drawMinimap(){ if(!mm.width)return; mmx.setTransform(DPR,0,0,DPR,0,0); mmx.fillStyle='#060b16'; mmx.fillRect(0,0,MM.w,MM.h);
  for(const c of CT){ if(hidden.has(c.layer))continue; const q=mmPt(c.x,c.y); mmx.strokeStyle=c.color+'55'; mmx.lineWidth=0.6; mmx.strokeRect(q[0],q[1],c.w*MM.s,c.h*MM.s); }
  for(let i=0;i<N.length;i++){ if(!vis(i))continue; const n=N[i],q=mmPt(n.x,n.y); mmx.globalAlpha=dim(i)?0.25:0.95; mmx.fillStyle=n.color; mmx.fillRect(q[0]-1,q[1]-0.6,Math.max(2,cardW*MM.s),Math.max(1.4,cardH*MM.s)); }
  mmx.globalAlpha=1; const p0=mmPt((0-ox)/scale,(0-oy)/scale),p1=mmPt((innerWidth-ox)/scale,(innerHeight-oy)/scale);
  mmx.strokeStyle='#e2e8f0'; mmx.lineWidth=1; mmx.strokeRect(p0[0],p0[1],p1[0]-p0[0],p1[1]-p0[1]); }
mm.addEventListener('mousedown',e=>{ const r=mm.getBoundingClientRect(); const wx=((e.clientX-r.left)-MM.ox)/MM.s, wy=((e.clientY-r.top)-MM.oy)/MM.s;
  ox=innerWidth/2-wx*scale; oy=innerHeight/2-wy*scale; draw(); });

// tour
function center(idxs,zoom){ if(!idxs.length)return; let a=1e9,b=1e9,c=-1e9,d=-1e9;
  idxs.forEach(i=>{const n=N[i];a=Math.min(a,n.x);b=Math.min(b,n.y);c=Math.max(c,n.x);d=Math.max(d,n.y);});
  if(zoom) scale=Math.max(0.5,Math.min(1.2,scale)); ox=innerWidth/2-(a+c)/2*scale; oy=innerHeight/2-(b+d)/2*scale; }
function showStep(){ const s=TOUR[tIdx]; focusSet=new Set(s.nodeIds); s.nodeIds.forEach(i=>nbr[i].forEach(j=>focusSet.add(j)));
  document.getElementById('ttitle').textContent=(tIdx+1)+'. '+s.title; document.getElementById('tdesc').textContent=s.description;
  document.getElementById('tcount').textContent=(tIdx+1)+' / '+TOUR.length;
  if(s.nodeIds.length){ sel=s.nodeIds[0]; renderPanel(); } center(s.nodeIds,true); draw(); }
function startTour(){ if(!TOUR.length)return; tIdx=0; document.getElementById('tour').classList.remove('hidden'); document.getElementById('tourstart').classList.add('hidden'); showStep(); }
function endTour(){ tIdx=-1; focusSet=null; document.getElementById('tour').classList.add('hidden'); document.getElementById('tourstart').classList.remove('hidden'); draw(); }
document.getElementById('tourstart').onclick=startTour;
document.getElementById('tprev').onclick=()=>{if(tIdx>0){tIdx--;showStep();}};
document.getElementById('tnext').onclick=()=>{if(tIdx<TOUR.length-1){tIdx++;showStep();}else endTour();};
document.getElementById('tclose').onclick=endTour;
if(!TOUR.length) document.getElementById('tourstart').classList.add('hidden');
window.addEventListener('keydown',e=>{ if(e.key==='Escape'){select(-1);if(tIdx>=0)endTour();}
  if(tIdx>=0&&e.key==='ArrowRight')document.getElementById('tnext').click();
  if(tIdx>=0&&e.key==='ArrowLeft')document.getElementById('tprev').click(); });

window.addEventListener('resize',resize);
renderPanel(); fit(); resize();
</script>
</body>
</html>
"""


def render_interactive_html(view_model: dict) -> str:
    data_json = json.dumps(view_model, ensure_ascii=False).replace("</", "<\\/")
    project = view_model.get("project", {})
    name = project.get("name", "project")
    stats = view_model.get("stats", {})
    subtitle = (f"{stats.get('nodes', 0)} nodes · {stats.get('edges', 0)} edges · "
                f"{len(view_model.get('layers', []))} layers")
    return (
        _HTML
        .replace("__DATA_JSON__", data_json)
        .replace("__PROJECT_NAME__", _h(name))
        .replace("__SUBTITLE__", _h(subtitle))
        .replace("__TITLE__", _h(f"{name} · Knowledge Graph"))
    )


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
