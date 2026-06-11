"""Smoke tests: schema round-trip, multi-language extraction, and rendering."""

from pathlib import Path
import json
import re

import codeglance
from codeglance.analyze import ts_core as ts
from codeglance.graph import analyze
from codeglance.render import render_interactive, render_static
from codeglance.schema import Edge, KnowledgeGraph, Node, Project

FIXTURES = Path(__file__).parent / "fixtures" / "multilang"
FIXTURES_IMPORTS = Path(__file__).parent / "fixtures" / "imports"
FIXTURES_LEGACY = Path(__file__).parent / "fixtures" / "legacy"
EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_package_version_matches_pyproject():
    root = Path(__file__).resolve().parent.parent
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    assert match
    assert codeglance.__version__ == match.group(1) == "0.0.1"
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "pypi/v/codeglance" not in readme
    assert "pypi-v0.0.1" in readme


def _sample_graph() -> KnowledgeGraph:
    return KnowledgeGraph(
        project=Project(name="demo", languages=["python"]),
        nodes=[
            Node(id="file:a.py", type="file", name="a.py", filePath="a.py", summary="A", tags=["python"]),
            Node(id="function:a.py:f", type="function", name="f", filePath="a.py", summary="fn", tags=["function"]),
        ],
        edges=[Edge(source="file:a.py", target="function:a.py:f", type="contains")],
    )


def test_schema_roundtrip():
    g = _sample_graph()
    g2 = KnowledgeGraph.from_dict(g.to_dict())
    assert g2.to_dict() == g.to_dict()
    assert g2.project.name == "demo"
    issues, _ = g2.validate()
    assert issues == []


def test_render_interactive_is_self_contained():
    html = render_interactive(_sample_graph())
    assert "<canvas" in html
    assert "const DATA = " in html
    assert 'src="http' not in html and 'href="http' not in html  # no external refs


def test_render_interactive_escapes_embedded_json_for_script_parser():
    graph = _sample_graph()
    graph.nodes[1].summary = "uses <!-- comments, <script>, </script>, and Map<String, Order>"
    html = render_interactive(graph)
    match = re.search(r"const DATA = (.*?);\nconst N=", html, re.S)
    assert match
    payload = match.group(1)
    assert "<" not in payload
    assert ">" not in payload
    assert "&" not in payload
    assert "\\u003cscript\\u003e" in payload
    assert "\\u003c/script\\u003e" in payload


def test_render_uses_cards_containers_and_type_colors():
    from codeglance.render import build_view_model, TYPE_COLORS
    vm = build_view_model(_sample_graph())
    assert vm["containers"] and vm["types"] and vm["cardW"] > 0
    fn = next(n for n in vm["nodes"] if n["type"] == "function")
    assert fn["color"] == TYPE_COLORS["function"]  # colored by type, not layer
    html_i = render_interactive(_sample_graph())
    assert "DATA.containers" in html_i and "overviewHTML" in html_i  # containers + project overview
    html_s = render_static(_sample_graph())
    assert "<script" not in html_s and "marker-end" in html_s  # zero-JS + directional edges


def test_interactive_has_toolbar_features():
    html = render_interactive(_sample_graph())
    # export menu, path finder (BFS), syntax highlighter, help, edge labels
    for marker in ("btnExport", "buildSVG", "pathFind", "hl_code", "tok-kw", "helpModal"):
        assert marker in html, f"missing feature: {marker}"


def test_overview_layer_cards_and_drilldown():
    from codeglance.render import build_view_model
    # the template always carries the overview/drill-down machinery
    html = render_interactive(_sample_graph())
    for marker in ("drawOverview", "setView", "pickLayer", "updateCrumb"):
        assert marker in html, f"missing: {marker}"
    assert "click to explore" in html.lower()
    # header chrome moved in from the original: category filters, detail toggle, layer chips, tour list
    for marker in ("catFilters", "layerChips", "detailSeg", "fnToggle", "Start Tour"):
        assert marker in html, f"missing header chrome: {marker}"
    assert 'id="types"' not in html and 'id="legend"' not in html  # left panels removed
    # inspector dropdown + collapsible file tree + panel collapse
    for marker in ("pselect", "filesHTML", "treeHTML", "fdirrow", "extBadge", "togglePanel", 'value="files"'):
        assert marker in html, f"missing sidebar feature: {marker}"
    # a graph WITH layers yields exactly one layer card per layer
    g = analyze(FIXTURES, use_llm=False)
    if g.layers:
        vm = build_view_model(g)
        assert len(vm["layerCards"]) == len(vm["layers"]) >= 1
        assert all("complexity" in c and "x" in c and "description" in c for c in vm["layerCards"])
        assert "layerEdges" in vm


def test_terraform_blocks_extracted():
    if not ts.is_available():
        return
    src = 'resource "aws_instance" "web" {}\nmodule "net" {}\nvariable "r" {}\n'
    names = {s["name"] for s in (ts.extract_symbols("terraform", "m.tf", src) or [])}
    assert "resource aws_instance.web" in names and "module net" in names


def test_terraform_dependency_edges():
    if not ts.is_available():
        return
    g = analyze(FIXTURES_LEGACY, use_llm=False, full=True)  # main.tf has an output referencing a resource
    name = {n.id: n.name for n in g.nodes}
    deps = {(name[e.source], name[e.target]) for e in g.edges if e.type == "depends_on"}
    assert ("output ip", "resource aws_instance.web") in deps


def test_theme_system():
    html = render_interactive(_sample_graph())
    # base colors extracted to CSS variables + a theme engine for canvas + DOM
    for m in ("THEMES", "applyTheme", "readTheme", "btnTheme", "--accent-rgb",
              "var(--bg)", "var(--accent)", "var(--text)", "Dark Ocean", "Light Minimal"):
        assert m in html, f"missing theme piece: {m}"


def test_file_type_icons_inlined():
    from codeglance.render import build_view_model
    from codeglance.render.icons import ICON_SVG, EXT_TO_KEY
    assert ICON_SVG.get("_folder") and ICON_SVG.get("python") and EXT_TO_KEY.get("tf") == "terraform"
    vm = build_view_model(_sample_graph())
    assert "_folder" in vm["iconSvg"] and "_folder_open" in vm["iconSvg"]  # folder glyphs always present
    assert "iconExt" in vm and "iconName" in vm


def test_render_static_has_no_javascript():
    html = render_static(_sample_graph())
    assert "<svg" in html and "</svg>" in html
    assert "<script" not in html  # truly zero-JS


def test_analyze_fixtures_python_only_still_finds_symbols():
    graph = analyze(FIXTURES, use_llm=False)
    kinds = {n.type for n in graph.nodes}
    assert "file" in kinds
    # Python ast path always yields nothing here (no .py in fixtures), but files exist:
    assert len([n for n in graph.nodes if n.type == "file"]) >= 10


def test_treesitter_extraction_when_available():
    if not ts.is_available():
        return  # extra not installed — skip
    graph = analyze(FIXTURES, use_llm=False)
    by_lang_symbols = [n for n in graph.nodes if n.type in ("function", "class")]
    assert len(by_lang_symbols) >= 20
    names = {n.name for n in graph.nodes}
    # representative symbols across languages
    assert "Widget" in names          # app.js class
    assert "UserService" in names     # service.ts class
    assert "NewServer" in names       # main.go func
    assert "Router" in names          # index.php class


def test_rust_impl_methods_attach_to_type():
    if not ts.is_available():
        return
    graph = analyze(FIXTURES, use_llm=False)
    names = {n.name for n in graph.nodes if n.filePath == "lib.rs"}
    assert "Config" in names
    assert "Config.new" in names  # impl method associated with its type, not a free function


def test_cross_language_imports():
    if not ts.is_available():
        return
    graph = analyze(FIXTURES_IMPORTS, use_llm=False)
    pairs = {
        (e.source.split(":", 1)[1], e.target.split(":", 1)[1])
        for e in graph.edges if e.type == "imports"
    }
    assert ("main.go", "store/store.go") in pairs      # Go module
    assert ("Main.java", "util/Helper.java") in pairs  # Java dotted suffix
    assert ("app.cpp", "lib.h") in pairs               # C++ include
    assert ("main.rs", "util.rs") in pairs             # Rust mod / use crate


def test_legacy_and_esoteric_languages():
    if not ts.is_available():
        return
    graph = analyze(FIXTURES_LEGACY, use_llm=False)
    names = {n.name for n in graph.nodes if n.type in ("function", "class")}
    # one representative symbol per language family
    for expected in ("Counter", "increment",  # VHDL
                     "alu", "dbl",             # Verilog
                     "Calc", "Add",            # Ada
                     "Token", "transfer",      # Solidity
                     "Widget", "render",       # Dart
                     "mathmod",                # Fortran
                     "Point", "dist",          # Julia
                     "HELLO"):                 # COBOL
        assert expected in names, f"missing symbol {expected!r}"
    # primitive type names must NOT leak in as symbols
    assert "uint" not in names and "bool" not in names


def test_python_captures_signature_linerange_docstring():
    from codeglance.analyze.languages.python import _python_extract
    _doc, _full, syms, _imp = _python_extract(
        'def f(x: int) -> str:\n    """Doc here."""\n    return str(x)\n'
    )
    assert syms[0]["signature"] == "def f(x: int) -> str"
    assert syms[0]["lineRange"] == [1, 3]
    assert syms[0]["docstring"] == "Doc here."


def test_treesitter_captures_linerange_and_jsdoc():
    if not ts.is_available():
        return
    syms = ts.extract_symbols(
        "javascript", "d.js", "/** Adds two numbers. */\nexport function add(a, b) { return a + b; }\n"
    )
    assert syms and syms[0]["docstring"] == "Adds two numbers."
    assert syms[0]["lineRange"] and syms[0]["signature"].startswith("function add")


def test_incremental_writes_fingerprints():
    from codeglance import fingerprint as fp
    analyze(FIXTURES_IMPORTS, use_llm=False)
    assert fp.load(FIXTURES_IMPORTS)  # fingerprints.json persisted and non-empty


def test_domain_view_built_with_cross_domain_flows():
    from codeglance.render import build_view_model
    # imports fixture has main.go at root + store/store.go + util/Helper.java → 3 domains, 2 flows
    g = analyze(FIXTURES_IMPORTS, use_llm=False, full=True)
    vm = build_view_model(g)
    assert "domains" in vm and "domainEdges" in vm
    assert vm["domains"] and vm["domainCardW"] > 0
    keys = {d["key"] for d in vm["domains"]}
    assert "store" in keys and "util" in keys  # subdirectory domains detected
    for d in vm["domains"]:
        assert {"i", "name", "entities", "nFiles", "flowCount", "x", "y", "members"} <= set(d)
    if ts.is_available():  # imports only resolve with tree-sitter/ast
        assert vm["domainEdges"], "expected cross-domain flows"
        e = vm["domainEdges"][0]
        assert {"a", "b", "label", "count"} <= set(e)


def test_default_theme_is_ocean_and_flow_animation_present():
    html = render_interactive(_sample_graph())
    # Dark Gold is the default — matches the original dashboard's signature accent (first paint + JS state)
    assert "--accent:#5ba4cf" in html and '"defaultTheme": "ocean"' in html  # default theme via view model
    assert "91,164,207" in html  # gold accent rgb on :root
    # marching-ants edge-flow animation + Domain/Structural mode toggle are wired in
    for marker in ("drawCards", "setMode", "modeSeg", "btnAnim", "setAnim",
                   "dashPhase", "lineDashOffset", "DATA.domains", "cardInfoHTML"):
        assert marker in html, f"missing: {marker}"


def test_python_variables_and_constants_extracted():
    from codeglance.analyze.languages.python import _python_extract
    _d, _f, syms, _i = _python_extract(
        "MAX = 10\nname = 'x'\nclass C:\n    field = 1\n    TIMEOUT = 30\n"
        "    def m(self):\n        local = 5\n        return local\n"
    )
    pairs = {(s["name"], s["kind"]) for s in syms}
    assert ("MAX", "constant") in pairs and ("name", "variable") in pairs
    assert "local" not in {s["name"] for s in syms}  # function-local vars are NOT captured
    c = next(s for s in syms if s["name"] == "C")
    fields = {(f["name"], f["kind"]) for f in c.get("fields", [])}
    assert ("field", "variable") in fields and ("TIMEOUT", "constant") in fields


def test_treesitter_top_level_vars_and_consts():
    if not ts.is_available():
        return
    go = {(s["name"], s["kind"]) for s in ts.extract_symbols(
        "go", "m.go", "package main\nconst Pi = 3\nvar count int\nfunc main(){ x:=1; _=x }\n")}
    assert ("Pi", "constant") in go and ("count", "variable") in go
    assert "x" not in {n for n, _ in go}  # function-local not captured
    js = {(s["name"], s["kind"]) for s in ts.extract_symbols(
        "javascript", "m.js", 'const API = 1;\nlet nm = "x";\nfunction go(){ const z = 9; return z; }\n')}
    assert ("API", "constant") in js and "z" not in {n for n, _ in js}


def test_variable_constant_type_colors_present():
    from codeglance.render import TYPE_COLORS
    assert "variable" in TYPE_COLORS and "constant" in TYPE_COLORS


def test_variables_across_more_languages():
    if not ts.is_available():
        return

    def kinds(lang, path, code):
        out = {}
        for s in ts.extract_symbols(lang, path, code) or []:
            if s["kind"] in ("variable", "constant"):
                out[s["name"]] = s["kind"]
            for f in s.get("fields", []):
                out[s["name"] + "." + f["name"]] = f["kind"]
        return out

    java = kinds("java", "A.java", "class A { int count; static final int MAX = 5; }")
    assert java.get("A.count") == "variable" and java.get("A.MAX") == "constant"
    php = kinds("php", "c.php", "<?php const K=1; class C { public $a; const X=2; }")
    assert php.get("K") == "constant" and php.get("C.X") == "constant"
    cs = kinds("csharp", "C.cs", "class C { int n; const int K=1; }")
    assert cs.get("C.n") == "variable" and cs.get("C.K") == "constant"


def test_language_coverage_broad():
    """Every supported family extracts >=1 symbol (tuned, generic, lisp, elixir, cobol, ...)."""
    if not ts.is_available():
        return
    samples = {
        "go": ("m.go", "package m\nfunc F(){}\ntype T struct{}\nvar X=1\n"),
        "rust": ("m.rs", "fn f(){}\nstruct T{}\nconst X:i32=1;\n"),
        "java": ("M.java", "class C{ void m(){} int x; }\n"),
        "csharp": ("C.cs", "class C{ void M(){} }\n"),
        "cpp": ("m.cpp", "class C{ public: void m(){} };\n"),
        "ruby": ("m.rb", "class C\n  def m\n  end\nend\n"),
        "php": ("m.php", "<?php function f(){} class C{}\n"),
        "kotlin": ("M.kt", "fun f(){}\nclass C{ val x=1 }\n"),
        "swift": ("M.swift", "func f(){}\nclass C{ var x=1 }\n"),
        "scala": ("M.scala", "object O{ def f=1 }\n"),
        "lua": ("m.lua", "function f() end\n"),
        "haskell": ("M.hs", "module M where\nf x = x + 1\n"),
        "gleam": ("m.gleam", "pub fn f() { 1 }\n"),
        "perl": ("m.pl", "sub f { return 1; }\n"),
        "zig": ("m.zig", "fn f() void {}\n"),
        "tcl": ("m.tcl", "proc f {x} { return 1 }\n"),
        "ocaml": ("m.ml", "let f x = x + 1\n"),
        "erlang": ("m.erl", "-module(m).\nf() -> ok.\n"),
        "elixir": ("m.ex", "defmodule M do\n  def f, do: 1\nend\n"),
        "clojure": ("m.clj", "(defn f [x] x)\n"),
        "scheme": ("m.scm", "(define (f x) x)\n"),
        "racket": ("m.rkt", "#lang racket\n(define (f x) x)\n"),
        "commonlisp": ("m.lisp", "(defun f (x) x)\n"),
        "fortran": ("m.f90", "module m\ncontains\nsubroutine s()\nend subroutine\nend module\n"),
        "ada": ("p.adb", "procedure P is begin null; end P;\n"),
        "solidity": ("c.sol", "contract C { function f() public {} }\n"),
        "dart": ("m.dart", "class C { void m(){} }\n"),
        "julia": ("m.jl", "function f(x)\n    x\nend\n"),
        "vhdl": ("e.vhd", "architecture a of e is begin end a;\n"),
        "cobol": ("h.cob", "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. HELLO.\n"
                           "       PROCEDURE DIVISION.\n       MAIN-PARA.\n           DISPLAY 'HI'.\n"),
        "terraform": ("m.tf", 'resource "aws_instance" "web" {}\n'),
    }
    failures = [lang for lang, (fn, code) in samples.items()
                if not (ts.extract_symbols(lang, fn, code) or [])]
    assert not failures, f"no symbols extracted for: {failures}"


def test_filter_search_focus_features_present():
    html = render_interactive(_sample_graph())
    # Filter popup, Fuzzy/Semantic search + ranked dropdown, and Focus mode (original-parity)
    for m in ("btnFilter", "filterMenu", "buildFilterMenu", "hiddenComplex",
              "searchResults", "searchMode", "scoreNode", "fuzzySub", "Semantic",
              "focusOn", "fbtn-focus"):
        assert m in html, f"missing parity feature: {m}"


def test_diff_overlay():
    from codeglance.render import build_view_model
    g = _sample_graph()
    g.changed = {"function:a.py:f"}          # mark one node as changed since last analysis
    vm = build_view_model(g)
    assert vm["hasDiff"] is True and len(vm["diffChanged"]) == 1
    # no changes -> no diff
    vm2 = build_view_model(_sample_graph())
    assert vm2["hasDiff"] is False and vm2["diffChanged"] == []
    # template carries the Diff toggle machinery
    html = render_interactive(_sample_graph())
    for m in ("btnDiff", "DIFFC", "diffOn", "setDiff", "DATA.diffChanged"):
        assert m in html, f"missing diff feature: {m}"


def test_knowledge_graph_extraction():
    from codeglance.render import _build_knowledge
    g = KnowledgeGraph(project=Project(name="wiki"), nodes=[
        Node(id="document:a.md", type="document", name="a.md", filePath="a.md"),
        Node(id="document:b.md", type="document", name="b.md", filePath="b.md"),
    ])
    sources = {"a.md": "# Alpha\n\nIntro paragraph. See [[Beta]].\n## Topic One\n",
               "b.md": "# Beta\n\nBody text linking to [the alpha page](a.md).\n"}
    index_of = {n.id: i for i, n in enumerate(g.nodes)}
    k = _build_knowledge(g, sources, index_of)
    assert k and len(k["nodes"]) == 2
    assert {n["name"] for n in k["nodes"]} == {"Alpha", "Beta"}
    pairs = {(k["nodes"][e["a"]]["name"], k["nodes"][e["b"]]["name"], e["type"]) for e in k["edges"]}
    assert ("Alpha", "Beta", "related") in pairs   # [[wikilink]]
    assert ("Beta", "Alpha", "cites") in pairs      # [](a.md) link
    alpha = next(n for n in k["nodes"] if n["name"] == "Alpha")
    assert "Topic One" in alpha["topics"]
    # a single markdown file yields no knowledge graph
    g1 = KnowledgeGraph(project=Project(name="x"),
                        nodes=[Node(id="document:r.md", type="document", name="r.md", filePath="r.md")])
    assert _build_knowledge(g1, {"r.md": "# R\n"}, {"document:r.md": 0}) is None


def test_knowledge_view_markers():
    html = render_interactive(_sample_graph())
    for m in ("CARDSETS", "drawCards", "cardInfoHTML", "cardOverHTML",
              'data-m="knowledge"', "DATA.knowledge"):
        assert m in html, f"missing knowledge feature: {m}"


def test_card_icons_and_deeplink():
    html = render_interactive(_sample_graph())
    # file-type icons rasterized onto the canvas cards + shareable deep-link
    for m in ("ICONIMG", "iconForNode", "drawImage", "setHash", "history.replaceState"):
        assert m in html, f"missing polish feature: {m}"
    # smooth camera fly-to, OS reduced-motion respect, copy-permalink toast
    for m in ("flyTo", "prefers-reduced-motion", "copyLink", "function toast", "@media"):
        assert m in html, f"missing polish feature: {m}"


def test_collapsible_clusters_and_responsive_resize():
    html = render_interactive(_sample_graph())
    # collapsible cluster view (default) + collapse-all + per-header toggle
    for m in ("drawClusters", "drawClusterBox", "pickCluster", "toggleCluster",
              "collapseAllClusters", "CLUSTER_HEAD"):
        assert m in html, f"missing cluster feature: {m}"
    # resize keeps the graph fitted/scaled instead of cropping it
    for m in ("fitMode", "function resize()"):
        assert m in html, f"missing responsive feature: {m}"
    # categorized keyboard-shortcuts modal
    for m in ("Keyboard Shortcuts", "kbcats", "Guided tour"):
        assert m in html, f"missing shortcuts-modal feature: {m}"


def test_interactive_mobile_touch_support():
    html = render_interactive(_sample_graph())
    for m in (
        "viewport-fit=cover",
        "safe-area-inset",
        "touch-action:none",
        "touchstart",
        "touchmove",
        "touchend",
        "tapCanvas",
        "two-finger pinch zoom",
        "58dvh",
        "#tourstart { display:block;",
    ):
        assert m in html, f"missing mobile support marker: {m}"


def test_interactive_toolbar_stays_compact():
    html = render_interactive(_sample_graph())
    for m in (
        "display:grid",
        "grid-template-columns:minmax(150px,max-content) auto auto minmax(300px,1fr) max-content",
        "@media (max-width:1360px) and (min-width:641px)",
        "max-height:82px",
        "body.show-facets #topbar",
        'class="brand"',
        'class="meta"',
        "#searchWrap:focus-within",
        'data-action="facets"',
        "#btnDiff, #detailSeg, #fnToggle, #searchMode",
        "CLUSTER_CONTENT_TOP",
        "typeof v==='number'",
        "applyDetail(false)",
        "max-height:min(230px,32vh)",
        "left:14px",
        "max-height:calc(100vh - var(--topbar-h,44px) - 40px)",
        'id="codeModal"',
        "openCodeModal",
        "source-expand",
        "overflow-x:auto",
        "width:100%; max-width:100%",
        "#topbar .bar::-webkit-scrollbar",
        'id="toolsRail"',
        'id="moreMenu"',
        "tools-collapsed",
        "tools-head",
        "data-tools-close",
        "graphViewport",
        "setToolsCollapsed",
        "refreshMoreControls",
    ):
        assert m in html, f"missing compact toolbar marker: {m}"
    assert 'id="btnMore"' not in html


def test_interactive_tour_hides_minimap():
    html = render_interactive(_sample_graph())
    for m in (
        "body.tour-active #mm",
        "body.tour-active #panel",
        "visibility:hidden",
        "document.body.classList.add('tour-active')",
        "document.body.classList.remove('tour-active')",
        "#tour { position:fixed; right:14px",
    ):
        assert m in html, f"missing tour/minimap layout marker: {m}"


def test_offline_terminal_present():
    html = render_interactive(_sample_graph())
    # in-HTML terminal: graph-query commands + live JS eval, fully offline (no CDN/fetch)
    for m in (
        'id="term"',
        "runTerm",
        "TERM_CMDS",
        "toggleTerm",
        "termOut",
        "btnTerm",
        "openTermHelp",
        "body.term-open #zoom",
        "body.inspector-collapsed #term",
        "right:388px",
    ):
        assert m in html, f"missing terminal feature: {m}"
    # it must stay self-contained — no network calls sneaking in
    assert "pyodide" not in html.lower()
    assert "cdn." not in html.lower()


def test_enums_back_compat_and_str_behaviour():
    from codeglance.enums import NodeType, ThemeName
    from codeglance import schema
    assert NodeType.FILE == "file" and isinstance(NodeType.CLASS, str)   # str-enum
    assert ThemeName.GOLD == "gold"
    # legacy value-sets are derived from the enums (single source of truth)
    assert schema.NODE_TYPES == {t.value for t in NodeType}
    assert schema.COMPLEXITY_VALUES == {"simple", "moderate", "complex"}
    assert "file" in schema.FILE_LEVEL_TYPES   # plain-string membership still works


def test_vizconfig_overrides_flow_into_output():
    from codeglance.config import VizConfig, DEFAULT_CONFIG
    from codeglance.render import build_view_model, render_interactive
    g = _sample_graph()
    vm = build_view_model(g, config=VizConfig(type_colors={"file": "#ff0000"}, card_w=999.0))
    file_node = next(n for n in vm["nodes"] if n["type"] == "file")
    assert file_node["color"] == "#ff0000"          # colour override flows to the node
    assert vm["cardW"] == 999.0                      # dimension override flows through layout
    assert DEFAULT_CONFIG.card_w == 216.0            # default config left intact
    assert "#ff0000" in render_interactive(g, config=VizConfig(type_colors={"file": "#ff0000"}))


def test_wiki_docs_mode_is_self_contained():
    from codeglance.render import render_wiki, _detect_install
    g = analyze(FIXTURES, use_llm=False)
    html = render_wiki(g)
    assert "<html" in html
    assert 'src="http' not in html and 'href="http' not in html      # self-contained / offline
    assert 'id="cg-theme"' in html and 'data-theme="ocean"' in html  # theme switcher, ocean default
    assert html.index("Getting started") < html.index('id="overview"')  # setup leads
    for section in ("Overview", "Getting started", "Reference"):
        assert section in html, f"missing wiki section: {section}"
    repo_root = Path(__file__).resolve().parent.parent
    steps = _detect_install(repo_root)
    assert any("pip install" in s["command"] for s in steps)   # repo has pyproject.toml


def test_context_map_is_dependency_first():
    from codeglance.render import render_context
    g = analyze(FIXTURES_IMPORTS, use_llm=False)   # fixtures with cross-file imports
    md = render_context(g)
    assert "codebase map (AI context)" in md
    assert "## Dependency map" in md and "## Files" in md
    assert "->" in md                               # file -> file dependencies present
    assert "<html" not in md and "<script" not in md  # plain Markdown, not a web page


def test_agent_context_is_low_token_handoff():
    from codeglance.render import render_context

    g = analyze(FIXTURES_IMPORTS, use_llm=False)
    md = render_context(g, mode="agent")
    assert "agent context" in md
    assert "## Snapshot" in md and "## Agent Rules" in md
    assert "## AI Reading Protocol" in md and "## Context Budget" in md
    assert "Open source only after this map points to it" in md
    assert "refresh after edits" in md and "--mode agent" in md
    assert "## Files" not in md  # compact mode omits the full per-file catalog
    assert len(md) < len(render_context(g))
    changed = next(n for n in g.nodes if n.filePath == "main.go")
    g.changed = {changed.id}
    changed_md = render_context(g, mode="agent")
    assert "## Changed Since Last Run" in changed_md and "`main.go`" in changed_md


def test_serve_index_lists_output_artifacts(tmp_path):
    from codeglance.cli import _resolve_serve_dir
    from codeglance.serve import build_index_html, iter_artifacts

    out = tmp_path / "demo"
    out.mkdir()
    (out / "glance.html").write_text("<html></html>", encoding="utf-8")
    (out / "agent.md").write_text("# Agent", encoding="utf-8")
    (out / "knowledge-graph.json").write_text("{}", encoding="utf-8")
    (out / "scratch.py").write_text("print('ignored')", encoding="utf-8")

    artifacts = iter_artifacts(out)
    names = {artifact.path for artifact in artifacts}
    assert names == {"agent.md", "glance.html", "knowledge-graph.json"}

    html = build_index_html(out)
    assert "glance.html" in html and "agent.md" in html and "knowledge-graph.json" in html
    assert "scratch.py" not in html and "/__file__/glance.html" in html

    project = tmp_path / "project"
    generated = project / ".codeglance"
    generated.mkdir(parents=True)
    assert _resolve_serve_dir(str(project)) == generated.resolve()
    assert _resolve_serve_dir(str(project), "demo") == (project / "demo").resolve()
    assert _resolve_serve_dir(str(out)) == out.resolve()


def test_generate_outputs_writes_complete_bundle(tmp_path):
    from codeglance.output import generate_outputs

    project = tmp_path / "project"
    project.mkdir()
    (project / "README.md").write_text("# Demo\n\nSmall project.\n", encoding="utf-8")
    (project / "app.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
    out = tmp_path / "site"

    graph, outputs = generate_outputs(project, out, full=True, profile="all")
    names = {item.path.name for item in outputs}
    expected = {
        "llms.txt",
        "glance.html",
        "graph.static.html",
        "wiki.html",
        "context.md",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    }
    assert expected <= names
    assert graph.nodes
    assert "<canvas" in (out / "glance.html").read_text(encoding="utf-8")
    assert "agent context" in (out / "agent.md").read_text(encoding="utf-8")
    index = (out / "index.html").read_text(encoding="utf-8")
    assert "glance.html" in index and "llm-context.schema.json" in index
    llms = (out / "llms.txt").read_text(encoding="utf-8")
    assert "Read Order" in llms and "`agent.md`" in llms
    assert "`knowledge-graph.toon`" in llms
    toon = (out / "knowledge-graph.toon").read_text(encoding="utf-8")
    assert "nodes[" in toon and "{id,type,name,path,summary,complexity,tags}" in toon
    assert "edges[" in toon and "{source,target,type,weight}" in toon
    schema = json.loads((out / "llm-context.schema.json").read_text(encoding="utf-8"))
    assert schema["schema"] == "codeglance.llm-context"
    assert schema["readOrder"][0] == "llms.txt"
    assert "knowledgeGraphSchema" in schema
    assert "knowledge-graph.toon" in schema["generatedArtifacts"]
    assert "file" in schema["nodeTypes"]
    assert "imports" in schema["edgeTypes"]


def test_generate_outputs_default_profile_is_minimal(tmp_path):
    from codeglance.output import generate_outputs

    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
    out = tmp_path / "site"

    _graph, outputs = generate_outputs(project, out, full=True)
    names = {item.path.name for item in outputs}
    assert names == {
        "llms.txt",
        "glance.html",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    }
    assert (out / "glance.html").is_file()
    assert (out / "agent.md").is_file()
    assert (out / "llms.txt").is_file()
    assert (out / "llm-context.schema.json").is_file()
    assert (out / "knowledge-graph.toon").is_file()
    assert not (out / "wiki.html").exists()
    assert not (out / "context.md").exists()
    assert not (out / "graph.static.html").exists()


def test_generate_outputs_rejects_unknown_profile(tmp_path):
    from codeglance.output import generate_outputs

    project = tmp_path / "project"
    project.mkdir()
    try:
        generate_outputs(project, tmp_path / "out", profile="everything")
    except ValueError as exc:
        assert "unknown output profile" in str(exc)
    else:
        raise AssertionError("generate_outputs should reject an unknown profile")


def test_generate_outputs_rejects_missing_root(tmp_path):
    from codeglance.output import generate_outputs

    missing = tmp_path / "missing"
    try:
        generate_outputs(missing, tmp_path / "out")
    except NotADirectoryError as exc:
        assert str(missing.resolve()) in str(exc)
    else:
        raise AssertionError("generate_outputs should reject a missing root")


def test_generate_accepts_out_alias():
    from codeglance.cli import build_parser

    args = build_parser().parse_args(["generate", ".", "--out", "demo", "--profile", "agent"])
    assert args.output == "demo"
    assert args.profile == "agent"


def test_public_api_and_model_facade():
    import codeglance
    from codeglance.api import analyze_project, render_agent_context, render_html
    from codeglance.models import KnowledgeGraph as PublicKnowledgeGraph

    root = Path("examples/taskman")
    graph = analyze_project(root, full=True)

    assert codeglance.analyze_project is analyze_project
    assert isinstance(graph, PublicKnowledgeGraph)
    assert "<!doctype html>" in render_html(graph, root)
    assert "AI Reading Protocol" in render_agent_context(graph, root, mode="agent")


def test_more_example_projects_are_analyzable():
    examples = {
        "terraform-azure": {
            "languages": {"terraform"},
            "symbols": {"resource azurerm_resource_group.main", "module app"},
            "deps": [("outputs.tf", "main.tf")],
        },
        "rust-cli": {
            "languages": {"rust"},
            "symbols": {"CliConfig", "build_report", "run"},
            "deps": [("src/main.rs", "src/config.rs"), ("src/main.rs", "src/report.rs")],
        },
        "canvas-cli": {
            "languages": {"python"},
            "symbols": {"Canvas", "Shape", "ShapeKind", "render_svg", "main"},
            "deps": [
                ("canvas_cli/cli.py", "canvas_cli/commands.py"),
                ("canvas_cli/renderer.py", "canvas_cli/models.py"),
            ],
        },
        "java-service": {
            "languages": {"java"},
            "symbols": {"App", "OrderService", "InMemoryOrderRepository"},
            "deps": [("src/main/java/com/example/orders/App.java",
                      "src/main/java/com/example/orders/service/OrderService.java")],
        },
    }
    for name, expected in examples.items():
        graph = analyze(EXAMPLES / name, use_llm=False, full=True)
        if expected["languages"]:
            assert expected["languages"] <= set(graph.project.languages), name
        symbols = {node.name for node in graph.nodes}
        assert expected["symbols"] <= symbols, name
        paths = {node.id: node.filePath for node in graph.nodes}
        deps = {(paths[e.source], paths[e.target]) for e in graph.edges if e.type in {"imports", "depends_on"}}
        for pair in expected["deps"]:
            assert pair in deps, f"{name} missing dependency {pair}"


def test_llm_helpers_are_safe_without_api_key(monkeypatch, tmp_path):
    from codeglance.analyze import llm

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm.is_available() is False
    assert llm.availability_hint() == "ANTHROPIC_API_KEY is not set."
    assert llm.enrich(_sample_graph(), root=tmp_path) == 0
    assert llm.name_layers([], []) == 0
    assert llm.narrate_tour([], []) == 0

    prompt = llm._build_prompt(
        "demo",
        [{"id": "file:a.py", "path": "a.py", "current": "old", "head": "def f(): pass"}],
    )
    assert "file:a.py" in prompt and "Return ONLY a JSON object" in prompt
    assert llm._parse_json_object('```json\n{"file:a.py": "A tiny module."}\n```') == {
        "file:a.py": "A tiny module."
    }
    assert llm._parse_json_object("no json here") == {}


def test_default_theme_from_config_and_validate_flags_bad_values():
    from codeglance.render import render_interactive
    from codeglance.config import VizConfig
    g = _sample_graph()
    assert '"defaultTheme": "ocean"' in render_interactive(g)                                  # default
    assert '"defaultTheme": "gold"' in render_interactive(g, config=VizConfig(default_theme="gold"))
    bad = KnowledgeGraph(project=Project(name="x"),
                         nodes=[Node(id="n", type="weird", name="n", summary="s", complexity="huge")])
    issues, warnings = bad.validate()
    assert issues == []                                                                        # not hard errors
    assert any("unknown type" in w for w in warnings)
    assert any("unknown complexity" in w for w in warnings)
