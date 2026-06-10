"""Analyze, render, dashboard, wiki, and context CLI commands."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..api import analyze_project
from ..render import render_context, render_wiki
from ..schema import KnowledgeGraph
from .common import GRAPH_DIR, GRAPH_FILE, default_html_name, emit, open_html, render_to_file, write_meta


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze a project, save the graph, and render HTML."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)

    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph.save(graph_path)
    write_meta(root, graph)
    stats = graph.stats()
    issues, _warnings = graph.validate()
    emit("")
    emit(
        f"✓ {graph.project.name}: {stats['nodes']} nodes, {stats['edges']} edges, "
        f"{stats['layers']} layers, {stats['tourSteps']} tour steps"
    )
    emit(f"  Graph: {graph_path}")
    if issues:
        emit(f"  ⚠ {len(issues)} validation issue(s) (graph still saved).")

    if args.graph_only:
        return 0

    out = Path(args.output) if args.output else root / GRAPH_DIR / default_html_name(args.static)
    render_to_file(graph, out, args.static, root)
    emit(f"  HTML : {out}")
    open_html(out, args.no_open)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Re-render an existing `knowledge-graph.json` to HTML."""
    graph_path = Path(args.graph).resolve()
    if not graph_path.is_file():
        emit(f"Error: file not found: {graph_path}")
        return 1
    graph = KnowledgeGraph.load(graph_path)
    root = graph_path.parent.parent if graph_path.parent.name == GRAPH_DIR else None
    out = Path(args.output) if args.output else graph_path.with_name(default_html_name(args.static))
    render_to_file(graph, out, args.static, root)
    emit(f"✓ Rendered {graph_path.name} → {out}")
    emit(f"  {len(graph.nodes)} nodes · {len(graph.edges)} edges · {len(graph.layers)} layers")
    open_html(out, args.no_open)
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Render and open a project's existing graph."""
    root = Path(args.path).resolve()
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    if not graph_path.is_file():
        emit(f"No knowledge graph found at {graph_path}.\nRun `codeglance {root}` first to analyze this project.")
        return 1
    graph = KnowledgeGraph.load(graph_path)
    out = Path(args.output) if args.output else root / GRAPH_DIR / default_html_name(args.static)
    render_to_file(graph, out, args.static, root)
    emit(f"✓ {graph.project.name} → {out}")
    open_html(out, args.no_open)
    return 0


def cmd_wiki(args: argparse.Namespace) -> int:
    """Generate a readable docs/wiki HTML page."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(graph_path)
    write_meta(root, graph)
    out = Path(args.output) if args.output else root / GRAPH_DIR / "wiki.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_wiki(graph, root), encoding="utf-8")
    emit(f"✓ {graph.project.name} wiki → {out}")
    open_html(out, args.no_open)
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    """Emit a compact AI-context codebase map."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(graph_path)
    write_meta(root, graph)
    mode = "agent" if args.brief else args.mode
    md = render_context(graph, root, mode=mode)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        emit(f"✓ context map → {args.output}")
    else:
        print(md)
    return 0
