"""Explain, impact, and onboarding CLI workflows."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..api import analyze_project, explain_target, render_impact_report, render_onboarding_guide
from .common import GRAPH_DIR, GRAPH_FILE, emit, write_meta


def cmd_explain(args: argparse.Namespace) -> int:
    """Explain one file, symbol, or graph node."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    try:
        md = explain_target(graph, args.target, root)
    except ValueError as exc:
        emit(f"Error: {exc}")
        return 1
    return _write_or_print(md, args.output, "explain report")


def cmd_impact(args: argparse.Namespace) -> int:
    """Generate a changed-file impact report."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    md = render_impact_report(graph, root)
    return _write_or_print(md, args.output, "impact report")


def cmd_onboard(args: argparse.Namespace) -> int:
    """Generate a human-friendly onboarding guide."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    md = render_onboarding_guide(graph, root)
    return _write_or_print(md, args.output, "onboarding guide")


def _write_or_print(markdown: str, output: str | None, label: str) -> int:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        emit(f"✓ {label} → {path}")
    else:
        print(markdown)
    return 0
