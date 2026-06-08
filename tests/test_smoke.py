"""Smoke tests: schema round-trip, multi-language extraction, and rendering."""

from pathlib import Path

from scopinglang.analyze import treesitter as ts
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
    from scopinglang.analyze.structural import _python_extract
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
    for marker in ("drawDomain", "setMode", "modeSeg", "btnAnim", "setAnim",
                   "dashPhase", "lineDashOffset", "DATA.domains", "domainInfoHTML"):
        assert marker in html, f"missing: {marker}"


def test_python_variables_and_constants_extracted():
    from scopinglang.analyze.structural import _python_extract
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
