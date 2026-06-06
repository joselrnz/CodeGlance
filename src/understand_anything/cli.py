"""Command-line interface.

    understand [path]                 analyze a project, write the graph, open an HTML view
    understand render <graph.json>    re-render an existing knowledge-graph.json to HTML
    understand dashboard [path]       open the HTML view for a project's existing graph

Flags: --static (zero-JS SVG), --llm (LLM enrichment), -o/--output, --no-open, --graph-only.
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from . import __version__
from .graph import analyze
from .render import render_interactive, render_static
from .schema import KnowledgeGraph

GRAPH_DIR = ".understand-anything"
GRAPH_FILE = "knowledge-graph.json"

# Recognized subcommands; used to make `analyze` the implicit default command.
_SUBCOMMANDS = {"analyze", "render", "dashboard"}


def _emit(msg: str) -> None:
    """Print a message to stderr (stdout is reserved for machine-consumable output)."""
    print(msg, file=sys.stderr)


def _render_to_file(graph: KnowledgeGraph, out: Path, static: bool, root: Path | None = None) -> Path:
    """Render the graph to HTML (static SVG or interactive) and write it to `out`."""
    out.parent.mkdir(parents=True, exist_ok=True)
    html = render_static(graph, root) if static else render_interactive(graph, root)
    out.write_text(html, encoding="utf-8")
    return out


def _write_meta(root: Path, graph: KnowledgeGraph) -> None:
    """Write a small meta.json (last analyzed time, commit, version, file count) next to the graph."""
    import json
    from .schema import FILE_LEVEL_TYPES

    meta = {
        "lastAnalyzedAt": graph.project.analyzedAt,
        "gitCommitHash": graph.project.gitCommitHash,
        "version": graph.version,
        "analyzedFiles": sum(1 for n in graph.nodes if n.type in FILE_LEVEL_TYPES),
    }
    (root / GRAPH_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _open(path: Path, no_open: bool) -> None:
    """Open the rendered HTML in a browser, or just print its URI when `no_open` is set."""
    uri = path.resolve().as_uri()
    if no_open:
        _emit(f"  Open it: {uri}")
        return
    try:
        webbrowser.open(uri)
        _emit(f"  Opened in your browser: {uri}")
    except Exception:
        _emit(f"  Open it manually: {uri}")


def _default_html_name(static: bool) -> str:
    """Return the default HTML output filename for static vs. interactive renders."""
    return "knowledge-graph.static.html" if static else "knowledge-graph.html"


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle the `analyze` subcommand: analyze a project, save the graph, render HTML. Returns an exit code."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        _emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze(root, use_llm=args.llm, model=args.model, progress=_emit, full=args.full)

    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph.save(graph_path)
    _write_meta(root, graph)
    stats = graph.stats()
    issues, warnings = graph.validate()
    _emit("")
    _emit(f"✓ {graph.project.name}: {stats['nodes']} nodes, {stats['edges']} edges, "
          f"{stats['layers']} layers, {stats['tourSteps']} tour steps")
    _emit(f"  Graph: {graph_path}")
    if issues:
        _emit(f"  ⚠ {len(issues)} validation issue(s) (graph still saved).")

    if args.graph_only:
        return 0

    out = Path(args.output) if args.output else root / GRAPH_DIR / _default_html_name(args.static)
    _render_to_file(graph, out, args.static, root)
    _emit(f"  HTML : {out}")
    _open(out, args.no_open)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Handle the `render` subcommand: re-render an existing knowledge-graph.json to HTML. Returns an exit code."""
    graph_path = Path(args.graph).resolve()
    if not graph_path.is_file():
        _emit(f"Error: file not found: {graph_path}")
        return 1
    graph = KnowledgeGraph.load(graph_path)
    # graph lives at <root>/.understand-anything/knowledge-graph.json → root is two levels up
    root = graph_path.parent.parent if graph_path.parent.name == GRAPH_DIR else None
    out = Path(args.output) if args.output else graph_path.with_name(_default_html_name(args.static))
    _render_to_file(graph, out, args.static, root)
    _emit(f"✓ Rendered {graph_path.name} → {out}")
    _emit(f"  {len(graph.nodes)} nodes · {len(graph.edges)} edges · {len(graph.layers)} layers")
    _open(out, args.no_open)
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Handle the `dashboard` subcommand: render and open a project's existing graph. Returns an exit code."""
    root = Path(args.path).resolve()
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    if not graph_path.is_file():
        _emit(f"No knowledge graph found at {graph_path}.\nRun `understand {root}` first to analyze this project.")
        return 1
    graph = KnowledgeGraph.load(graph_path)
    out = Path(args.output) if args.output else root / GRAPH_DIR / _default_html_name(args.static)
    _render_to_file(graph, out, args.static, root)
    _emit(f"✓ {graph.project.name} → {out}")
    _open(out, args.no_open)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser with the analyze/render/dashboard subcommands and flags."""
    p = argparse.ArgumentParser(
        prog="understand",
        description="Turn a codebase into an interactive knowledge-graph HTML file (pure Python).",
    )
    p.add_argument("--version", action="version", version=f"understand-anything-py {__version__}")
    sub = p.add_subparsers(dest="command")

    a = sub.add_parser("analyze", help="analyze a project and render an HTML graph")
    a.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    a.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    a.add_argument("--model", default=None, help="LLM model id (default: claude-sonnet-4-6)")
    a.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    a.add_argument("-o", "--output", default=None, help="HTML output path")
    a.add_argument("--no-open", action="store_true", help="do not open the browser")
    a.add_argument("--graph-only", action="store_true", help="only write knowledge-graph.json, no HTML")
    a.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    a.set_defaults(func=cmd_analyze)

    r = sub.add_parser("render", help="render an existing knowledge-graph.json to HTML")
    r.add_argument("graph", help="path to knowledge-graph.json")
    r.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    r.add_argument("-o", "--output", default=None, help="HTML output path")
    r.add_argument("--no-open", action="store_true", help="do not open the browser")
    r.set_defaults(func=cmd_render)

    d = sub.add_parser("dashboard", help="open the HTML view for a project's existing graph")
    d.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    d.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    d.add_argument("-o", "--output", default=None, help="HTML output path")
    d.add_argument("--no-open", action="store_true", help="do not open the browser")
    d.set_defaults(func=cmd_dashboard)

    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: parse args (defaulting to `analyze`) and dispatch. Returns an exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    # Make `analyze` the default command: `understand .` == `understand analyze .`
    if argv and argv[0] not in _SUBCOMMANDS and argv[0] not in ("-h", "--help", "--version"):
        argv = ["analyze", *argv]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
