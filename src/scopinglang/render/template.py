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
  :root { color-scheme: dark; --bg:#0a0e14; --surface:#1b2530; --elevated:#1b2530; --card:#1a222c; --code-bg:#0b0f15; --text:#e8edf2; --text2:#87939f; --muted:#536b7a; --accent:#5ba4cf; --accent-rgb:91,164,207; --tint:rgba(255,255,255,0.02); --font-heading:Georgia,"Times New Roman",serif; }
  * { box-sizing: border-box; }
  html,body { margin:0; height:100%; overflow:hidden; background:var(--bg); color:var(--text);
    font-family: ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  #cv { display:block; position:fixed; inset:0; }
  .card { background:rgba(20,20,20,0.94); border:1px solid rgba(var(--accent-rgb),0.14); border-radius:12px;
    backdrop-filter: blur(6px); box-shadow:0 10px 34px rgba(0,0,0,0.45); }
  #topbar { position:fixed; top:14px; left:14px; right:14px; display:flex; align-items:center;
    gap:14px; padding:10px 14px; z-index:5; }
  #topbar .title { font-weight:700; font-size:15px; white-space:nowrap; }
  #topbar .sub { color:var(--text2); font-size:12px; white-space:nowrap; }
  #search { flex:1; min-width:120px; background:var(--bg); border:1px solid rgba(var(--accent-rgb),0.28); color:var(--text);
    padding:7px 11px; border-radius:8px; font-size:13px; outline:none; }
  #search:focus { border-color:var(--accent); }
  #topbar .hint { color:var(--muted); font-size:11px; white-space:nowrap; }
  .leg { position:fixed; left:14px; max-width:230px; overflow:auto; padding:10px 12px; z-index:5; font-size:12px; }
  #types { top:104px; max-height:34vh; } #legend { bottom:14px; max-height:40vh; }
  #crumb { position:fixed; top:62px; left:14px; z-index:6; padding:6px 13px; font-size:11px; font-weight:600;
    text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }
  #crumb button { background:transparent; border:none; color:var(--accent); padding:0; font:inherit; cursor:pointer; text-transform:uppercase; }
  .leg h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }
  .lg { display:flex; align-items:center; gap:8px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  .lg:hover { background:var(--elevated); } .lg.off { opacity:.4; }
  .sw { width:11px; height:11px; border-radius:3px; flex:none; }
  .lg .nm { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .lg .ct { color:var(--muted); }
  #panel { position:fixed; right:14px; top:64px; width:360px; max-height:calc(100vh - 84px); overflow:auto;
    padding:16px; z-index:6; }
  #panel .close { position:absolute; top:10px; right:12px; cursor:pointer; color:var(--muted); font-size:16px; }
  #panel .ptype { display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.05em;
    padding:2px 7px; border-radius:99px; border:1px solid; }
  #panel .cx { font-size:10px; color:#94a3b8; } .cx-simple{color:#5a9e6f} .cx-moderate{color:#fbbf24} .cx-complex{color:#fb7185}
  #panel h3 { margin:8px 0 4px; font-size:16px; word-break:break-word; }
  #panel .path { color:#7dd3fc; font-size:11px; font-family:ui-monospace,monospace; word-break:break-all; }
  #panel .summary { color:var(--text); font-size:13px; line-height:1.5; margin:10px 0; }
  .ov-h { font-size:11px; color:var(--text2); text-transform:uppercase; letter-spacing:.05em; margin:14px 0 6px; }
  .ov-title { font-size:18px; font-weight:700; } .ov-desc { color:var(--text); font-size:12px; line-height:1.5; margin-top:4px; }
  .ov-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:12px; }
  .stat { background:var(--bg); border:1px solid rgba(var(--accent-rgb),0.14); border-radius:8px; padding:8px 10px; }
  .stat .v { font-size:20px; font-weight:700; } .stat .k { font-size:11px; color:var(--text2); }
  .pills { display:flex; flex-wrap:wrap; gap:5px; } .pill { font-size:11px; background:var(--elevated); color:var(--text);
    padding:2px 8px; border-radius:99px; }
  .bar { display:flex; align-items:center; gap:7px; font-size:11px; margin:3px 0; }
  .bar .bk{width:9px;height:9px;border-radius:2px;flex:none} .bar .bl{width:74px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .bar .bb{flex:1;height:7px;background:var(--bg);border-radius:4px;overflow:hidden} .bar .bb>span{display:block;height:100%}
  .bar .bc{color:var(--muted);width:28px;text-align:right}
  .nb { font-size:12px; padding:4px 7px; border-radius:6px; cursor:pointer; color:var(--text);
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .nb:hover { background:var(--elevated); color:#fff; }
  .nb .et { color:#7c8aa3; font-family:ui-monospace,monospace; font-size:10px; } .muted{color:var(--muted)}
  .path .lr { color:var(--accent); font-size:10px; }
  pre.sig { background:var(--code-bg); border:1px solid rgba(var(--accent-rgb),0.14); border-left:2px solid #5a9e6f; border-radius:6px;
    padding:7px 9px; margin:8px 0; overflow:auto; font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
    font-size:11px; color:#bfe3c8; white-space:pre; }
  .doc { color:var(--text); font-size:12px; line-height:1.5; white-space:pre-wrap; background:rgba(var(--accent-rgb),0.06);
    border:1px solid rgba(var(--accent-rgb),0.18); border-radius:6px; padding:8px 10px; }
  .code { background:var(--code-bg); border:1px solid rgba(var(--accent-rgb),0.14); border-radius:8px; overflow:auto; max-height:340px;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:11px; line-height:1.5; }
  .code table.ct { border-collapse:collapse; width:100%; }
  .code td.ln { user-select:none; text-align:right; color:#5c5145; padding:0 9px; width:1%; white-space:nowrap;
    border-right:1px solid rgba(var(--accent-rgb),0.14); }
  .code td.lc { padding:0 10px; white-space:pre; color:var(--text); }
  .code tr.hl { background:rgba(var(--accent-rgb),0.14); } .code tr.hl td.ln { color:var(--accent); }
  #tip { position:fixed; pointer-events:none; z-index:9; max-width:320px; padding:8px 10px; font-size:12px; display:none; }
  #tip .tn{font-weight:600} #tip .tt{color:var(--text2);font-size:11px} #tip .ts{color:var(--text);margin-top:3px}
  #mm { position:fixed; right:14px; bottom:14px; width:210px; height:140px; z-index:5; padding:0; cursor:crosshair; }
  #tour { position:fixed; right:240px; bottom:14px; width:340px; padding:14px 16px; z-index:6; }
  #tour h4 { margin:0 0 4px; font-size:14px; } #tour .desc { font-size:13px; color:var(--text); line-height:1.5; margin:6px 0 12px; }
  .tourbtns { display:flex; gap:8px; align-items:center; }
  button { background:var(--elevated); color:var(--text); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:8px; padding:6px 12px; font-size:12px; cursor:pointer; }
  button:hover { background:rgba(var(--accent-rgb),0.28); } #tcount { flex:1; text-align:center; color:var(--text2); font-size:12px; }
  #tourstart { position:fixed; right:240px; bottom:14px; z-index:5; }
  #topbar .bar { display:flex; gap:6px; flex:none; }
  #topbar .bar button { padding:5px 9px; font-size:11px; }
  #topbar .bar button.on { color:var(--accent); border-color:rgba(var(--accent-rgb),0.5); background:rgba(var(--accent-rgb),0.12); }
  #exportMenu { position:fixed; top:56px; right:14px; z-index:8; display:flex; flex-direction:column; padding:6px; gap:2px; min-width:130px; }
  #filterMenu { position:fixed; top:56px; right:14px; z-index:9; width:240px; max-height:78vh; overflow:auto; padding:12px; }
  #filterMenu h5 { margin:11px 2px 5px; font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }
  #filterMenu h5:first-child { margin-top:0; }
  #filterMenu label { display:flex; align-items:center; gap:7px; font-size:12px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  #filterMenu label:hover { background:var(--elevated); } #filterMenu input { accent-color:var(--accent); }
  #searchWrap { position:relative; display:flex; align-items:center; gap:6px; flex:none; }
  .smode { display:flex; background:var(--elevated); border-radius:7px; padding:2px; }
  .smode button { border:none; background:transparent; color:var(--text2); font-size:10px; padding:3px 7px; border-radius:5px; cursor:pointer; }
  .smode button.on { background:rgba(var(--accent-rgb),0.2); color:var(--accent); }
  #searchResults { position:fixed; z-index:9; width:330px; max-height:300px; overflow:auto; padding:6px; display:none; }
  #searchResults .sr { display:flex; align-items:center; gap:8px; padding:5px 7px; border-radius:6px; cursor:pointer; }
  #searchResults .sr:hover { background:var(--elevated); }
  #searchResults .srb { font-size:9px; text-transform:uppercase; border:1px solid; border-radius:3px; padding:1px 4px; flex:none; }
  #searchResults .srn { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #searchResults .srbar { width:46px; height:5px; background:var(--bg); border-radius:3px; overflow:hidden; flex:none; }
  #searchResults .srbar>span { display:block; height:100%; background:var(--accent); }
  #panel .fbtn-focus { position:absolute; top:9px; right:34px; font-size:10px; padding:3px 8px; }
  #panel .fbtn-focus.on { color:var(--accent); border-color:var(--accent); background:rgba(var(--accent-rgb),0.16); }
  #exportMenu button { text-align:left; }
  .modal { position:fixed; inset:0; background:rgba(0,0,0,0.55); z-index:20; display:flex; align-items:center; justify-content:center; }
  .modal .mbox { width:440px; max-width:92vw; max-height:80vh; overflow:auto; padding:18px; position:relative; }
  .modal h4 { margin:0 0 12px; font-size:15px; }
  .modal select { width:100%; margin:5px 0; background:var(--bg); color:var(--text); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:6px; padding:7px; font-size:12px; }
  #pathResult { margin-top:12px; font-size:12px; }
  #pathResult .step { display:flex; align-items:center; gap:8px; padding:4px 6px; border-radius:6px; cursor:pointer; }
  #pathResult .step:hover { background:var(--elevated); } #pathResult .num { color:var(--bg); background:var(--accent); border-radius:99px; width:18px; height:18px; display:inline-flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; }
  .kb { display:grid; grid-template-columns:auto 1fr; gap:7px 14px; font-size:12px; align-items:center; }
  .kb kbd { font-family:ui-monospace,monospace; background:var(--bg); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:4px; padding:1px 7px; color:var(--accent); justify-self:start; }
  .tok-cm{color:#6b7f8e;font-style:italic} .tok-st{color:#c9a06c} .tok-nu{color:#d19a66} .tok-kw{color:#c084fc}
  .title, #panel h3, .ov-title, .modal h4, #tour h4 { font-family:var(--font-heading); font-weight:400; letter-spacing:.2px; }
  #topbar .personas { display:flex; gap:2px; flex:none; }
  .pa { background:transparent; border:1px solid transparent; color:var(--text2); padding:4px 9px; font-size:11px; border-radius:7px; cursor:pointer; }
  .pa:hover { color:var(--text); } .pa.active { color:var(--accent); background:rgba(var(--accent-rgb),0.1); border-color:rgba(var(--accent-rgb),0.3); }
  #zoom { position:fixed; left:14px; top:50%; transform:translateY(-50%); display:flex; flex-direction:column; gap:6px; z-index:6; }
  #zoom button { width:32px; height:32px; font-size:16px; padding:0; }
  #topbar { overflow-x:auto; } #topbar .grow { flex:1; min-width:8px; }
  #topbar #search { flex:none; width:150px; }
  .seg { display:flex; background:var(--elevated); border-radius:8px; padding:2px; flex:none; gap:2px; }
  .seg button { padding:4px 9px; font-size:11px; border:none; background:transparent; color:var(--text2); border-radius:6px; }
  .seg button.on { background:rgba(var(--accent-rgb),0.2); color:var(--accent); }
  .fnbtn { flex:none; font-size:10px; text-transform:uppercase; letter-spacing:.05em; padding:4px 8px;
    border:1px solid rgba(var(--accent-rgb),0.28); background:var(--card); color:var(--text2); border-radius:6px; }
  .fnbtn.on { border-color:#d19a66; background:rgba(209,154,102,0.12); color:#e0a96a; }
  .cats { display:flex; gap:4px; flex:none; }
  .cat { display:flex; align-items:center; gap:5px; font-size:10px; text-transform:uppercase; letter-spacing:.04em;
    padding:4px 7px; border:1px solid rgba(var(--accent-rgb),0.18); border-radius:6px; background:var(--card); color:var(--text2);
    cursor:pointer; white-space:nowrap; } .cat:hover{color:var(--text);} .cat.off{opacity:.35;}
  .cat .d, .chip .d { width:8px; height:8px; border-radius:99px; flex:none; }
  .chips { display:flex; gap:10px; flex:none; align-items:center; }
  .chip { display:flex; align-items:center; gap:5px; font-size:11px; color:var(--text2); cursor:pointer; white-space:nowrap; }
  .chip:hover{color:var(--text);} .chip.dim{opacity:.4;} .chip.active{color:var(--text);font-weight:600;}
  .chip .muted{color:var(--muted);margin-left:1px;}
  .bigbtn { width:100%; background:rgba(var(--accent-rgb),0.1); border:1px solid rgba(var(--accent-rgb),0.3); color:var(--accent);
    padding:9px; border-radius:8px; margin:6px 0 10px; cursor:pointer; font-size:13px; }
  .bigbtn:hover{ background:rgba(var(--accent-rgb),0.2); }
  .tstep { font-size:12px; padding:6px 9px; background:var(--card); border:1px solid rgba(var(--accent-rgb),0.12);
    border-radius:7px; margin:4px 0; cursor:pointer; color:var(--text); }
  .tstep:hover{ border-color:rgba(var(--accent-rgb),0.4); } .tstep .tn{ color:var(--accent); font-family:ui-monospace,monospace; }
  .ptabs { display:flex; gap:6px; margin:0 0 12px; border-bottom:1px solid rgba(var(--accent-rgb),0.14); padding-bottom:8px; }
  .ptab { flex:1; background:transparent; border:none; color:var(--text2); font-size:11px; text-transform:uppercase;
    letter-spacing:.06em; padding:6px; border-radius:6px; cursor:pointer; } .ptab.on { background:rgba(var(--accent-rgb),0.15); color:var(--accent); }
  .ftree .fdir { font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); margin:10px 0 4px;
    font-family:ui-monospace,monospace; word-break:break-all; }
  .ftree2 { font-size:12px; }
  .ftree2 .frow { display:flex; align-items:center; gap:7px; padding:3px 6px; border-radius:6px; cursor:pointer;
    color:var(--text); white-space:nowrap; }
  .ftree2 .frow:hover { background:var(--elevated); color:#fff; }
  .ftree2 .fchev { width:12px; flex:none; color:var(--muted); font-size:9px; text-align:center; }
  .ftree2 .fdirrow .fname { color:var(--text2); }
  .ftree2 .fname { overflow:hidden; text-overflow:ellipsis; }
  .ftree2 .fic { font-size:8px; font-family:ui-monospace,monospace; border:1px solid; border-radius:3px; padding:1px 0;
    min-width:22px; text-align:center; flex:none; text-transform:uppercase; line-height:1.4; }
  .ftree2 .fic-svg { flex:none; width:15px; height:15px; display:inline-flex; } .fic-svg svg { width:15px; height:15px; display:block; }
  #themeMenu { position:fixed; top:56px; right:14px; z-index:9; width:236px; max-height:82vh; overflow:auto; padding:10px; }
  .tm-h { font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); margin:10px 4px 6px; }
  .tm-h:first-child { margin-top:2px; }
  .tm-row { display:flex; align-items:center; gap:7px; width:100%; padding:7px 8px; border:1px solid transparent; background:transparent; border-radius:8px; cursor:pointer; color:var(--text); font-size:12px; }
  .tm-row:hover { background:var(--elevated); } .tm-row.on { border-color:rgba(var(--accent-rgb),0.4); background:rgba(var(--accent-rgb),0.1); }
  .tm-sw { width:13px; height:13px; border-radius:99px; border:1px solid rgba(150,150,150,0.25); flex:none; }
  .tm-row .tm-name { flex:1; text-align:left; } .tm-row .tm-chk { color:var(--accent); opacity:0; } .tm-row.on .tm-chk { opacity:1; }
  .tm-acc { display:flex; flex-wrap:wrap; gap:7px; padding:2px 4px 4px; }
  .tm-dot { width:26px; height:26px; border-radius:99px; border:2px solid transparent; cursor:pointer; padding:0; } .tm-dot.on { border-color:var(--text); }
  .tm-font { display:flex; gap:4px; padding:2px 4px; }
  .tm-fbtn { flex:1; padding:6px; font-size:11px; border:1px solid rgba(var(--accent-rgb),0.2); background:var(--elevated); color:var(--text2); border-radius:6px; cursor:pointer; }
  .tm-fbtn.on { color:var(--accent); border-color:rgba(var(--accent-rgb),0.4); background:rgba(var(--accent-rgb),0.12); }
  #panel { transition:transform .2s ease; } #panel.collapsed { transform:translateX(118%); }
  #panelReopen { position:fixed; right:0; top:120px; z-index:6; border-radius:8px 0 0 8px; padding:8px 7px; font-size:11px; }
  .pclose { background:transparent; border:none; color:var(--text2); cursor:pointer; font-size:14px; padding:0 6px; margin-left:auto; }
  .pclose:hover { color:var(--text); }
  .hidden { display:none !important; }
</style>
</head>
<body>
<canvas id="cv"></canvas>
<div id="topbar" class="card">
  <span class="title">__PROJECT_NAME__</span>
  <span class="personas">
    <button class="pa active" data-p="all" title="Code-focused — show functions">Deep Dive</button>
    <button class="pa" data-p="overview" title="High-level architecture view">Overview</button>
    <button class="pa" data-p="learn" title="Guided learning tour">Learn</button>
  </span>
  <span class="seg" id="modeSeg">
    <button data-m="structural" class="on" title="Code structure graph">Structural</button>
    <button data-m="domain" title="Business domain map">Domain</button>
  </span>
  <button id="btnDiff" class="fnbtn" title="Diff: highlight files changed since last analysis (b)">Diff OFF</button>
  <span class="seg" id="detailSeg">
    <button data-d="file" title="Files only — architecture-level">Files</button>
    <button data-d="class" class="on" title="Files + Classes">+Classes</button>
  </span>
  <button id="fnToggle" class="fnbtn" title="Toggle functions, variables & constants">fn</button>
  <span id="searchWrap">
    <input id="search" placeholder="Search nodes…" autocomplete="off"/>
    <span class="smode" id="searchMode"><button data-m="fuzzy" class="on" title="Fuzzy text match">Fuzzy</button><button data-m="semantic" title="Keyword-relevance ranking (offline, no embeddings)">Semantic</button></span>
  </span>
  <span id="catFilters" class="cats"></span>
  <span id="layerChips" class="chips"></span>
  <span class="grow"></span>
  <span class="bar">
    <button id="btnFit" title="Fit to view (f)">⤢ Fit</button>
    <button id="btnPath" title="Path finder (p)">↦ Path</button>
    <button id="btnFilter" title="Filter (i)">⛂ Filter</button>
    <button id="btnExport" title="Export (e)">⬇ Export</button>
    <button id="btnAnim" class="on" title="Toggle edge flow animation (a)">≈ Flow</button>
    <button id="btnTheme" title="Theme (t)">◑ Theme</button>
    <button id="btnHelp" title="Shortcuts (?)">?</button>
  </span>
</div>
<div id="themeMenu" class="card hidden"></div>
<div id="crumb" class="card"></div>
<div id="zoom" class="">
  <button id="zin" class="card" title="Zoom in">+</button>
  <button id="zout" class="card" title="Zoom out">−</button>
</div>
<div id="panel" class="card"></div>
<button id="panelReopen" class="card hidden" title="Show panel">‹ Panel</button>
<div id="tip" class="card"></div>
<canvas id="mm" class="card"></canvas>
<button id="tourstart">▶ Guided tour</button>
<div id="tour" class="card hidden">
  <h4 id="ttitle"></h4><div class="desc" id="tdesc"></div>
  <div class="tourbtns"><button id="tprev">‹</button><span id="tcount"></span><button id="tnext">›</button><button id="tclose">Done</button></div>
</div>
<div id="exportMenu" class="card hidden">
  <button data-x="png">⬇ PNG image</button><button data-x="svg">⬇ SVG vector</button><button data-x="json">⬇ JSON data</button>
</div>
<div id="filterMenu" class="card hidden"></div>
<div id="searchResults" class="card"></div>
<div id="pathModal" class="modal hidden"><div class="mbox card">
  <span class="close" onclick="closePath()">✕</span><h4>Dependency Path Finder</h4>
  <select id="pathFrom"></select><select id="pathTo"></select>
  <div class="tourbtns"><button id="pathFind">Find path</button><button id="pathClear">Clear</button></div>
  <div id="pathResult"></div>
</div></div>
<div id="helpModal" class="modal hidden"><div class="mbox card">
  <span class="close" onclick="document.getElementById('helpModal').classList.add('hidden')">✕</span>
  <h4>Keyboard shortcuts</h4>
  <div class="kb">
    <kbd>/</kbd><span>Focus search</span>
    <kbd>f</kbd><span>Fit graph to view</span>
    <kbd>p</kbd><span>Open path finder</span>
    <kbd>e</kbd><span>Export menu</span>
    <kbd>a</kbd><span>Toggle edge-flow animation</span>
    <kbd>d</kbd><span>Toggle Domain / Structural view</span>
    <kbd>i</kbd><span>Filter panel</span>
    <kbd>x</kbd><span>Focus selected node (1-hop)</span>
    <kbd>b</kbd><span>Toggle diff overlay (changed files)</span>
    <kbd>?</kbd><span>This help</span>
    <kbd>Esc</kbd><span>Close panel / tour / modal</span>
    <kbd>← →</kbd><span>Prev / next tour step</span>
  </div>
</div></div>
<script>
const DATA = __DATA_JSON__;
const N=DATA.nodes, E=DATA.edges, L=DATA.layers, TY=DATA.types, TOUR=DATA.tour, CT=DATA.containers;
const LC=DATA.layerCards||[], LE=DATA.layerEdges||[], lcW=DATA.layerCardW||300, lcH=DATA.layerCardH||172;
const DM=DATA.domains||[], DE=DATA.domainEdges||[], dW=DATA.domainCardW||300, dH=DATA.domainCardH||150;
const cardW=DATA.cardW, cardH=DATA.cardH;
const FILE_LEVEL=new Set(['file','config','document','service','pipeline','table','schema','resource','endpoint']);
let view='overview', lhover=-1, sidebarTab='info';   // 'overview' shows layer cards; a number drills into that layer
let graphMode='structural', dhover=-1, selDomain=-1; // graphMode: 'structural' | 'domain'
let animOn=true, dashPhase=0, _animRunning=false;    // marching-ants edge-flow animation
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
const nbr=N.map(()=>new Set()), etype={};
for(const e of E){ const a=e[0],b=e[1]; nbr[a].add(b); nbr[b].add(a); etype[a+'_'+b]=e[2]; }
const edgeBetween=(i,j)=>etype[i+'_'+j]||etype[j+'_'+i]||'related';
// --- theme engine: CSS variables drive the DOM; T mirrors them for the canvas ---
const T={};
function ac(a){ return 'rgba('+(T.accentRgb||'212,165,116')+','+a+')'; }
function hexToRgb(h){ h=(h||'').replace('#',''); if(h.length===3)h=h.split('').map(c=>c+c).join('');
  const n=parseInt(h||'0',16); return [(n>>16)&255,(n>>8)&255,n&255].join(','); }
function readTheme(){ const s=getComputedStyle(document.documentElement), g=(k,d)=>(s.getPropertyValue(k).trim()||d);
  T.bg=g('--bg','#0a0a0a'); T.card=g('--card','#1a1a1a'); T.text=g('--text','#f5f0eb');
  T.text2=g('--text2','#a39787'); T.muted=g('--muted','#6b5f53'); T.accent=g('--accent','#d4a574');
  T.accentRgb=g('--accent-rgb','91,164,207'); T.tint=g('--tint','rgba(255,255,255,0.02)'); T.fontHeading=g('--font-heading','Georgia,serif'); }
const THEMES={
 gold:{label:'Dark Gold',bg:'#0a0a0a',elevated:'#241c14',card:'#1a1a1a',codeBg:'#0f0d0b',text:'#f5f0eb',text2:'#a39787',muted:'#6b5f53',accent:'#d4a574',tint:'rgba(255,255,255,0.02)',light:false},
 ocean:{label:'Dark Ocean',bg:'#0a0e14',elevated:'#1b2530',card:'#1a222c',codeBg:'#0b0f15',text:'#e8edf2',text2:'#87939f',muted:'#536b7a',accent:'#5ba4cf',tint:'rgba(255,255,255,0.02)',light:false},
 forest:{label:'Dark Forest',bg:'#0a0f0c',elevated:'#172017',card:'#16201a',codeBg:'#0a0f0b',text:'#e9f0ea',text2:'#8aa394',muted:'#5a7563',accent:'#5fb389',tint:'rgba(255,255,255,0.02)',light:false},
 rose:{label:'Dark Rose',bg:'#120a0e',elevated:'#241820',card:'#211820',codeBg:'#140a10',text:'#f2e8ed',text2:'#a3879a',muted:'#7a536b',accent:'#cf7a8a',tint:'rgba(255,255,255,0.02)',light:false},
 light:{label:'Light Minimal',bg:'#f4f4f6',elevated:'#e9ebf0',card:'#ffffff',codeBg:'#f1f2f5',text:'#1a1f29',text2:'#5a6675',muted:'#97a2b0',accent:'#4e93ba',tint:'rgba(0,0,0,0.03)',light:true},
};
const FONTS={Serif:'Georgia,"Times New Roman",serif',Sans:'ui-sans-serif,system-ui,sans-serif',Mono:'ui-monospace,SFMono-Regular,Menlo,monospace'};
const ACCENTS=['#d4a574','#5ba4cf','#5fb389','#cf7a8a','#a78bfa','#e0a96a','#2dd4bf','#9aa3ad'];
let THEME_STATE={name:'ocean',accent:'',font:''};
function applyTheme(){ const th=THEMES[THEME_STATE.name]||THEMES.gold, r=document.documentElement.style;
  r.setProperty('--bg',th.bg); r.setProperty('--surface',th.elevated); r.setProperty('--elevated',th.elevated);
  r.setProperty('--card',th.card); r.setProperty('--code-bg',th.codeBg); r.setProperty('--text',th.text);
  r.setProperty('--text2',th.text2); r.setProperty('--muted',th.muted); r.setProperty('--tint',th.tint);
  const acc=THEME_STATE.accent||th.accent; r.setProperty('--accent',acc); r.setProperty('--accent-rgb',hexToRgb(acc));
  r.setProperty('--font-heading', FONTS[THEME_STATE.font]||FONTS.Serif);
  document.documentElement.style.colorScheme=th.light?'light':'dark';
  try{localStorage.setItem('sl-theme',JSON.stringify(THEME_STATE));}catch(e){}
  readTheme(); if(typeof draw==='function') draw(); }
let DPR=1, scale=1, ox=0, oy=0;
const hidden=new Set(), hiddenTypes=new Set(), hiddenComplex=new Set();
let hover=-1, sel=-1, matched=null, focusSet=null, tIdx=-1, pathNodes=null, pathEdges=null;
let searchMode='fuzzy', searchResults=[], focusCenter=-1;
const DIFFC=new Set(DATA.diffChanged||[]); const hasDiff=!!DATA.hasDiff; let diffOn=false;
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const SX=x=>x*scale+ox, SY=y=>y*scale+oy;
const vis=i=>view!=='overview'&&N[i].layer===view&&!hiddenTypes.has(N[i].type)&&!hiddenComplex.has(N[i].complexity);
function dim(i){ if(diffOn&&!DIFFC.has(i))return true; if(matched&&!matched.has(i))return true; if(focusSet&&!focusSet.has(i))return true;
  if(pathNodes&&!pathNodes.has(i))return true;
  if(hover>=0&&i!==hover&&!nbr[hover].has(i))return true; return false; }
// Lightweight per-line syntax highlighter (comments, strings, numbers, keywords).
const _KW=/\b(function|class|def|return|if|else|elif|for|while|do|switch|case|import|from|export|const|let|var|new|public|private|protected|static|void|int|float|double|string|str|bool|boolean|async|await|yield|self|this|super|struct|enum|impl|trait|fn|module|package|namespace|using|type|interface|extends|implements|try|catch|finally|throw|raise|with|as|in|is|not|and|or|None|True|False|null|nil|true|false|begin|end|then|elsif|require|include|pub|mut|match|where|lambda)\b/g;
function hl_code(line){ const rx=/(\/\/[^\n]*|#[^\n]*|--[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)|\b(\d[\d_.]*)\b/g;
  let out='', last=0, m;
  while((m=rx.exec(line))){ out+=_kw(line.slice(last,m.index)); const t=m[0];
    const cls=m[1]?'tok-cm':m[2]?'tok-st':'tok-nu'; out+='<span class="'+cls+'">'+esc(t)+'</span>'; last=m.index+t.length; }
  return out+_kw(line.slice(last)); }
function _kw(s){ return esc(s).replace(_KW, '<span class="tok-kw">$1</span>'); }

function bounds(){
  if(graphMode==='domain'){ if(!DM.length)return[0,0,800,600]; let a=1e9,b=1e9,c=-1e9,d=-1e9;
    for(const k of DM){a=Math.min(a,k.x-dW/2);b=Math.min(b,k.y-dH/2);c=Math.max(c,k.x+dW/2);d=Math.max(d,k.y+dH/2);} return [a,b,c,d]; }
  if(view==='overview'){ if(!LC.length)return[0,0,800,600]; let a=1e9,b=1e9,c=-1e9,d=-1e9;
    for(const k of LC){a=Math.min(a,k.x-lcW/2);b=Math.min(b,k.y-lcH/2);c=Math.max(c,k.x+lcW/2);d=Math.max(d,k.y+lcH/2);} return [a,b,c,d]; }
  const c0=CT.find(k=>k.layer===view); if(c0) return [c0.x,c0.y,c0.x+c0.w,c0.y+c0.h];
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
function dbp(fx,fy,cx,cy){ const dx=fx-cx,dy=fy-cy; if(!dx&&!dy)return[cx,cy];
  const sx=dx?(dW/2)/Math.abs(dx):1e9, sy=dy?(dH/2)/Math.abs(dy):1e9, s=Math.min(sx,sy); return [cx+dx*s,cy+dy*s]; }

function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle=T.bg; ctx.fillRect(0,0,innerWidth,innerHeight);
  updateCrumb();
  if(graphMode==='domain'){ drawDomain(); drawMinimap(); return; }
  if(view==='overview'){ drawOverview(); drawMinimap(); return; }
  // layer containers (only the drilled-in layer)
  for(const c of CT){ if(c.layer!==view)continue;
    const x=SX(c.x),y=SY(c.y),w=c.w*scale,h=c.h*scale;
    rr(x,y,w,h,11); ctx.fillStyle=T.tint; ctx.fill();
    ctx.lineWidth=1.2; ctx.strokeStyle=c.color+'66'; ctx.stroke();
    if(scale>0.28){ ctx.fillStyle=c.color; ctx.font='600 13px ui-sans-serif';
      ctx.fillText(c.name+'  ('+c.count+')', x+12, y+21); } }
  // edges (dashed + animated "marching ants" when flow animation is on)
  ctx.setLineDash(animOn?[7,7]:[]); ctx.lineDashOffset=animOn?-dashPhase:0;
  for(const e of E){ const a=e[0],b=e[1]; if(!vis(a)||!vis(b))continue;
    const onpath = pathEdges && (pathEdges.has(a+'_'+b)||pathEdges.has(b+'_'+a));
    const lit=(hover===a||hover===b||sel===a||sel===b)||onpath;
    const A=N[a],B=N[b], p1=bp(B.x,B.y,A.x,A.y), p2=bp(A.x,A.y,B.x,B.y);
    const x1=SX(p1[0]),y1=SY(p1[1]),x2=SX(p2[0]),y2=SY(p2[1]);
    ctx.strokeStyle=onpath?ac(0.95):lit?ac(0.8):((dim(a)&&dim(b))?ac(0.05):ac(0.22));
    // curved (quadratic bezier) connector with a perpendicular bow at the midpoint
    const mx=(x1+x2)/2, my=(y1+y2)/2, dxe=x2-x1, dye=y2-y1, len=Math.hypot(dxe,dye)||1;
    const off=Math.min(38,len*0.16), cxp=mx-dye/len*off, cyp=my+dxe/len*off;
    ctx.lineWidth=onpath?3:lit?2:1; ctx.beginPath(); ctx.moveTo(x1,y1); ctx.quadraticCurveTo(cxp,cyp,x2,y2); ctx.stroke();
    if(scale>0.3){ const ang=Math.atan2(y2-cyp,x2-cxp),s=6;
      ctx.beginPath(); ctx.moveTo(x2,y2); ctx.lineTo(x2-s*Math.cos(ang-0.42),y2-s*Math.sin(ang-0.42));
      ctx.lineTo(x2-s*Math.cos(ang+0.42),y2-s*Math.sin(ang+0.42)); ctx.closePath(); ctx.fillStyle=ctx.strokeStyle; ctx.fill(); }
    if(e[2] && (lit || scale>0.95)){ ctx.font='9px ui-monospace,monospace'; ctx.fillStyle=lit?T.text:ac(0.55);
      ctx.fillText(e[2], (mx+cxp)/2+3, (my+cyp)/2-3); } }
  ctx.setLineDash([]);
  // cards
  for(let i=0;i<N.length;i++){ if(vis(i)) drawCard(i); }
  drawMinimap();
}
function drawCard(i){ const n=N[i]; const w=cardW*scale,h=cardH*scale,x=SX(n.x)-w/2,y=SY(n.y)-h/2;
  if(x>innerWidth||y>innerHeight||x+w<0||y+h<0)return;
  ctx.globalAlpha=dim(i)?0.22:1;
  rr(x,y,w,h,7); ctx.fillStyle=T.card; ctx.fill();
  ctx.fillStyle=n.color; ctx.fillRect(x,y+1,Math.max(3,4*scale),h-2);
  if(i===sel){ctx.lineWidth=2;ctx.strokeStyle=T.accent;} else if(i===hover){ctx.lineWidth=1.5;ctx.strokeStyle=n.color;} else {ctx.lineWidth=1;ctx.strokeStyle=ac(0.16);}
  rr(x,y,w,h,7); ctx.stroke();
  if(diffOn&&DIFFC.has(i)){ ctx.lineWidth=2.5; ctx.strokeStyle='#5fb389'; rr(x,y,w,h,7); ctx.stroke(); }
  if(scale>0.3){ const pad=Math.max(8,8*scale);
    ctx.font='700 '+Math.round(7*scale+3)+'px ui-monospace,monospace'; ctx.fillStyle=n.color;
    ctx.fillText(n.type.toUpperCase(), x+pad, y+Math.round(12*scale)+4);
    ctx.font='600 '+Math.round(8*scale+4)+'px ui-sans-serif'; ctx.fillStyle=T.text;
    ctx.fillText(clipText(n.name, w-pad*2), x+pad, y+h-Math.round(9*scale)-2); }
  ctx.globalAlpha=1;
}
function pick(mx,my){ const wx=(mx-ox)/scale, wy=(my-oy)/scale;
  for(let i=N.length-1;i>=0;i--){ if(!vis(i))continue; const n=N[i];
    if(Math.abs(wx-n.x)<=cardW/2 && Math.abs(wy-n.y)<=cardH/2) return i; } return -1; }
function pickLayer(mx,my){ const wx=(mx-ox)/scale, wy=(my-oy)/scale;
  for(let i=LC.length-1;i>=0;i--){ const l=LC[i]; if(Math.abs(wx-l.x)<=lcW/2 && Math.abs(wy-l.y)<=lcH/2) return l.i; } return -1; }

// --- Overview level: one descriptive card per layer + aggregated inter-layer edges ---
function wrapText(text,x,y,maxw,lh,maxLines){ const words=(text||'').split(/\s+/); let line='',ln=0;
  for(let i=0;i<words.length;i++){ const t=line?line+' '+words[i]:words[i];
    if(ctx.measureText(t).width>maxw && line){ ctx.fillText(line,x,y+ln*lh); line=words[i]; if(++ln>=maxLines){ctx.fillText(line+'…',x,y+ln*lh);return;} }
    else line=t; }
  if(line&&ln<maxLines) ctx.fillText(line,x,y+ln*lh); }
function drawOverview(){
  ctx.setLineDash(animOn?[7,7]:[]); ctx.lineDashOffset=animOn?-dashPhase:0;
  for(const e of LE){ const A=LC[e.a],B=LC[e.b]; if(!A||!B)continue;
    const x1=SX(A.x),y1=SY(A.y),x2=SX(B.x),y2=SY(B.y),mx=(x1+x2)/2,my=(y1+y2)/2;
    const dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy)||1,off=Math.min(46,len*0.16),cxp=mx-dy/len*off,cyp=my+dx/len*off;
    ctx.strokeStyle=ac(0.4); ctx.lineWidth=Math.min(5,1+Math.log2(e.count+1));
    ctx.beginPath();ctx.moveTo(x1,y1);ctx.quadraticCurveTo(cxp,cyp,x2,y2);ctx.stroke();
    ctx.fillStyle=T.text2; ctx.font='11px ui-monospace,monospace'; ctx.fillText(e.count,(mx+cxp)/2+2,(my+cyp)/2); }
  ctx.setLineDash([]);
  for(const l of LC){ const w=lcW*scale,h=lcH*scale,x=SX(l.x)-w/2,y=SY(l.y)-h/2;
    if(x>innerWidth||y>innerHeight||x+w<0||y+h<0)continue;
    rr(x,y,w,h,13); ctx.fillStyle=T.card; ctx.fill();
    ctx.fillStyle=l.color; ctx.fillRect(x,y+2,Math.max(4,5*scale),h-4);
    ctx.lineWidth=lhover===l.i?2:1; ctx.strokeStyle=lhover===l.i?T.accent:ac(0.22); rr(x,y,w,h,13); ctx.stroke();
    if(scale>0.2){ const pad=16*scale+4;
      ctx.fillStyle=l.color; ctx.font='700 '+Math.round(7*scale+3)+'px ui-monospace,monospace'; ctx.fillText('LAYER · '+l.complexity, x+pad, y+Math.round(15*scale)+4);
      ctx.fillStyle=T.text; ctx.font=Math.round(10*scale+6)+'px Georgia,serif'; ctx.fillText(clipText(l.name,w-pad*2), x+pad, y+Math.round(40*scale)+2);
      ctx.fillStyle=T.text2; ctx.font=Math.round(6.5*scale+4)+'px ui-sans-serif'; wrapText(l.description||'', x+pad, y+Math.round(58*scale)+4, w-pad*2, Math.round(7*scale+6), 4);
      ctx.fillStyle=T.muted; ctx.font=Math.round(6.5*scale+3)+'px ui-sans-serif'; ctx.fillText(l.count+' files   ·   click to explore →', x+pad, y+h-Math.round(12*scale)); } }
}
function setView(v){ if(graphMode!=='structural'){ graphMode='structural'; selDomain=-1; applyModeUI(); }
  view=v; sel=-1; matched=null; pathNodes=null; pathEdges=null; focusSet=null; lhover=-1;
  const s=document.getElementById('search'); if(s)s.value=''; renderPanel(); fit(); draw(); }
window.setView=setView;
function updateCrumb(){ const cr=document.getElementById('crumb'); if(!cr)return;
  if(graphMode==='domain'){ cr.innerHTML='Domain Map'+(selDomain>=0?' &nbsp;›&nbsp; '+esc(DM[selDomain].name):''); return; }
  if(view==='overview') cr.innerHTML='Project Overview';
  else cr.innerHTML='<button onclick="setView(\'overview\')">‹ Project</button> &nbsp;›&nbsp; '+esc((L[view]&&L[view].name)||'Layer');
  if(typeof refreshChips==='function') refreshChips(); }

// --- Domain map: business-domain cards + cross-domain flows (animated) ---
function applyModeUI(){ const struct=graphMode==='structural';
  document.querySelectorAll('#modeSeg button').forEach(b=>b.classList.toggle('on', b.dataset.m===graphMode));
  ['detailSeg','fnToggle','catFilters','layerChips'].forEach(id=>{ const el=document.getElementById(id); if(el) el.classList.toggle('hidden', !struct); }); }
function setMode(m){ if(m===graphMode)return; graphMode=m; selDomain=-1; dhover=-1; sel=-1; matched=null;
  applyModeUI(); renderPanel(); fit(); draw(); }
window.setMode=setMode;
function pickDomain(mx,my){ const wx=(mx-ox)/scale, wy=(my-oy)/scale;
  for(let i=DM.length-1;i>=0;i--){ const d=DM[i]; if(Math.abs(wx-d.x)<=dW/2 && Math.abs(wy-d.y)<=dH/2) return i; } return -1; }
function centerDomain(i){ const d=DM[i]; if(!d)return; ox=innerWidth/2-d.x*scale; oy=innerHeight/2-d.y*scale; }
function selectDomain(i){ selDomain=i; sidebarTab='info'; renderPanel(); if(i>=0) centerDomain(i); draw(); }
window.selectDomain=selectDomain;
function drawDomain(){
  ctx.setLineDash(animOn?[8,8]:[]); ctx.lineDashOffset=animOn?-dashPhase:0;
  for(const e of DE){ const A=DM[e.a],B=DM[e.b]; if(!A||!B)continue;
    const p1=dbp(B.x,B.y,A.x,A.y), p2=dbp(A.x,A.y,B.x,B.y);
    const x1=SX(p1[0]),y1=SY(p1[1]),x2=SX(p2[0]),y2=SY(p2[1]);
    const lit=(dhover===e.a||dhover===e.b||selDomain===e.a||selDomain===e.b);
    const mx=(x1+x2)/2,my=(y1+y2)/2,dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy)||1,off=Math.min(54,len*0.16),cxp=mx-dy/len*off,cyp=my+dx/len*off;
    ctx.strokeStyle=lit?ac(0.92):ac(0.32); ctx.lineWidth=lit?2.6:Math.min(4,1.2+Math.log2(e.count+1));
    ctx.beginPath();ctx.moveTo(x1,y1);ctx.quadraticCurveTo(cxp,cyp,x2,y2);ctx.stroke();
    ctx.setLineDash([]);
    if(scale>0.22){ const ang=Math.atan2(y2-cyp,x2-cxp),s=8; ctx.beginPath();ctx.moveTo(x2,y2);
      ctx.lineTo(x2-s*Math.cos(ang-0.4),y2-s*Math.sin(ang-0.4));ctx.lineTo(x2-s*Math.cos(ang+0.4),y2-s*Math.sin(ang+0.4));ctx.closePath();ctx.fillStyle=ctx.strokeStyle;ctx.fill(); }
    if(e.label&&(lit||scale>0.45)){ ctx.font='10px ui-monospace,monospace'; ctx.fillStyle=lit?T.text:ac(0.6); ctx.fillText(e.label,(mx+cxp)/2+3,(my+cyp)/2-2); }
    if(animOn){ctx.setLineDash([8,8]);ctx.lineDashOffset=-dashPhase;}
  }
  ctx.setLineDash([]);
  for(const d of DM){ const w=dW*scale,h=dH*scale,x=SX(d.x)-w/2,y=SY(d.y)-h/2;
    if(x>innerWidth||y>innerHeight||x+w<0||y+h<0)continue;
    const on=(dhover===d.i||selDomain===d.i);
    rr(x,y,w,h,12); ctx.fillStyle=T.card; ctx.fill();
    ctx.fillStyle=d.color; ctx.fillRect(x,y+2,Math.max(4,5*scale),h-4);
    ctx.lineWidth=on?2:1; ctx.strokeStyle=on?T.accent:ac(0.22); rr(x,y,w,h,12); ctx.stroke();
    if(scale>0.16){ const pad=14*scale+5;
      ctx.fillStyle=d.color; ctx.font='700 '+Math.round(6.5*scale+3)+'px ui-monospace,monospace'; ctx.fillText('DOMAIN', x+pad, y+Math.round(15*scale)+2);
      ctx.fillStyle=T.text; ctx.font=Math.round(9*scale+5)+'px '+(T.fontHeading||'Georgia,serif'); ctx.fillText(clipText(d.name,w-pad*2), x+pad, y+Math.round(37*scale)+2);
      ctx.fillStyle=T.text2; ctx.font=Math.round(6*scale+4)+'px ui-sans-serif'; wrapText(d.description||'', x+pad, y+Math.round(53*scale), w-pad*2, Math.round(6*scale+6), 2);
      if(scale>0.34 && d.entities && d.entities.length){ ctx.fillStyle=T.muted; ctx.font='9px ui-sans-serif'; ctx.fillText('ENTITIES', x+pad, y+h-Math.round(32*scale)-2);
        ctx.fillStyle=T.text2; ctx.font='10px ui-monospace,monospace'; ctx.fillText(clipText(d.entities.slice(0,4).join('   '), w-pad*2), x+pad, y+h-Math.round(18*scale)); }
      ctx.fillStyle=T.muted; ctx.font=Math.round(6*scale+3)+'px ui-sans-serif'; ctx.fillText(d.nFiles+' files  ·  '+d.flowCount+' flows', x+pad, y+h-Math.round(6*scale)); }
  }
}
function domainOverHTML(){ let h='<div class="ov-title">Domain Map</div><div class="ov-desc">Business domains inferred from the project structure, linked by cross-domain flows. Click a domain for details.</div>';
  h+='<div class="ov-grid">'+stat('Domains',DM.length)+stat('Flows',DE.length)+'</div>';
  if(DM.length){ h+='<div class="ov-h">Domains</div>';
    for(const d of DM) h+='<div class="nb" data-dom="'+d.i+'"><span class="sw" style="display:inline-block;width:10px;height:10px;border-radius:3px;background:'+d.color+'"></span> '+esc(d.name)+' <span class="muted">· '+d.nFiles+' files</span></div>'; }
  else h+='<div class="ov-desc" style="margin-top:10px">No domains detected (no nested directories to group by).</div>';
  return h; }
function domainInfoHTML(i){ const d=DM[i]; let h='<span class="close" onclick="selectDomain(-1)">✕</span>';
  h+='<span class="ptype" style="color:'+d.color+';border-color:'+d.color+'">domain</span>';
  h+='<h3>'+esc(d.name)+'</h3>';
  if(d.description) h+='<div class="summary">'+esc(d.description)+'</div>';
  h+='<div class="ov-grid">'+stat('Files',d.nFiles)+stat('Entities',d.nEntities)+stat('Flows',d.flowCount)+'</div>';
  if(d.entities&&d.entities.length) h+='<div class="ov-h">Entities</div><div class="pills">'+d.entities.map(e=>'<span class="pill">'+esc(e)+'</span>').join('')+'</div>';
  const outs=DE.filter(e=>e.a===i), ins=DE.filter(e=>e.b===i);
  if(outs.length){ h+='<div class="ov-h">Flows out ('+outs.length+')</div>'; for(const e of outs) h+='<div class="nb" data-dom="'+e.b+'"><span class="et">'+esc(e.label||'flow')+'</span> '+esc(DM[e.b].name)+' <span class="muted">· '+e.count+'</span></div>'; }
  if(ins.length){ h+='<div class="ov-h">Flows in ('+ins.length+')</div>'; for(const e of ins) h+='<div class="nb" data-dom="'+e.a+'"><span class="et">'+esc(e.label||'flow')+'</span> '+esc(DM[e.a].name)+' <span class="muted">· '+e.count+'</span></div>'; }
  if(d.members&&d.members.length){ h+='<div class="ov-h">Files ('+d.nFiles+')</div>'; for(const idx of d.members.slice(0,40)){ const n=N[idx]; if(!n||!FILE_LEVEL.has(n.type))continue; h+='<div class="nb" data-i="'+idx+'">'+esc(n.name)+' <span class="muted">· '+esc(n.type)+'</span></div>'; } }
  return h; }

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
  if(TOUR.length){ h+='<div class="ov-h">Project Tour · '+TOUR.length+' steps</div><button class="bigbtn" onclick="startTour()">▶ Start Tour</button>';
    TOUR.forEach((stp,i)=>{ h+='<div class="tstep" data-t="'+i+'"><span class="tn">'+(i+1)+'.</span> '+esc(stp.title)+'</div>'; }); }
  return h; }
function codeHTML(src, range){ const lines=src.split('\n'); const s=(range&&range[0])||0, e=(range&&range[1])||0;
  let h='<div class="code"><table class="ct">';
  for(let i=0;i<lines.length;i++){ const ln=i+1, hl=(ln>=s&&ln<=e)?' class="hl"':'';
    h+='<tr'+hl+'><td class="ln">'+ln+'</td><td class="lc">'+hl_code(lines[i]||' ')+'</td></tr>'; }
  return h+'</table></div>'; }
function infoHTML(i){ const n=N[i]; let h='<span class="close" onclick="select(-1)">✕</span>';
  h+='<button class="fbtn-focus'+(focusCenter===i?' on':'')+'" onclick="focusOn('+i+')" title="Isolate this node + its neighbors (x)">⊙ '+(focusCenter===i?'Unfocus':'Focus')+'</button>';
  h+='<span class="ptype" style="color:'+n.color+';border-color:'+n.color+'">'+esc(n.type)+'</span> <span class="cx cx-'+esc(n.complexity)+'">●&nbsp;'+esc(n.complexity)+'</span>';
  h+='<h3>'+esc(n.name)+'</h3>';
  if(n.path){ h+='<div class="path">'+esc(n.path)+(n.lineRange?' <span class="lr">L'+n.lineRange[0]+'–'+n.lineRange[1]+'</span>':'')+'</div>'; }
  if(n.signature) h+='<pre class="sig">'+esc(n.signature)+'</pre>';
  if(n.summary) h+='<div class="summary">'+esc(n.summary)+'</div>';
  if(n.docstring && n.docstring!==n.summary) h+='<div class="ov-h">Documentation</div><div class="doc">'+esc(n.docstring)+'</div>';
  if(n.languageNotes) h+='<div class="ov-h">Language notes</div><div class="doc">'+esc(n.languageNotes)+'</div>';
  if(n.tags&&n.tags.length) h+='<div class="pills">'+n.tags.map(t=>'<span class="pill">'+esc(t)+'</span>').join('')+'</div>';
  if(n.layer>=0) h+='<div class="ov-h">Layer</div><div class="nb" style="cursor:default"><span class="sw" style="background:'+L[n.layer].color+'"></span>&nbsp;'+esc(L[n.layer].name)+'</div>';
  const conns=[...nbr[i]].sort((a,b)=>N[b].deg-N[a].deg);
  if(conns.length){ h+='<div class="ov-h">Connections ('+conns.length+')</div>';
    for(const j of conns.slice(0,60)) h+='<div class="nb" data-i="'+j+'"><span class="et">'+esc(edgeBetween(i,j))+'</span> '+esc(N[j].name)+'</div>'; }
  const src=DATA.sources[n.path];
  if(src){ h+='<div class="ov-h">Source · '+esc(n.path)+'</div>'+codeHTML(src, n.lineRange); }
  return h; }
// --- collapsible file-tree (IDE-style) ---
const openDirs=new Set(); let FTREE=null;
function buildTree(){ const root={dirs:{},files:[]};
  for(let i=0;i<N.length;i++){ const n=N[i]; if(!FILE_LEVEL.has(n.type)||!n.path)continue;
    const parts=n.path.split('/'); let cur=root;
    for(let k=0;k<parts.length-1;k++){ const d=parts[k]; cur.dirs[d]=cur.dirs[d]||{dirs:{},files:[]}; cur=cur.dirs[d]; }
    cur.files.push({i, name:parts[parts.length-1], color:n.color}); }
  return root; }
const _EXT={py:'py',pyi:'py',js:'js',mjs:'js',cjs:'js',jsx:'jsx',ts:'ts',tsx:'tsx',md:'md',markdown:'md',rst:'md',
  json:'{}',yaml:'yml',yml:'yml',toml:'tml',ini:'ini',xml:'xml',csv:'csv',env:'env',go:'go',rs:'rs',rb:'rb',php:'php',
  java:'jv',kt:'kt',swift:'sw',scala:'sc',c:'c',h:'h',cc:'c+',cpp:'c+',hpp:'c+',cs:'c#',lua:'lua',sh:'sh',bash:'sh',
  ps1:'ps',sql:'sql',graphql:'gql',proto:'pb',html:'<>',htm:'<>',css:'css',scss:'css',vue:'vue',svelte:'sv',
  tf:'tf',tfvars:'tf',hcl:'hcl',vhd:'hdl',vhdl:'hdl',v:'v',sv:'sv',cob:'cob',cbl:'cob',f90:'f90',f:'f',adb:'ada',
  ads:'ada',pas:'pas',hs:'hs',lhs:'hs',ml:'ml',mli:'ml',ex:'ex',exs:'ex',erl:'erl',clj:'clj',elm:'elm',jl:'jl',
  r:'r',pl:'pl',pm:'pl',groovy:'gv',gradle:'gv',dart:'dt',zig:'zig',nim:'nim',cr:'cr',d:'d',sol:'sol',m:'m',mm:'m+',
  tcl:'tcl',lisp:'lsp',scm:'scm',rkt:'rkt',gleam:'gl',odin:'odn',glsl:'gl',hlsl:'hl',wgsl:'wg',dockerfile:'dk'};
function extBadge(name,color){ const low=name.toLowerCase();
  // real vscode-icons file-type logo if we have one (matched by filename, then extension)
  let key=(DATA.iconName&&DATA.iconName[low]);
  const ext=(low.indexOf('.')>=0?low.split('.').pop():low);
  if(!key) key=(DATA.iconExt&&DATA.iconExt[ext]);
  const svg=key&&DATA.iconSvg&&DATA.iconSvg[key];
  if(svg) return '<span class="fic-svg">'+svg+'</span>';
  const lbl=_EXT[ext]||(ext?ext.slice(0,3):'•');   // fallback text badge
  return '<span class="fic" style="color:'+color+';border-color:'+color+'66">'+esc(lbl)+'</span>'; }
function treeHTML(node, prefix, depth){ let h=''; const dirNames=Object.keys(node.dirs).sort();
  for(const d of dirNames){ const path=prefix?prefix+'/'+d:d, open=openDirs.has(path);
    const fic=DATA.iconSvg&&DATA.iconSvg[open?'_folder_open':'_folder'];
    h+='<div class="frow fdirrow" data-d="'+esc(path)+'" style="padding-left:'+(depth*13+6)+'px"><span class="fchev">'+(open?'▾':'▸')+'</span>'+(fic?'<span class="fic-svg">'+fic+'</span>':'')+'<span class="fname">'+esc(d)+'</span></div>';
    if(open) h+=treeHTML(node.dirs[d], path, depth+1); }
  for(const f of node.files){ h+='<div class="frow fitem" data-i="'+f.i+'" style="padding-left:'+(depth*13+20)+'px">'+extBadge(f.name,f.color)+'<span class="fname">'+esc(f.name)+'</span></div>'; }
  return h; }
function filesHTML(){ if(!FTREE){ FTREE=buildTree(); Object.keys(FTREE.dirs).forEach(d=>openDirs.add(d)); }
  if(!Object.keys(FTREE.dirs).length && !FTREE.files.length) return '<div class="ov-desc">No files.</div>';
  return '<div class="ftree2">'+treeHTML(FTREE,'',0)+'</div>'; }
function renderPanel(){
  const tabs='<div class="ptabs"><button class="ptab'+(sidebarTab==='info'?' on':'')+'" data-tab="info">Info</button>'
    +'<button class="ptab'+(sidebarTab==='files'?' on':'')+'" data-tab="files">Files</button>'
    +'<button class="pclose" title="Hide panel">⟩</button></div>';
  const body = sidebarTab==='files' ? filesHTML()
    : graphMode==='domain' ? (selDomain>=0 ? domainInfoHTML(selDomain) : domainOverHTML())
    : (sel>=0 ? infoHTML(sel) : overviewHTML());
  panel.innerHTML = tabs + body;
  panel.querySelectorAll('.ptab').forEach(el=>el.onclick=()=>{ sidebarTab=el.dataset.tab; renderPanel(); });
  panel.querySelector('.pclose').onclick=()=>togglePanel(false);
  panel.querySelectorAll('.nb[data-dom]').forEach(el=>el.onclick=()=>selectDomain(+el.dataset.dom));
  panel.querySelectorAll('.nb[data-i]').forEach(el=>el.onclick=()=>goToNode(+el.dataset.i));
  panel.querySelectorAll('.fitem[data-i]').forEach(el=>el.onclick=()=>goToNode(+el.dataset.i));
  panel.querySelectorAll('.fdirrow').forEach(el=>el.onclick=()=>{ const p=el.dataset.d;
    if(openDirs.has(p))openDirs.delete(p); else openDirs.add(p); renderPanel(); });
  panel.querySelectorAll('.tstep').forEach(el=>el.onclick=()=>{ startTour(); tIdx=+el.dataset.t; showStep(); });
  const hl=panel.querySelector('.ct tr.hl'); if(hl) hl.scrollIntoView({block:'center'}); }
function togglePanel(open){ panel.classList.toggle('collapsed', !open);
  document.getElementById('panelReopen').classList.toggle('hidden', open); }
window.togglePanel=togglePanel;
document.getElementById('panelReopen').onclick=()=>togglePanel(true);
function select(i){ sel=i; focusSet=null; focusCenter=-1; renderPanel(); if(i>=0) center([i],false); draw(); }
function goToNode(i){ if(i<0)return; if(graphMode!=='structural'){ graphMode='structural'; selDomain=-1; applyModeUI(); }
  if(N[i]&&N[i].layer>=0) view=N[i].layer; sidebarTab='info'; sel=i; focusSet=null; focusCenter=-1; renderPanel(); center([i],true); draw(); }
window.select=select; window.goToNode=goToNode;

// --- search: Fuzzy (text) / Semantic (offline keyword-relevance) + ranked results dropdown ---
const gid = id => document.getElementById(id);
function fuzzySub(s,q){ let i=0; for(const c of s){ if(c===q[i]) i++; if(i===q.length) return true; } return q.length===0; }
function scoreNode(n,q){
  const name=(n.name||'').toLowerCase(), path=(n.path||'').toLowerCase(), sum=(n.summary||'').toLowerCase(), tags=(n.tags||[]).join(' ').toLowerCase();
  if(searchMode==='semantic'){ const toks=q.split(/\s+/).filter(Boolean); if(!toks.length)return 0; let hit=0;
    for(const t of toks){ if(name.includes(t))hit+=1; else if(sum.includes(t)||tags.includes(t))hit+=0.6; else if(path.includes(t))hit+=0.4; } return Math.min(1,hit/toks.length); }
  if(name===q)return 1; if(name.startsWith(q))return 0.92; if(name.includes(q))return 0.8;
  if(fuzzySub(name,q))return 0.6; if(path.includes(q)||sum.includes(q))return 0.45; return 0;
}
function renderSearchResults(){ const el=gid('searchResults'); if(!el)return;
  if(!searchResults.length){ el.style.display='none'; return; }
  const sb=gid('search').getBoundingClientRect(); el.style.left=sb.left+'px'; el.style.top=(sb.bottom+6)+'px';
  el.innerHTML=searchResults.map(([i,s])=>{ const n=N[i];
    return '<div class="sr" data-i="'+i+'"><span class="srb" style="color:'+n.color+';border-color:'+n.color+'">'+esc(n.type)+'</span><span class="srn">'+esc(n.name)+'</span><span class="srbar"><span style="width:'+Math.round(s*100)+'%"></span></span></div>'; }).join('');
  el.querySelectorAll('.sr').forEach(x=>x.onclick=()=>{ goToNode(+x.dataset.i); gid('searchResults').style.display='none'; });
  el.style.display='block'; }
function runSearch(q){ q=(q||'').trim().toLowerCase();
  if(!q){ matched=null; searchResults=[]; renderSearchResults(); draw(); return; }
  const scored=[]; for(let i=0;i<N.length;i++){ const s=scoreNode(N[i],q); if(s>0) scored.push([i,s]); }
  scored.sort((a,b)=>b[1]-a[1]); matched=new Set(scored.map(x=>x[0])); searchResults=scored.slice(0,6);
  renderSearchResults(); draw(); }
gid('search').addEventListener('input',e=>runSearch(e.target.value));
gid('search').addEventListener('focus',()=>{ if(searchResults.length) renderSearchResults(); });
gid('search').addEventListener('blur',()=>setTimeout(()=>{ const el=gid('searchResults'); if(el)el.style.display='none'; },180));
document.querySelectorAll('#searchMode button').forEach(b=>b.onclick=()=>{ searchMode=b.dataset.m;
  document.querySelectorAll('#searchMode button').forEach(x=>x.classList.toggle('on',x.dataset.m===searchMode)); runSearch(gid('search').value); });

// --- header: category filters, detail toggle, layer chips (like the original dashboard) ---
const CATS=[
  {n:'Code',t:['file','function','class','module','variable','constant'],c:'#4a7c9b'},
  {n:'Config',t:['config'],c:'#5eead4'},
  {n:'Docs',t:['document'],c:'#7dd3fc'},
  {n:'Infra',t:['service','pipeline','resource'],c:'#a78bfa'},
  {n:'Data',t:['table','schema'],c:'#6ee7b7'},
  {n:'Domain',t:['concept','domain','flow','step'],c:'#b07a8a'},
  {n:'Knowledge',t:['article','entity','topic','claim','source'],c:T.accent},
];
(function(){ const el=document.getElementById('catFilters');
  el.innerHTML=CATS.map((c,i)=>'<button class="cat" data-i="'+i+'" title="Toggle '+c.n+' nodes"><span class="d" style="background:'+c.c+'"></span>'+c.n+'</button>').join('');
  el.querySelectorAll('.cat').forEach(b=>b.onclick=()=>{ const c=CATS[+b.dataset.i], off=c.t.some(t=>hiddenTypes.has(t));
    if(off){ c.t.forEach(t=>hiddenTypes.delete(t)); } else { c.t.forEach(t=>hiddenTypes.add(t)); }
    b.classList.toggle('off', !off); draw(); }); })();
(function(){ const el=document.getElementById('layerChips');
  el.innerHTML=L.map((l,i)=>'<span class="chip" data-i="'+i+'"><span class="d" style="background:'+l.color+'"></span>'+esc(l.name)+'<span class="muted">('+l.count+')</span></span>').join('');
  el.querySelectorAll('.chip').forEach(x=>x.onclick=()=>setView(+x.dataset.i)); })();
function refreshChips(){ document.querySelectorAll('#layerChips .chip').forEach((x,i)=>{
  x.classList.toggle('active', view===i); x.classList.toggle('dim', view!=='overview'&&view!==i); }); }

// detail level (Files / +Classes) + function toggle.
// Small projects (e.g. one main() function) show functions by default so the
// drill-in view isn't nearly empty; larger graphs stay at the cleaner file/class level.
let detail='class', showFns=(N.length<=24);
function applyDetail(){ ['class','function','variable','constant'].forEach(t=>hiddenTypes.delete(t));
  if(detail==='file'){ ['class','function','variable','constant'].forEach(t=>hiddenTypes.add(t)); }
  else if(!showFns){ ['function','variable','constant'].forEach(t=>hiddenTypes.add(t)); }
  document.querySelectorAll('#detailSeg button').forEach(b=>b.classList.toggle('on', b.dataset.d===detail));
  document.getElementById('fnToggle').classList.toggle('on', showFns);
  draw(); }
document.querySelectorAll('#detailSeg button').forEach(b=>b.onclick=()=>{ detail=b.dataset.d; if(detail==='file')showFns=false; applyDetail(); });
document.getElementById('fnToggle').onclick=()=>{ showFns=!showFns; if(showFns)detail='class'; applyDetail(); };

// camera
let drag=false,lx,ly,moved=false;
cv.addEventListener('mousedown',e=>{drag=true;moved=false;lx=e.clientX;ly=e.clientY;});
window.addEventListener('mousemove',e=>{ if(drag){ox+=e.clientX-lx;oy+=e.clientY-ly;lx=e.clientX;ly=e.clientY;moved=true;draw();return;}
  if(graphMode==='domain'){ const h=pickDomain(e.clientX,e.clientY); if(h!==dhover){dhover=h;cv.style.cursor=h>=0?'pointer':'grab';draw();} tooltip(-1,e); return; }
  if(view==='overview'){ const h=pickLayer(e.clientX,e.clientY); if(h!==lhover){lhover=h;cv.style.cursor=h>=0?'pointer':'grab';draw();} tooltip(-1,e); return; }
  const h=pick(e.clientX,e.clientY); if(h!==hover){hover=h;cv.style.cursor=h>=0?'pointer':'grab';draw();} tooltip(h,e); });
window.addEventListener('mouseup',e=>{ if(drag&&!moved){
    if(graphMode==='domain'){ const h=pickDomain(e.clientX,e.clientY); selectDomain(h); }
    else if(view==='overview'){ const h=pickLayer(e.clientX,e.clientY); if(h>=0) setView(h); }
    else { const h=pick(e.clientX,e.clientY); select(h); } } drag=false; });
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0016);
  ox=e.clientX-(e.clientX-ox)*f; oy=e.clientY-(e.clientY-oy)*f; scale*=f; draw();},{passive:false});

// minimap
const mm=document.getElementById('mm'), mmx=mm.getContext('2d'); const MM={w:210,h:140,s:1,ox:0,oy:0};
function mmInit(){ const[a,b,c,d]=bounds(); const gw=(c-a)||1,gh=(d-b)||1,p=8;
  mm.width=MM.w*DPR; mm.height=MM.h*DPR; mm.style.width=MM.w+'px'; mm.style.height=MM.h+'px';
  MM.s=Math.min((MM.w-2*p)/gw,(MM.h-2*p)/gh); MM.ox=p-a*MM.s+(MM.w-2*p-gw*MM.s)/2; MM.oy=p-b*MM.s+(MM.h-2*p-gh*MM.s)/2; }
const mmPt=(x,y)=>[x*MM.s+MM.ox,y*MM.s+MM.oy];
function drawMinimap(){ if(!mm.width)return; mmx.setTransform(DPR,0,0,DPR,0,0); mmx.fillStyle=T.bg; mmx.fillRect(0,0,MM.w,MM.h);
  if(graphMode==='domain'){ for(const d of DM){ const q=mmPt(d.x-dW/2,d.y-dH/2); mmx.fillStyle=d.color; mmx.globalAlpha=0.9; mmx.fillRect(q[0],q[1],Math.max(3,dW*MM.s),Math.max(2,dH*MM.s)); } mmx.globalAlpha=1; }
  else if(view==='overview'){ for(const l of LC){ const q=mmPt(l.x-lcW/2,l.y-lcH/2); mmx.fillStyle=l.color; mmx.globalAlpha=0.9; mmx.fillRect(q[0],q[1],Math.max(3,lcW*MM.s),Math.max(2,lcH*MM.s)); } mmx.globalAlpha=1; }
  else { for(let i=0;i<N.length;i++){ if(!vis(i))continue; const n=N[i],q=mmPt(n.x,n.y); mmx.globalAlpha=dim(i)?0.25:0.95; mmx.fillStyle=n.color; mmx.fillRect(q[0]-1,q[1]-0.6,Math.max(2,cardW*MM.s),Math.max(1.4,cardH*MM.s)); } mmx.globalAlpha=1; }
  const p0=mmPt((0-ox)/scale,(0-oy)/scale),p1=mmPt((innerWidth-ox)/scale,(innerHeight-oy)/scale);
  mmx.strokeStyle=T.accent; mmx.lineWidth=1; mmx.strokeRect(p0[0],p0[1],p1[0]-p0[0],p1[1]-p0[1]); }
mm.addEventListener('mousedown',e=>{ const r=mm.getBoundingClientRect(); const wx=((e.clientX-r.left)-MM.ox)/MM.s, wy=((e.clientY-r.top)-MM.oy)/MM.s;
  ox=innerWidth/2-wx*scale; oy=innerHeight/2-wy*scale; draw(); });

// tour
function center(idxs,zoom){ if(!idxs.length)return; let a=1e9,b=1e9,c=-1e9,d=-1e9;
  idxs.forEach(i=>{const n=N[i];a=Math.min(a,n.x);b=Math.min(b,n.y);c=Math.max(c,n.x);d=Math.max(d,n.y);});
  if(zoom) scale=Math.max(0.5,Math.min(1.2,scale)); ox=innerWidth/2-(a+c)/2*scale; oy=innerHeight/2-(b+d)/2*scale; }
function showStep(){ const s=TOUR[tIdx]; focusSet=new Set(s.nodeIds); s.nodeIds.forEach(i=>nbr[i].forEach(j=>focusSet.add(j)));
  document.getElementById('ttitle').textContent=(tIdx+1)+'. '+s.title; document.getElementById('tdesc').textContent=s.description;
  document.getElementById('tcount').textContent=(tIdx+1)+' / '+TOUR.length;
  // drill into the layer the step's first node lives in, so it's actually visible
  if(s.nodeIds.length){ const ly=N[s.nodeIds[0]].layer; if(ly>=0) view=ly; sel=s.nodeIds[0]; renderPanel(); }
  center(s.nodeIds,true); draw(); }
function startTour(){ if(!TOUR.length)return; tIdx=0; document.getElementById('tour').classList.remove('hidden'); document.getElementById('tourstart').classList.add('hidden'); showStep(); }
function endTour(){ tIdx=-1; focusSet=null; document.getElementById('tour').classList.add('hidden'); document.getElementById('tourstart').classList.remove('hidden'); draw(); }
document.getElementById('tourstart').onclick=startTour;
document.getElementById('tprev').onclick=()=>{if(tIdx>0){tIdx--;showStep();}};
document.getElementById('tnext').onclick=()=>{if(tIdx<TOUR.length-1){tIdx++;showStep();}else endTour();};
document.getElementById('tclose').onclick=endTour;
if(!TOUR.length) document.getElementById('tourstart').classList.add('hidden');
window.startTour=startTour;
// --- toolbar: fit / export / path finder / help ---
const $=id=>document.getElementById(id);
function fitAll(){ matched=null; pathNodes=null; pathEdges=null; focusSet=null; focusCenter=-1; fit(); draw(); }
// focus mode: isolate a node + its 1-hop neighbors (others dim heavily)
function focusOn(i){ if(i<0)return;
  if(focusCenter===i){ focusSet=null; focusCenter=-1; renderPanel(); draw(); return; }   // toggle off
  focusCenter=i; focusSet=new Set([i]); nbr[i].forEach(j=>focusSet.add(j));
  if(graphMode==='structural'&&N[i]&&N[i].layer>=0) view=N[i].layer; sel=i; sidebarTab='info'; renderPanel(); center([i],true); draw(); }
window.focusOn=focusOn;
// filter popup: node-type + complexity checkboxes (+ reset), syncing the category chips
const COMPLEX=['simple','moderate','complex'];
function syncCatChips(){ document.querySelectorAll('#catFilters .cat').forEach(b=>{ const c=CATS[+b.dataset.i]; if(c) b.classList.toggle('off', c.t.some(t=>hiddenTypes.has(t))); }); }
function buildFilterMenu(){ const fm=$('filterMenu'); let h='<h5>Node types</h5>';
  for(const t of TY) h+='<label><input type="checkbox" data-ft="type" value="'+esc(t.type)+'"'+(hiddenTypes.has(t.type)?'':' checked')+'><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:'+t.color+'"></span>'+esc(t.type)+' <span class="muted">'+t.count+'</span></label>';
  h+='<h5>Complexity</h5>';
  for(const c of COMPLEX) h+='<label><input type="checkbox" data-ft="complex" value="'+c+'"'+(hiddenComplex.has(c)?'':' checked')+'>'+c+'</label>';
  h+='<button class="bigbtn fm-reset" style="margin-top:12px">Reset filters</button>'; fm.innerHTML=h;
  fm.querySelectorAll('input[data-ft]').forEach(inp=>inp.onchange=()=>{ const set=inp.dataset.ft==='type'?hiddenTypes:hiddenComplex;
    if(inp.checked) set.delete(inp.value); else set.add(inp.value); if(inp.dataset.ft==='type') syncCatChips(); draw(); });
  fm.querySelector('.fm-reset').onclick=()=>{ hiddenComplex.clear(); hiddenTypes.clear(); applyDetail(); buildFilterMenu(); syncCatChips(); draw(); };
}
$('btnFilter').onclick=()=>{ const fm=$('filterMenu'); const show=fm.classList.contains('hidden');
  exMenu.classList.add('hidden'); themeMenu.classList.add('hidden'); if(show) buildFilterMenu(); fm.classList.toggle('hidden'); };
// diff overlay: highlight nodes whose file changed since the last analysis (incremental runs)
function setDiff(on){ if(!hasDiff)return; diffOn=on; const b=$('btnDiff'); if(b){ b.textContent='Diff '+(on?'ON':'OFF'); b.classList.toggle('on',on); } draw(); }
$('btnDiff').onclick=()=>setDiff(!diffOn);
if(!hasDiff){ const b=$('btnDiff'); if(b){ b.style.opacity=0.4; b.title='No changes detected since the last analysis'; } }
$('btnFit').onclick=fitAll;

// zoom buttons (zoom around viewport centre)
function zoomBy(f){ ox=innerWidth/2-(innerWidth/2-ox)*f; oy=innerHeight/2-(innerHeight/2-oy)*f; scale*=f; draw(); }
$('zin').onclick=()=>zoomBy(1.25); $('zout').onclick=()=>zoomBy(0.8);

// persona tabs: Deep Dive (functions on) / Overview (high-level) / Learn (tour)
function setPersona(p, btn){ document.querySelectorAll('.pa').forEach(x=>x.classList.remove('active')); if(btn)btn.classList.add('active');
  if(p==='overview'){ setView('overview'); }
  else if(p==='all'){ showFns=true; detail='class'; applyDetail(); }
  else if(p==='learn'){ startTour(); }
  draw(); }
document.querySelectorAll('.pa').forEach(b=>b.onclick=()=>setPersona(b.dataset.p, b));

// export (PNG of current view, full-graph SVG, or the graph data as JSON)
function dl(blob,name){ const u=URL.createObjectURL(blob),a=document.createElement('a'); a.href=u; a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(u),1500); }
const exMenu=$('exportMenu');
$('btnExport').onclick=()=>exMenu.classList.toggle('hidden');
exMenu.querySelectorAll('button').forEach(b=>b.onclick=()=>{ exMenu.classList.add('hidden'); const x=b.dataset.x, nm=(DATA.project.name||'graph');
  if(x==='png') cv.toBlob(bl=>dl(bl,nm+'.png'));
  else if(x==='json') dl(new Blob([JSON.stringify(DATA,null,2)],{type:'application/json'}),nm+'.json');
  else if(x==='svg') dl(new Blob([buildSVG()],{type:'image/svg+xml'}),nm+'.svg'); });
function buildSVG(){ const bb=bounds(),pad=40,W=(bb[2]-bb[0])+2*pad,H=(bb[3]-bb[1])+2*pad;
  let s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+(bb[0]-pad)+' '+(bb[1]-pad)+' '+W+' '+H+'" font-family="sans-serif">';
  s+='<rect x="'+(bb[0]-pad)+'" y="'+(bb[1]-pad)+'" width="'+W+'" height="'+H+'" fill="'+T.bg+'"/>';
  s+='<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="'+T.muted+'"/></marker></defs>';
  for(const k of CT) s+='<rect x="'+k.x+'" y="'+k.y+'" width="'+k.w+'" height="'+k.h+'" rx="11" fill="'+T.tint+'" stroke="'+k.color+'" stroke-opacity="0.45"/><text x="'+(k.x+12)+'" y="'+(k.y+21)+'" fill="'+k.color+'" font-size="13" font-weight="600">'+esc(k.name)+' ('+k.count+')</text>';
  for(const e of E){ const A=N[e[0]],B=N[e[1]]; s+='<line x1="'+A.x+'" y1="'+A.y+'" x2="'+B.x+'" y2="'+B.y+'" stroke="'+ac(0.4)+'" stroke-opacity="0.7" marker-end="url(#ar)"/>'; }
  for(const n of N){ const x=n.x-cardW/2,y=n.y-cardH/2; s+='<g><rect x="'+x+'" y="'+y+'" width="'+cardW+'" height="'+cardH+'" rx="7" fill="'+T.card+'" stroke="'+ac(0.18)+'"/><rect x="'+x+'" y="'+(y+1)+'" width="4" height="'+(cardH-2)+'" fill="'+n.color+'"/><text x="'+(x+10)+'" y="'+(y+17)+'" fill="'+n.color+'" font-size="9" font-weight="700" font-family="monospace">'+esc(n.type.toUpperCase())+'</text><text x="'+(x+10)+'" y="'+(y+cardH-14)+'" fill="'+T.text+'" font-size="12" font-weight="600">'+esc(n.name.length>26?n.name.slice(0,25)+'…':n.name)+'</text></g>'; }
  return s+'</svg>'; }

// path finder (BFS over the undirected neighbour graph)
function fillSel(s){ s.innerHTML=N.map((n,i)=>'<option value="'+i+'">'+esc(n.name)+' · '+esc(n.type)+'</option>').join(''); }
fillSel($('pathFrom')); fillSel($('pathTo'));
$('btnPath').onclick=()=>$('pathModal').classList.remove('hidden');
window.closePath=()=>$('pathModal').classList.add('hidden');
$('pathClear').onclick=()=>{ pathNodes=null; pathEdges=null; $('pathResult').innerHTML=''; draw(); };
$('pathFind').onclick=()=>{ const a=+$('pathFrom').value, b=+$('pathTo').value;
  const prev=new Array(N.length).fill(-2); prev[a]=-1; const q=[a];
  while(q.length){ const u=q.shift(); if(u===b)break; for(const v of nbr[u]) if(prev[v]===-2){prev[v]=u;q.push(v);} }
  if(prev[b]===-2){ $('pathResult').innerHTML='<div style="color:#fb7185">No path between these nodes.</div>'; pathNodes=null; pathEdges=null; draw(); return; }
  const path=[]; for(let u=b; u!==-1; u=prev[u]) path.unshift(u);
  pathNodes=new Set(path); pathEdges=new Set(); for(let i=0;i+1<path.length;i++) pathEdges.add(path[i]+'_'+path[i+1]);
  let h='<div class="ov-h">'+path.length+' nodes on path</div>';
  path.forEach((i,k)=>{ h+='<div class="step" data-i="'+i+'"><span class="num">'+(k+1)+'</span> '+esc(N[i].name)+' <span class="muted">'+esc(N[i].type)+'</span></div>'; });
  $('pathResult').innerHTML=h;
  $('pathResult').querySelectorAll('.step').forEach(el=>el.onclick=()=>{ closePath(); select(+el.dataset.i); });
  closePath(); center(path,true); draw(); };

$('btnHelp').onclick=()=>$('helpModal').classList.remove('hidden');

// edge-flow animation (marching ants) + domain/structural mode toggle
function startAnim(){ if(_animRunning)return; _animRunning=true; requestAnimationFrame(stepAnim); }
function stepAnim(){ if(!animOn){ _animRunning=false; return; } dashPhase+=0.6; draw(); requestAnimationFrame(stepAnim); }
function setAnim(on){ animOn=on; const b=$('btnAnim'); if(b)b.classList.toggle('on',on); if(on) startAnim(); else draw(); }
$('btnAnim').onclick=()=>setAnim(!animOn);
document.querySelectorAll('#modeSeg button').forEach(b=>b.onclick=()=>setMode(b.dataset.m));
if(!DM.length){ const db=document.querySelector('#modeSeg [data-m="domain"]'); if(db){ db.disabled=true; db.style.opacity=0.4; db.title='No domains detected'; } }

// theme menu (presets + accent swatches + heading font)
const themeMenu=$('themeMenu');
function buildThemeMenu(){ let h='<div class="tm-h">Theme</div>';
  for(const k in THEMES){ const t=THEMES[k];
    h+='<button class="tm-row" data-theme="'+k+'"><span class="tm-sw" style="background:'+t.bg+'"></span><span class="tm-sw" style="background:'+t.card+'"></span><span class="tm-sw" style="background:'+t.accent+'"></span><span class="tm-name">'+t.label+'</span><span class="tm-chk">✓</span></button>'; }
  h+='<div class="tm-h">Accent color</div><div class="tm-acc">';
  for(const a of ACCENTS) h+='<button class="tm-dot" data-acc="'+a+'" style="background:'+a+'"></button>';
  h+='</div><div class="tm-h">Heading font</div><div class="tm-font">';
  for(const f in FONTS) h+='<button class="tm-fbtn" data-font="'+f+'" style="font-family:'+FONTS[f]+'">'+f+'</button>';
  themeMenu.innerHTML=h+'</div>';
  themeMenu.querySelectorAll('[data-theme]').forEach(b=>b.onclick=()=>{ THEME_STATE.name=b.dataset.theme; applyTheme(); refreshThemeMenu(); });
  themeMenu.querySelectorAll('[data-acc]').forEach(b=>b.onclick=()=>{ THEME_STATE.accent=b.dataset.acc; applyTheme(); refreshThemeMenu(); });
  themeMenu.querySelectorAll('[data-font]').forEach(b=>b.onclick=()=>{ THEME_STATE.font=b.dataset.font; applyTheme(); refreshThemeMenu(); }); }
function refreshThemeMenu(){ const acc=THEME_STATE.accent||THEMES[THEME_STATE.name].accent;
  themeMenu.querySelectorAll('[data-theme]').forEach(b=>b.classList.toggle('on', b.dataset.theme===THEME_STATE.name));
  themeMenu.querySelectorAll('[data-acc]').forEach(b=>b.classList.toggle('on', b.dataset.acc.toLowerCase()===acc.toLowerCase()));
  themeMenu.querySelectorAll('[data-font]').forEach(b=>b.classList.toggle('on', b.dataset.font===(THEME_STATE.font||'Serif'))); }
buildThemeMenu();
$('btnTheme').onclick=()=>{ themeMenu.classList.toggle('hidden'); refreshThemeMenu(); };

window.addEventListener('keydown',e=>{
  if(e.target&&e.target.tagName==='INPUT'){ if(e.key==='Escape')e.target.blur(); return; }
  if(e.key==='Escape'){ const fm=$('filterMenu'); const anyOpen=[...document.querySelectorAll('.modal')].some(m=>!m.classList.contains('hidden'))||!exMenu.classList.contains('hidden')||!themeMenu.classList.contains('hidden')||!fm.classList.contains('hidden');
    document.querySelectorAll('.modal').forEach(m=>m.classList.add('hidden')); exMenu.classList.add('hidden'); themeMenu.classList.add('hidden'); fm.classList.add('hidden'); const sr=$('searchResults'); if(sr)sr.style.display='none';
    if(anyOpen){ return; }
    if(focusSet){ focusSet=null; focusCenter=-1; draw(); return; }
    if(sel>=0){ select(-1); }
    else if(tIdx>=0){ endTour(); }
    else if(view!=='overview'){ setView('overview'); }
    pathNodes=null; pathEdges=null; draw(); }
  else if(e.key==='/'){ e.preventDefault(); $('search').focus(); }
  else if(e.key==='f'){ fitAll(); }
  else if(e.key==='p'){ $('pathModal').classList.remove('hidden'); }
  else if(e.key==='e'){ exMenu.classList.toggle('hidden'); }
  else if(e.key==='t'){ themeMenu.classList.toggle('hidden'); refreshThemeMenu(); }
  else if(e.key==='a'){ setAnim(!animOn); }
  else if(e.key==='d'){ setMode(graphMode==='domain'?'structural':'domain'); }
  else if(e.key==='i'){ $('btnFilter').click(); }
  else if(e.key==='x'){ if(sel>=0) focusOn(sel); }
  else if(e.key==='b'){ setDiff(!diffOn); }
  else if(e.key==='?'){ $('helpModal').classList.remove('hidden'); }
  if(tIdx>=0&&e.key==='ArrowRight')$('tnext').click();
  if(tIdx>=0&&e.key==='ArrowLeft')$('tprev').click(); });

window.addEventListener('resize',resize);
try{ const sv=JSON.parse(localStorage.getItem('sl-theme')||'null'); if(sv&&THEMES[sv.name]) THEME_STATE=sv; }catch(e){}
applyTheme(); applyDetail(); applyModeUI(); renderPanel(); fit(); resize(); if(animOn) startAnim();
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
