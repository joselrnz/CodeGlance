"""Smoke tests: schema round-trip, multi-language extraction, and rendering."""

from pathlib import Path

from scopinglang.analyze import ts_core as ts
from scopinglang.graph import analyze
from scopinglang.render import render_interactive, render_static
from scopinglang.schema import Edge, KnowledgeGraph, Node, Project

FIXTURES = Path(__file__).parent / "fixtures" / "multilang"
FIXTURES_IMPORTS = Path(__file__).parent / "fixtures" / "imports"
FIXTURES_LEGACY = Path(__file__).parent / "fixtures" / "legacy"


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


def test_render_uses_cards_containers_and_type_colors():
    from scopinglang.render import build_view_model, TYPE_COLORS
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
    from scopinglang.render import build_view_model
    # the template always carries the overview/drill-down machinery
    html = render_interactive(_sample_graph())
    for marker in ("drawOverview", "setView", "pickLayer", "updateCrumb"):
        assert marker in html, f"missing: {marker}"
    assert "click to explore" in html.lower()
    # header chrome moved in from the original: category filters, detail toggle, layer chips, tour list
    for marker in ("catFilters", "layerChips", "detailSeg", "fnToggle", "Start Tour"):
        assert marker in html, f"missing header chrome: {marker}"
    assert 'id="types"' not in html and 'id="legend"' not in html  # left panels removed
    # sidebar Info/Files tabs + collapsible file tree + panel collapse
    for marker in ("ptab", "filesHTML", "treeHTML", "fdirrow", "extBadge", "togglePanel", 'data-tab="files"'):
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
    from scopinglang.render import build_view_model
    from scopinglang.render.icons import ICON_SVG, EXT_TO_KEY
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
    from scopinglang.analyze.languages.python import _python_extract
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
    from scopinglang import fingerprint as fp
    analyze(FIXTURES_IMPORTS, use_llm=False)
    assert fp.load(FIXTURES_IMPORTS)  # fingerprints.json persisted and non-empty


def test_domain_view_built_with_cross_domain_flows():
    from scopinglang.render import build_view_model
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
    # Dark Ocean is the default (first paint + JS state)
    assert "--accent:#5ba4cf" in html and "name:'ocean'" in html
    # marching-ants edge-flow animation + Domain/Structural mode toggle are wired in
    for marker in ("drawCards", "setMode", "modeSeg", "btnAnim", "setAnim",
                   "dashPhase", "lineDashOffset", "DATA.domains", "cardInfoHTML"):
        assert marker in html, f"missing: {marker}"


def test_python_variables_and_constants_extracted():
    from scopinglang.analyze.languages.python import _python_extract
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
    from scopinglang.render import TYPE_COLORS
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
    from scopinglang.render import build_view_model
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
    from scopinglang.render import _build_knowledge
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
