"""CSS for the self-contained interactive graph template."""

from __future__ import annotations

STYLE = r'''
  :root { color-scheme: dark; --bg:#0a0e14; --surface:#1b2530; --elevated:#1b2530; --card:#1a222c; --code-bg:#0b0f15; --text:#e8edf2; --text2:#87939f; --muted:#536b7a; --accent:#5ba4cf; --accent-rgb:91,164,207; --tint:rgba(255,255,255,0.02); --font-heading:Georgia,"Times New Roman",serif; --tools-w:286px; --tools-rail-w:46px; }
  * { box-sizing: border-box; }
  html,body { margin:0; height:100%; overflow:hidden; overscroll-behavior:none; background:var(--bg); color:var(--text);
    -webkit-text-size-adjust:100%; font-family: ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  #cv { display:block; position:fixed; inset:0; touch-action:none; }
  .card { background:rgba(20,20,20,0.94); border:1px solid rgba(var(--accent-rgb),0.14); border-radius:12px;
    backdrop-filter: blur(6px); box-shadow:0 10px 34px rgba(0,0,0,0.45); }
  #topbar { position:fixed; top:14px; left:14px; right:14px; display:grid;
    grid-template-columns:minmax(188px,240px) auto auto minmax(260px,1fr) max-content;
    grid-auto-rows:minmax(38px,auto); align-items:center; gap:8px 14px; padding:13px 14px 12px;
    z-index:5; max-height:92px; overflow:hidden; }
  body.show-facets #topbar { max-height:132px; }
  #topbar .brand { grid-column:1; min-width:0; max-width:240px; display:flex; flex-direction:column; justify-content:center; gap:4px; line-height:1.22; overflow:hidden; }
  #topbar .title { display:block; min-width:0; font-weight:700; font-size:16px; line-height:1.28; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; padding-bottom:1px; }
  #topbar .meta { display:block; color:var(--muted); font-size:10px; line-height:1.35; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%; }
  #topbar .sub { color:var(--text2); font-size:12px; white-space:nowrap; }
  #search { flex:1; min-width:0; background:transparent; border:none; color:var(--text);
    padding:7px 5px; border-radius:8px; font-size:13px; outline:none; }
  #searchWrap:focus-within { border-color:rgba(var(--accent-rgb),0.62); box-shadow:0 0 0 3px rgba(var(--accent-rgb),0.10); }
  #topbar .hint { color:var(--muted); font-size:11px; white-space:nowrap; }
  .leg { position:fixed; left:14px; max-width:230px; overflow:auto; padding:10px 12px; z-index:5; font-size:12px; }
  #types { top:104px; max-height:34vh; } #legend { bottom:14px; max-height:40vh; }
  #crumb { position:fixed; top:calc(20px + var(--topbar-h,44px)); left:calc(var(--tools-w) + 34px); right:388px; z-index:12;
    display:flex; align-items:center; gap:6px; min-height:38px; max-width:calc(100vw - var(--tools-w) - 430px);
    padding:5px 8px; font-size:11px; font-weight:600; color:var(--text2); overflow-x:auto; scrollbar-width:none; }
  #crumb::-webkit-scrollbar { display:none; }
  body.tools-collapsed #crumb { left:calc(var(--tools-rail-w) + 30px); }
  body.inspector-collapsed #crumb { right:58px; max-width:calc(100vw - var(--tools-w) - 100px); }
  #crumb button { flex:0 0 auto; min-height:28px; background:rgba(var(--accent-rgb),0.08); border:1px solid rgba(var(--accent-rgb),0.22);
    color:var(--accent); padding:5px 9px; border-radius:8px; font:inherit; line-height:1; cursor:pointer; touch-action:manipulation; white-space:nowrap; }
  #crumb button:hover { background:rgba(var(--accent-rgb),0.18); border-color:rgba(var(--accent-rgb),0.48); }
  #crumb .crumb-sep { flex:0 0 auto; color:var(--muted); }
  #crumb .crumb-note { flex:0 0 auto; color:var(--muted); font-weight:400; text-transform:none; letter-spacing:0; white-space:nowrap; }
  #crumb .crumb-full { flex:0 0 auto; max-width:360px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
    color:var(--text2); background:rgba(var(--accent-rgb),0.05); border:1px solid rgba(var(--accent-rgb),0.12); border-radius:8px; padding:6px 9px; font-weight:500; }
  .leg h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }
  .lg { display:flex; align-items:center; gap:8px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  .lg:hover { background:var(--elevated); } .lg.off { opacity:.4; }
  .sw { width:11px; height:11px; border-radius:3px; flex:none; }
  .lg .nm { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .lg .ct { color:var(--muted); }
  #panel { position:fixed; right:14px; top:calc(22px + var(--topbar-h,44px)); width:min(360px,calc(100vw - 28px)); max-height:calc(100vh - var(--topbar-h,44px) - 40px); overflow:auto;
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
  .code { background:var(--code-bg); border:1px solid rgba(var(--accent-rgb),0.14); border-radius:8px; overflow:auto; max-height:min(230px,32vh);
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:11px; line-height:1.5; }
  .code table.ct { border-collapse:collapse; width:100%; }
  .code td.ln { user-select:none; text-align:right; color:#5c5145; padding:0 9px; width:1%; white-space:nowrap;
    border-right:1px solid rgba(var(--accent-rgb),0.14); }
  .code td.lc { padding:0 10px; white-space:pre; color:var(--text); }
  .code tr.hl { background:rgba(var(--accent-rgb),0.14); } .code tr.hl td.ln { color:var(--accent); }
  #tip { position:fixed; pointer-events:none; z-index:9; width:min(420px, calc(100vw - 28px)); max-width:420px; padding:10px 12px; font-size:12px; display:none; overflow-wrap:anywhere; }
  #tip .tn{font-weight:700;line-height:1.25} #tip .tt{color:var(--text2);font-size:11px;line-height:1.35;margin-top:2px} #tip .ts{color:var(--text);margin-top:6px;line-height:1.45}
  #mm { position:fixed; right:14px; bottom:14px; width:210px; height:140px; z-index:5; padding:0; cursor:crosshair;
    transition:opacity .16s ease, transform .16s ease; }
  body.tour-active #mm { opacity:0; visibility:hidden; pointer-events:none; transform:translateY(8px); }
  #tour { position:fixed; left:calc(var(--tools-w) + 34px); right:388px; bottom:14px; width:auto; max-width:560px;
    margin:0 auto; padding:14px 16px; z-index:7; }
  body.tools-collapsed #tour { left:calc(var(--tools-rail-w) + 30px); }
  body.inspector-collapsed #tour { right:58px; }
  #tour h4 { margin:0 0 4px; font-size:14px; } #tour .desc { font-size:13px; color:var(--text); line-height:1.5; margin:6px 0 12px; }
  .tourbtns { display:flex; gap:8px; align-items:center; }
  button { background:var(--elevated); color:var(--text); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:8px; padding:6px 12px; font-size:12px; cursor:pointer; }
  button:hover { background:rgba(var(--accent-rgb),0.28); } #tcount { flex:1; text-align:center; color:var(--text2); font-size:12px; }
  #tourstart { position:fixed; right:240px; bottom:14px; z-index:5; }
  #topbar .bar { grid-column:5; justify-self:stretch; display:flex; gap:6px; min-width:0; justify-content:flex-end;
    width:100%; max-width:100%; overflow-x:auto; scrollbar-width:none; }
  #topbar .bar::-webkit-scrollbar { display:none; }
  #topbar .bar button { padding:5px 9px; font-size:11px; }
  #topbar .bar button.on { color:var(--accent); border-color:rgba(var(--accent-rgb),0.5); background:rgba(var(--accent-rgb),0.12); }
  #btnHelp { display:none; }
  #btnDiff, #detailSeg, #fnToggle, #searchMode,
  #btnFit, #btnPath, #btnFilter, #btnExport, #btnAnim, #btnTheme, #btnTerm { display:none; }
  #exportMenu { position:fixed; top:calc(16px + var(--topbar-h,44px)); right:14px; z-index:8; display:flex; flex-direction:column; padding:6px; gap:2px; min-width:130px; }
  #filterMenu { position:fixed; top:calc(16px + var(--topbar-h,44px)); right:14px; z-index:9; width:240px; max-height:78vh; overflow:auto; padding:12px; }
  #filterMenu h5 { margin:11px 2px 5px; font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }
  #filterMenu h5:first-child { margin-top:0; }
  #filterMenu label { display:flex; align-items:center; gap:7px; font-size:12px; padding:3px 4px; border-radius:6px; cursor:pointer; }
  #filterMenu label:hover { background:var(--elevated); } #filterMenu input { accent-color:var(--accent); }
  #searchWrap { position:relative; display:grid; grid-template-columns:auto minmax(130px,1fr) auto; align-items:center; gap:6px; flex:none;
    background:rgba(8,12,18,0.82); border:1px solid rgba(var(--accent-rgb),0.24); border-radius:10px; padding:0 6px; }
  #searchWrap::before { content:"⌕"; color:var(--muted); font-size:14px; line-height:1; padding-left:2px; }
  .smode { display:flex; background:var(--elevated); border-radius:7px; padding:2px; }
  .smode button { border:none; background:transparent; color:var(--text2); font-size:10px; padding:3px 7px; border-radius:5px; cursor:pointer; }
  .smode button.on { background:rgba(var(--accent-rgb),0.2); color:var(--accent); }
  #moreMenu { position:fixed; top:calc(22px + var(--topbar-h,44px)); left:14px; right:auto; z-index:6; width:var(--tools-w);
    max-height:calc(100vh - var(--topbar-h,44px) - 40px); overflow:auto; padding:12px; }
  #moreMenu .tools-head { display:flex; align-items:center; justify-content:space-between; gap:10px; margin:0 0 10px; padding-bottom:8px;
    border-bottom:1px solid rgba(var(--accent-rgb),0.16); color:var(--text); font-size:12px; font-weight:700; letter-spacing:.02em; }
  #moreMenu .tools-head button { width:28px; min-width:28px; height:28px; padding:0; border-radius:8px; font-size:14px; }
  #moreMenu h5 { margin:8px 0 5px; color:var(--text2); font-size:10px; text-transform:uppercase; letter-spacing:.06em; }
  #moreMenu h5:first-of-type { margin-top:0; }
  #moreMenu .mrow { display:grid; grid-template-columns:1fr 1fr; gap:5px; margin-bottom:7px; }
  #moreMenu button { min-width:0; padding:5px 8px; font-size:11px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #moreMenu button.on { color:var(--accent); border-color:rgba(var(--accent-rgb),0.5); background:rgba(var(--accent-rgb),0.16); }
  #toolsRail { position:fixed; left:14px; top:calc(22px + var(--topbar-h,44px)); z-index:7; display:none; width:var(--tools-rail-w);
    height:104px; padding:0; align-items:center; justify-content:center; writing-mode:vertical-rl; transform:rotate(180deg);
    font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
  body.tools-collapsed #toolsRail { display:flex; }
  body.tools-collapsed #moreMenu { display:none !important; }
  #searchResults { position:fixed; z-index:9; width:330px; max-height:300px; overflow:auto; padding:6px; display:none; }
  #searchResults .sr { display:flex; align-items:center; gap:8px; padding:5px 7px; border-radius:6px; cursor:pointer; }
  #searchResults .sr:hover { background:var(--elevated); }
  #searchResults .srb { font-size:9px; text-transform:uppercase; border:1px solid; border-radius:3px; padding:1px 4px; flex:none; }
  #searchResults .srn { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #searchResults .srbar { width:46px; height:5px; background:var(--bg); border-radius:3px; overflow:hidden; flex:none; }
  #searchResults .srbar>span { display:block; height:100%; background:var(--accent); }
  #panel .fbtn-focus { position:absolute; top:9px; right:34px; font-size:10px; padding:3px 8px; }
  #panel .fbtn-focus.on { color:var(--accent); border-color:var(--accent); background:rgba(var(--accent-rgb),0.16); }
  /* node-action row — sits below the tabs (no more absolute buttons overlapping the FILES tab) */
  .pacts { display:flex; align-items:center; gap:6px; margin:2px 0 12px; }
  .source-head { display:flex; align-items:center; gap:8px; }
  .source-head span { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .source-head .pact { margin:0; text-transform:none; letter-spacing:0; }
  .source-head a.pact { text-decoration:none; display:inline-flex; align-items:center; gap:4px; }
  .editor-open { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; min-width:32px; justify-content:center; }
  .editor-open svg { width:13px; height:13px; flex:0 0 13px; display:block; }
  .vscode-mark { color:#22a7f2; }
  .cursor-mark { color:#f4f7fb; }
  .pact { font-size:10px; padding:4px 9px; border:1px solid rgba(var(--accent-rgb),0.28); background:var(--card); color:var(--text2); border-radius:7px; cursor:pointer; }
  .pact:hover { color:var(--text); border-color:rgba(var(--accent-rgb),0.5); }
  .pact.on { color:var(--accent); border-color:var(--accent); background:rgba(var(--accent-rgb),0.16); }
  #toast { position:fixed; left:50%; bottom:24px; transform:translateX(-50%) translateY(12px); padding:9px 16px; font-size:13px; z-index:30; opacity:0; pointer-events:none; transition:opacity .2s, transform .2s; }
  #toast.show { opacity:1; transform:translateX(-50%) translateY(0); }
  #btnReload.stale { color:var(--accent); border-color:rgba(var(--accent-rgb),0.72); background:rgba(var(--accent-rgb),0.18); box-shadow:0 0 0 1px rgba(var(--accent-rgb),0.18) inset; }
  #btnReload.stale::after { content:""; width:6px; height:6px; margin-left:6px; border-radius:50%; background:var(--accent); display:inline-block; vertical-align:middle; box-shadow:0 0 10px rgba(var(--accent-rgb),0.8); }
  /* responsive: progressively shed non-essential header controls as the window narrows */
  @media (max-width:1360px){ #layerChips { display:none; } }
  @media (max-width:1160px){ #catFilters { display:none; } }
  @media (max-width:860px){ #mm { width:150px; height:100px; } }
  @media (hover:none) and (pointer:coarse){
    button, .pa, .cat, .chip, .ptab, .pact, .tm-row, .tm-fbtn { min-height:36px; }
    #topbar .bar button { min-width:38px; }
  }
  @media (max-width:640px){
    #topbar { display:grid; top:max(8px,env(safe-area-inset-top)); left:max(8px,env(safe-area-inset-left)); right:max(8px,env(safe-area-inset-right));
      grid-template-columns:minmax(0,1fr) auto; grid-auto-rows:auto; align-items:center; gap:7px; padding:10px 10px; max-height:116px; overflow:hidden; }
    body.show-facets #topbar { max-height:202px; overflow:auto; }
    #topbar .brand { grid-column:1; min-width:0; max-width:none; }
    #topbar .title { min-width:0; overflow:hidden; text-overflow:ellipsis; font-size:15px; line-height:1.28; }
    #topbar .meta { max-width:none; font-size:9px; line-height:1.35; }
    #topbar .personas, #modeSeg { display:none; }
    #topbar .bar { grid-column:2; width:auto; min-width:0; margin-left:0; overflow:visible; scrollbar-width:none; padding-bottom:0; }
    #topbar .bar::-webkit-scrollbar { display:none; }
    #topbar .bar button { flex:0 0 auto; }
    #topbar #search, #topbar #searchWrap { grid-column:1 / -1; grid-row:2; width:auto; }
    #topbar .cats { grid-column:1 / -1; grid-row:3; width:100%; }
    #topbar .chips { grid-column:1 / -1; grid-row:4; width:100%; }
    #btnDiff, #detailSeg, #fnToggle, #searchMode,
    #btnFit, #btnPath, #btnFilter, #btnExport, #btnAnim, #btnTheme, #btnTerm { display:none; }
    #topbar .bar { justify-content:flex-end; overflow:visible; }
    #topbar .grow { display:none; }
    #crumb, #mm { display:none; }
    #zoom { bottom:max(10px,env(safe-area-inset-bottom)); }
    body.term-open #zoom { bottom:calc(min(48dvh,340px) + max(18px,env(safe-area-inset-bottom))); }
    #tourstart { display:block; top:calc(max(8px,env(safe-area-inset-top)) + var(--topbar-h,44px) + 8px);
      right:max(8px,env(safe-area-inset-right)); bottom:auto; }
    #panel { left:max(8px,env(safe-area-inset-left)); right:max(8px,env(safe-area-inset-right)); width:auto; top:auto;
      bottom:max(8px,env(safe-area-inset-bottom)); max-height:58dvh; padding:20px 14px 14px; border-radius:14px 14px 10px 10px; }
    #panel::before { content:""; position:absolute; top:7px; left:50%; transform:translateX(-50%); width:42px; height:4px;
      border-radius:999px; background:rgba(var(--accent-rgb),0.32); }
    #panel.collapsed { transform:translateY(120%); }
    #panelReopen { top:auto; right:max(8px,env(safe-area-inset-right)); bottom:max(10px,env(safe-area-inset-bottom));
      border-radius:999px; padding:10px 12px; }
    #filterMenu, #themeMenu, #exportMenu, #moreMenu, #searchResults { left:max(8px,env(safe-area-inset-left)) !important;
      right:max(8px,env(safe-area-inset-right)) !important; width:auto !important; max-height:48dvh; }
    #filterMenu, #themeMenu, #exportMenu, #moreMenu { top:calc(max(8px,env(safe-area-inset-top)) + var(--topbar-h,44px) + 8px); }
    #toolsRail { display:flex; left:max(8px,env(safe-area-inset-left)); top:calc(max(8px,env(safe-area-inset-top)) + var(--topbar-h,44px) + 8px);
      width:auto; height:36px; padding:0 12px; writing-mode:horizontal-tb; transform:none; border-radius:999px; }
    body:not(.tools-collapsed) #toolsRail { display:none; }
    #tour { left:max(8px,env(safe-area-inset-left)); right:max(8px,env(safe-area-inset-right)); bottom:max(8px,env(safe-area-inset-bottom));
      width:auto; max-height:44dvh; overflow:auto; }
    #term { left:max(8px,env(safe-area-inset-left)); right:max(8px,env(safe-area-inset-right)); bottom:max(8px,env(safe-area-inset-bottom));
      width:auto; height:min(48dvh,340px); }
    .code { max-height:24dvh; }
    .modal { align-items:flex-end; padding:8px; }
    .modal .mbox { width:100%; max-width:100%; max-height:82dvh; border-radius:14px 14px 10px 10px; }
  }
  #exportMenu button { text-align:left; }
  .modal { position:fixed; inset:0; background:rgba(0,0,0,0.55); z-index:20; display:flex; align-items:center; justify-content:center; }
  .modal .mbox { width:440px; max-width:92vw; max-height:80vh; overflow:auto; padding:18px; position:relative; }
  .modal .close { position:absolute; top:12px; right:14px; cursor:pointer; color:var(--muted); font-size:16px; z-index:2; }
  .modal .close:hover { color:var(--text); }
  .modal h4 { margin:0 0 12px; font-size:15px; }
  .modal select { width:100%; margin:5px 0; background:var(--bg); color:var(--text); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:6px; padding:7px; font-size:12px; }
  #codeModal .mbox { width:min(1120px,94vw); height:min(82vh,760px); max-height:86vh; display:flex; flex-direction:column; overflow:hidden; }
  #codeModal h4 { padding-right:26px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #codeBody { flex:1; min-height:0; display:flex; }
  #codeModal .code { flex:1; max-height:none; width:100%; }
  #pathResult { margin-top:12px; font-size:12px; }
  #pathResult .step { display:flex; align-items:center; gap:8px; padding:4px 6px; border-radius:6px; cursor:pointer; }
  #pathResult .step:hover { background:var(--elevated); } #pathResult .num { color:var(--bg); background:var(--accent); border-radius:99px; width:18px; height:18px; display:inline-flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; }
  .kb { display:grid; grid-template-columns:auto 1fr; gap:7px 14px; font-size:12px; align-items:center; }
  .kb kbd, .kbfoot kbd { font-family:ui-monospace,monospace; background:var(--bg); border:1px solid rgba(var(--accent-rgb),0.28); border-radius:4px; padding:1px 7px; color:var(--accent); justify-self:start; white-space:nowrap; }
  .kbsub { color:var(--text2); font-size:12px; margin:-4px 0 16px; }
  .kbcats { display:grid; grid-template-columns:1fr 1fr; gap:18px 30px; }
  .kbcat h5 { margin:0 0 9px; font-size:10px; text-transform:uppercase; letter-spacing:.07em; color:var(--accent); }
  .kbfoot { margin-top:18px; padding-top:12px; border-top:1px solid rgba(var(--accent-rgb),0.14); text-align:center; color:var(--muted); font-size:11px; }
  @media (max-width:560px){ .kbcats { grid-template-columns:1fr; } }
  .tok-cm{color:#6b7f8e;font-style:italic} .tok-st{color:#c9a06c} .tok-nu{color:#d19a66} .tok-kw{color:#c084fc}
  .title, #panel h3, .ov-title, .modal h4, #tour h4 { font-family:var(--font-heading); font-weight:400; letter-spacing:.2px; }
  #topbar .personas { grid-column:2; display:flex; gap:2px; flex:none; }
  .pa { background:transparent; border:1px solid transparent; color:var(--text2); padding:4px 9px; font-size:11px; border-radius:7px; cursor:pointer; }
  .pa:hover { color:var(--text); } .pa.active { color:var(--accent); background:rgba(var(--accent-rgb),0.1); border-color:rgba(var(--accent-rgb),0.3); }
  #zoom { position:fixed; left:50%; bottom:24px; transform:translateX(-50%); display:flex; gap:6px; z-index:6; }
  body.term-open #zoom { bottom:calc(min(42vh,320px) + 38px); }
  body.tour-active #zoom { bottom:150px; }
  body.term-open.tour-active #zoom { bottom:calc(min(42vh,320px) + 38px); }
  #zoom button { width:32px; height:32px; font-size:16px; padding:0; }
  #termFab { position:fixed; left:14px; bottom:24px; z-index:7; width:42px; height:42px; padding:0; border-radius:12px;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; font-weight:700; }
  #termFab.on { color:var(--accent); border-color:rgba(var(--accent-rgb),0.62); background:rgba(var(--accent-rgb),0.18); }
  #topbar .grow { display:none; }
  #topbar #search { flex:none; width:100%; }
  #modeSeg { grid-column:3; }
  #detailSeg { grid-column:5; }
  #btnDiff { grid-column:4; }
  #fnToggle { grid-column:6; }
  #searchWrap { grid-column:4; min-width:0; width:100%; }
  #topbar .bar { grid-column:5; }
  .seg { display:flex; background:var(--elevated); border-radius:8px; padding:2px; flex:none; gap:2px; }
  .seg button { padding:4px 9px; font-size:11px; border:none; background:transparent; color:var(--text2); border-radius:6px; }
  .seg button.on { background:rgba(var(--accent-rgb),0.2); color:var(--accent); }
  .fnbtn { flex:none; font-size:10px; text-transform:uppercase; letter-spacing:.05em; padding:4px 8px;
    border:1px solid rgba(var(--accent-rgb),0.28); background:var(--card); color:var(--text2); border-radius:6px; }
  .fnbtn.on { border-color:#d19a66; background:rgba(209,154,102,0.12); color:#e0a96a; }
  .cats { grid-column:1 / span 5; grid-row:2; display:flex; gap:4px; min-width:0; overflow-x:auto; scrollbar-width:none;
    padding:1px 0 2px; }
  .cats::-webkit-scrollbar { display:none; }
  .cat { display:flex; align-items:center; gap:5px; font-size:10px; text-transform:uppercase; letter-spacing:.04em;
    padding:4px 7px; border:1px solid rgba(var(--accent-rgb),0.18); border-radius:6px; background:var(--card); color:var(--text2);
    cursor:pointer; white-space:nowrap; } .cat:hover{color:var(--text);} .cat.off{opacity:.35;}
  .cat .d, .chip .d { width:8px; height:8px; border-radius:99px; flex:none; }
  .chips { grid-column:6 / -1; grid-row:2; display:flex; gap:10px; min-width:0; overflow-x:auto; scrollbar-width:none;
    align-items:center; padding:1px 0 2px; }
  .chips::-webkit-scrollbar { display:none; }
  .chip { display:flex; align-items:center; gap:5px; font-size:11px; color:var(--text2); cursor:pointer; white-space:nowrap; }
  .chip:hover{color:var(--text);} .chip.dim{opacity:.4;} .chip.active{color:var(--text);font-weight:600;}
  .chip .muted{color:var(--muted);margin-left:1px;}
  #topbar .cats, #topbar .chips { display:none; }
  body.show-facets #topbar .cats, body.show-facets #topbar .chips { display:flex; }
  @media (max-width:1360px) and (min-width:641px){
    #topbar { grid-template-columns:minmax(176px,220px) auto auto minmax(220px,1fr) max-content; }
    #btnDiff, #detailSeg, #fnToggle, #searchMode,
    #btnFit, #btnPath, #btnFilter, #btnExport, #btnAnim, #btnTheme, #btnTerm { display:none; }
    #searchWrap { grid-column:4 !important; }
    #topbar .bar { grid-column:5 !important; max-width:100%; overflow:visible; justify-content:flex-end; }
  }
  @media (max-width:1100px) and (min-width:641px){
    #topbar { grid-template-columns:minmax(156px,190px) auto auto minmax(180px,1fr) max-content; }
    #topbar .title { font-size:15px; }
    #topbar .meta { font-size:9px; }
    #topbar .bar { overflow:visible; justify-content:flex-end; }
  }
  .bigbtn { width:100%; background:rgba(var(--accent-rgb),0.1); border:1px solid rgba(var(--accent-rgb),0.3); color:var(--accent);
    padding:9px; border-radius:8px; margin:6px 0 10px; cursor:pointer; font-size:13px; }
  .bigbtn:hover{ background:rgba(var(--accent-rgb),0.2); }
  .tstep { font-size:12px; padding:6px 9px; background:var(--card); border:1px solid rgba(var(--accent-rgb),0.12);
    border-radius:7px; margin:4px 0; cursor:pointer; color:var(--text); }
  .tstep:hover{ border-color:rgba(var(--accent-rgb),0.4); } .tstep .tn{ color:var(--accent); font-family:ui-monospace,monospace; }
  .ptabs { display:flex; gap:8px; align-items:center; margin:0 0 12px; border-bottom:1px solid rgba(var(--accent-rgb),0.14); padding-bottom:8px; }
  .pselect { flex:1; min-width:0; background:var(--elevated); color:var(--text); border:1px solid rgba(var(--accent-rgb),0.24);
    border-radius:7px; padding:6px 8px; font-size:12px; outline:none; }
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
  #themeMenu { position:fixed; top:calc(16px + var(--topbar-h,44px)); right:14px; z-index:9; width:236px; max-height:82vh; overflow:auto; padding:10px; }
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
  /* offline terminal: graph queries + live JS, all against the embedded data */
  #term { position:fixed; left:calc(var(--tools-w) + 34px); right:388px; bottom:14px; width:auto; height:min(42vh,320px);
    z-index:8; display:flex; flex-direction:column; padding:0; overflow:hidden;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  body.tools-collapsed #term { left:calc(var(--tools-rail-w) + 30px); }
  body.inspector-collapsed #term { right:58px; }
  #term .thead { display:flex; align-items:center; gap:8px; padding:7px 12px; font-size:11px; color:var(--text2);
    border-bottom:1px solid rgba(var(--accent-rgb),0.18); }
  #term .thead .tt { color:var(--accent); font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
  #term .tclose { cursor:pointer; color:var(--muted); margin-left:auto; } #term .tclose:hover { color:var(--text); }
  #termOut { flex:1; overflow:auto; padding:8px 12px; font-size:12px; line-height:1.55; }
  #termOut>div { white-space:pre-wrap; word-break:break-word; }
  #term .tin { display:flex; align-items:center; gap:8px; padding:7px 12px; border-top:1px solid rgba(var(--accent-rgb),0.18); }
  #term .tin .pr { color:var(--accent); } #term .tin input { flex:1; background:transparent; border:none; outline:none; color:var(--text); font:inherit; }
  .ln-cmd { color:var(--text); } .ln-cmd .pr { color:var(--accent); } .ln-out { color:var(--text2); }
  .ln-err { color:#fb7185; } .ln-ok { color:#5fb389; } .ln-node { cursor:pointer; } .ln-node:hover { color:var(--accent); }
  @media (max-width:640px){
    #topbar .personas, #modeSeg { display:none !important; }
    #zoom { left:50%; right:auto; bottom:max(10px,env(safe-area-inset-bottom)); transform:translateX(-50%); display:flex; }
    body.term-open #zoom { bottom:calc(min(48dvh,340px) + max(18px,env(safe-area-inset-bottom))); }
    body.tour-active #zoom { bottom:calc(44dvh + max(18px,env(safe-area-inset-bottom))); }
    body.term-open.tour-active #zoom { bottom:calc(max(min(48dvh,340px),44dvh) + max(18px,env(safe-area-inset-bottom))); }
    #termFab { left:max(8px,env(safe-area-inset-left)); bottom:max(10px,env(safe-area-inset-bottom)); }
    #panelReopen { top:auto; right:max(8px,env(safe-area-inset-right)); bottom:max(10px,env(safe-area-inset-bottom));
      height:auto; border-radius:999px; padding:10px 12px; }
  }
  .hidden { display:none !important; }
'''
