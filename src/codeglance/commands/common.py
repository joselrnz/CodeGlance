"""Shared CLI command helpers."""

from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

from ..render import render_interactive, render_static
from ..schema import FILE_LEVEL_TYPES, KnowledgeGraph

GRAPH_DIR = ".codeglance"
GRAPH_FILE = "knowledge-graph.json"


def emit(msg: str) -> None:
    """Print a message to stderr; stdout stays machine-consumable."""
    print(msg, file=sys.stderr)


def render_to_file(graph: KnowledgeGraph, out: Path, static: bool, root: Path | None = None) -> Path:
    """Render the graph to HTML and write it to `out`."""
    out.parent.mkdir(parents=True, exist_ok=True)
    html = render_static(graph, root) if static else render_interactive(graph, root)
    out.write_text(html, encoding="utf-8")
    return out


def write_meta(root: Path, graph: KnowledgeGraph) -> None:
    """Write graph metadata next to the generated knowledge graph."""
    meta = {
        "lastAnalyzedAt": graph.project.analyzedAt,
        "gitCommitHash": graph.project.gitCommitHash,
        "version": graph.version,
        "analyzedFiles": sum(1 for n in graph.nodes if n.type in FILE_LEVEL_TYPES),
    }
    (root / GRAPH_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def open_html(path: Path, no_open: bool) -> None:
    """Open rendered HTML in a browser, or print the URI when disabled."""
    uri = path.resolve().as_uri()
    if no_open:
        emit(f"  Open it: {uri}")
        return
    try:
        webbrowser.open(uri)
        emit(f"  Opened in your browser: {uri}")
    except Exception:
        emit(f"  Open it manually: {uri}")


def default_html_name(static: bool) -> str:
    """Return the default HTML output filename for static vs. interactive renders."""
    return "knowledge-graph.static.html" if static else "knowledge-graph.html"
