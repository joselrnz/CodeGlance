"""HTML shell fragments for the self-contained interactive graph."""

from __future__ import annotations

HTML_OPEN = r'''<!doctype html>
<html lang="__HTML_LANG__" dir="__HTML_DIR__">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>__TITLE__</title>
<style>'''

HTML_BODY = r'''</style>
</head>
<body>
<canvas id="cv"></canvas>
<div id="topbar" class="card">
  <span class="brand"><span class="title">__PROJECT_NAME__</span><span class="meta">__SUBTITLE__</span></span>
  <span class="personas">
    <button class="pa active" data-p="overview" title="High-level architecture — one card per layer">__NAV_OVERVIEW__</button>
    <button class="pa" data-p="drill" title="Drill into files and classes without function noise">__NAV_DRILL__</button>
    <button class="pa" data-p="all" title="Full engineer view — files, classes, functions, variables, and constants">__NAV_EXPLORE__</button>
    <button class="pa" data-p="learn" title="Guided step-by-step tour">__NAV_TOUR__</button>
  </span>
  <span class="seg" id="modeSeg">
    <button data-m="structural" class="on" title="Code structure graph">__MAP_STRUCTURAL__</button>
    <button data-m="domain" title="Business domain map">__MAP_DOMAIN__</button>
    <button data-m="knowledge" title="Knowledge graph (docs / wiki)">__MAP_KNOWLEDGE__</button>
  </span>
  <button id="btnDiff" class="fnbtn" title="Diff: highlight files changed since last analysis (b)">Diff OFF</button>
  <span class="seg" id="detailSeg">
    <button data-d="file" title="Files only — architecture-level">Files</button>
    <button data-d="class" class="on" title="Files + Classes">+Classes</button>
  </span>
  <button id="fnToggle" class="fnbtn" title="Toggle functions, variables & constants">fn</button>
  <span id="searchWrap">
    <input id="search" placeholder="__SEARCH_NODES__" autocomplete="off"/>
    <span class="smode" id="searchMode"><button data-m="fuzzy" class="on" title="Fuzzy text match">__SEARCH_FUZZY__</button><button data-m="semantic" title="Keyword-relevance ranking (offline, no embeddings)">__SEARCH_SEMANTIC__</button></span>
  </span>
  <span id="catFilters" class="cats"></span>
  <span id="layerChips" class="chips"></span>
  <span class="grow"></span>
  <span class="bar">
    <button id="btnFit" title="Fit to view (f)">⤢ __ACTION_FIT__</button>
    <button id="btnPath" title="Path finder (p)">↦ __ACTION_PATH__</button>
    <button id="btnFilter" title="Filter (i)">⛂ __ACTION_FILTER__</button>
    <button id="btnExport" title="Export (e)">⬇ __ACTION_EXPORT__</button>
    <button id="btnAnim" class="on" title="Toggle edge flow animation (a)">≈ __ACTION_FLOW__</button>
    <button id="btnTheme" title="Theme (t)">◑ __ACTION_THEME__</button>
    <button id="btnTerm" title="Terminal — query the graph + run JS, offline (~)">&gt;_ Term</button>
    <button id="btnReload" title="Reload this HTML while keeping the current selection">↻ __ACTION_REFRESH__</button>
    <button id="btnHelp" title="Shortcuts (?)">?</button>
  </span>
</div>
<div id="themeMenu" class="card hidden"></div>
<button id="toolsRail" class="card" title="Show tools">__LABEL_TOOLS__</button>
<div id="moreMenu" class="card hidden">
  <div class="tools-head"><span>__LABEL_TOOLS__</span><button data-tools-close title="Hide tools">‹</button></div>
  <h5 class="mobile-only">View</h5>
  <div class="mrow mobile-only">
    <button data-persona="overview">__NAV_OVERVIEW__</button>
    <button data-persona="drill">__NAV_DRILL__</button>
    <button data-persona="all">__NAV_EXPLORE__</button>
    <button data-persona="learn">__NAV_TOUR__</button>
  </div>
  <h5 class="mobile-only">Map</h5>
  <div class="mrow mobile-only">
    <button data-mode="structural">__MAP_STRUCTURAL__</button>
    <button data-mode="domain">__MAP_DOMAIN__</button>
    <button data-mode="knowledge">__MAP_KNOWLEDGE__</button>
  </div>
  <h5>__LABEL_ANALYSIS__</h5>
  <div class="mrow">
    <button data-mirror="btnDiff">__ACTION_DIFF__</button>
    <button data-mirror="fnToggle">__ACTION_FUNCTIONS__</button>
    <button data-action="facets">__ACTION_FACETS__</button>
  </div>
  <h5>__LABEL_DETAIL__</h5>
  <div class="mrow">
    <button data-detail="file">__DETAIL_FILES__</button>
    <button data-detail="class">__DETAIL_CLASSES__</button>
  </div>
  <h5>__LABEL_SEARCH__</h5>
  <div class="mrow">
    <button data-search-mode="fuzzy">__SEARCH_FUZZY__</button>
    <button data-search-mode="semantic">__SEARCH_SEMANTIC__</button>
  </div>
  <h5>__LABEL_ACTIONS__</h5>
  <div class="mrow">
    <button data-mirror="btnFit">__ACTION_FIT__</button>
    <button data-mirror="btnPath">__ACTION_PATH__</button>
    <button data-mirror="btnFilter">__ACTION_FILTER__</button>
    <button data-mirror="btnExport">__ACTION_EXPORT__</button>
    <button data-mirror="btnAnim">__ACTION_FLOW__</button>
    <button data-mirror="btnTheme">__ACTION_THEME__</button>
    <button data-mirror="btnTerm">Term</button>
    <button data-mirror="btnReload">__ACTION_REFRESH__</button>
    <button data-mirror="btnHelp">__ACTION_HELP__</button>
  </div>
</div>
<div id="crumb" class="card"></div>
<div id="zoom" class="">
  <button id="zin" class="card" title="Zoom in">+</button>
  <button id="zout" class="card" title="Zoom out">−</button>
</div>
<button id="termFab" class="card" title="Open terminal">&gt;_</button>
<div id="panel" class="card"></div>
<button id="panelReopen" class="card hidden" title="Show inspector">‹ Inspector</button>
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
<div id="codeModal" class="modal hidden"><div class="mbox card">
  <span class="close" onclick="closeCodeModal()">✕</span><h4 id="codeTitle">Source</h4><div id="codeBody"></div>
</div></div>
<div id="term" class="card hidden">
  <div class="thead"><span class="tt">terminal</span><span>· graph queries + JS · 100% offline · type <b>help</b></span><span class="tclose" onclick="toggleTerm(false)">✕</span></div>
  <div id="termOut"></div>
  <div class="tin"><span class="pr">›</span><input id="termIn" autocomplete="off" spellcheck="false" placeholder="help"/></div>
</div>
<div id="helpModal" class="modal hidden"><div class="mbox card" style="width:600px">
  <span class="close" onclick="document.getElementById('helpModal').classList.add('hidden')">✕</span>
  <h4>Keyboard Shortcuts</h4>
  <div class="kbsub">Drive the whole graph from the keyboard — no mouse required.</div>
  <div class="kbcats">
    <div class="kbcat"><h5>General</h5><div class="kb">
      <kbd>/</kbd><span>Focus search</span>
      <kbd>i</kbd><span>Filter panel</span>
      <kbd>e</kbd><span>Export menu</span>
      <kbd>t</kbd><span>Theme menu</span>
      <kbd>~</kbd><span>Terminal (queries + JS)</span>
      <kbd>?</kbd><span>Toggle this help</span>
      <kbd>Esc</kbd><span>Close panel / menu</span>
    </div></div>
    <div class="kbcat"><h5>Navigation</h5><div class="kb">
      <kbd>f</kbd><span>Fit graph to view</span>
      <kbd>0</kbd><span>Reset &amp; fit</span>
      <kbd>+ −</kbd><span>Zoom in / out</span>
      <kbd>← ↑ → ↓</kbd><span>Pan the canvas</span>
      <kbd>p</kbd><span>Path finder</span>
      <kbd>x</kbd><span>Focus node + neighbors</span>
    </div></div>
    <div class="kbcat"><h5>View modes</h5><div class="kb">
      <kbd>d</kbd><span>Domain ⇄ Structural</span>
      <kbd>k</kbd><span>Knowledge ⇄ Structural</span>
      <kbd>b</kbd><span>Diff overlay</span>
      <kbd>a</kbd><span>Edge-flow animation</span>
      <kbd>c</kbd><span>Collapse / expand all clusters</span>
    </div></div>
    <div class="kbcat"><h5>Guided tour</h5><div class="kb">
      <kbd>← →</kbd><span>Previous / next step</span>
      <kbd>Esc</kbd><span>Exit the tour</span>
    </div></div>
  </div>
  <div class="kbfoot">Press <kbd>Esc</kbd> or click outside to close</div>
</div></div>
<script>'''

HTML_CLOSE = r'''</script>
</body>
</html>'''
