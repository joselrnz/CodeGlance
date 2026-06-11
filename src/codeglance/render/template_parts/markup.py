"""HTML shell fragments for the self-contained interactive graph."""

from __future__ import annotations

HTML_OPEN = r'''<!doctype html>
<html lang="en">
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
    <button class="pa active" data-p="overview" title="High-level architecture — one card per layer">Overview</button>
    <button class="pa" data-p="drill" title="Drill into files and classes without function noise">Drill</button>
    <button class="pa" data-p="all" title="Full engineer view — files, classes, functions, variables, and constants">Explore</button>
    <button class="pa" data-p="learn" title="Guided step-by-step tour">Tour</button>
  </span>
  <span class="seg" id="modeSeg">
    <button data-m="structural" class="on" title="Code structure graph">Structural</button>
    <button data-m="domain" title="Business domain map">Domain</button>
    <button data-m="knowledge" title="Knowledge graph (docs / wiki)">Knowledge</button>
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
    <button id="btnTerm" title="Terminal — query the graph + run JS, offline (~)">&gt;_ Term</button>
    <button id="btnHelp" title="Shortcuts (?)">?</button>
  </span>
</div>
<div id="themeMenu" class="card hidden"></div>
<button id="toolsRail" class="card" title="Show tools">Tools</button>
<div id="moreMenu" class="card hidden">
  <div class="tools-head"><span>Tools</span><button data-tools-close title="Hide tools">‹</button></div>
  <h5 class="mobile-only">View</h5>
  <div class="mrow mobile-only">
    <button data-persona="overview">Overview</button>
    <button data-persona="drill">Drill</button>
    <button data-persona="all">Explore</button>
    <button data-persona="learn">Tour</button>
  </div>
  <h5 class="mobile-only">Map</h5>
  <div class="mrow mobile-only">
    <button data-mode="structural">Structural</button>
    <button data-mode="domain">Domain</button>
    <button data-mode="knowledge">Knowledge</button>
  </div>
  <h5>Analysis</h5>
  <div class="mrow">
    <button data-mirror="btnDiff">Diff</button>
    <button data-mirror="fnToggle">Functions</button>
    <button data-action="facets">Facets</button>
  </div>
  <h5>Detail</h5>
  <div class="mrow">
    <button data-detail="file">Files</button>
    <button data-detail="class">+Classes</button>
  </div>
  <h5>Search</h5>
  <div class="mrow">
    <button data-search-mode="fuzzy">Fuzzy</button>
    <button data-search-mode="semantic">Semantic</button>
  </div>
  <h5>Actions</h5>
  <div class="mrow">
    <button data-mirror="btnFit">Fit</button>
    <button data-mirror="btnPath">Path</button>
    <button data-mirror="btnFilter">Filter</button>
    <button data-mirror="btnExport">Export</button>
    <button data-mirror="btnAnim">Flow</button>
    <button data-mirror="btnTheme">Theme</button>
    <button data-mirror="btnTerm">Term</button>
    <button data-mirror="btnHelp">Help</button>
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
