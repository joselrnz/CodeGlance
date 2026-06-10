"""Command-line interface.

    codeglance [path]                 analyze a project, write the graph, open an HTML view
    codeglance render <graph.json>    re-render an existing knowledge-graph.json to HTML
    codeglance dashboard [path]       open the HTML view for a project's existing graph
    codeglance generate [path]        generate all human/agent outputs into one folder
    codeglance serve [path]           host generated HTML/Markdown/JSON outputs locally

Flags: --static (zero-JS SVG), --llm (LLM enrichment), -o/--output/--out, --no-open, --graph-only.
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

GRAPH_DIR = ".codeglance"
GRAPH_FILE = "knowledge-graph.json"

# Recognized subcommands; used to make `analyze` the implicit default command.
_SUBCOMMANDS = {"analyze", "render", "dashboard", "wiki", "context", "generate", "serve"}


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
    # graph lives at <root>/.codeglance/knowledge-graph.json → root is two levels up
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
        _emit(f"No knowledge graph found at {graph_path}.\nRun `codeglance {root}` first to analyze this project.")
        return 1
    graph = KnowledgeGraph.load(graph_path)
    out = Path(args.output) if args.output else root / GRAPH_DIR / _default_html_name(args.static)
    _render_to_file(graph, out, args.static, root)
    _emit(f"✓ {graph.project.name} → {out}")
    _open(out, args.no_open)
    return 0


def cmd_wiki(args: argparse.Namespace) -> int:
    """Handle the `wiki` subcommand: generate a readable docs/wiki HTML page. Returns an exit code."""
    from .render import render_wiki

    root = Path(args.path).resolve()
    if not root.is_dir():
        _emit(f"Error: not a directory: {root}")
        return 1
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph = analyze(root, use_llm=args.llm, model=args.model, progress=_emit, full=args.full)
    graph.save(graph_path)
    _write_meta(root, graph)
    out = Path(args.output) if args.output else root / GRAPH_DIR / "wiki.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_wiki(graph, root), encoding="utf-8")
    _emit(f"✓ {graph.project.name} wiki → {out}")
    _open(out, args.no_open)
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    """Handle the `context` subcommand: emit a compact AI-context codebase map. Returns an exit code."""
    from .render import render_context

    root = Path(args.path).resolve()
    if not root.is_dir():
        _emit(f"Error: not a directory: {root}")
        return 1
    graph_path = root / GRAPH_DIR / GRAPH_FILE
    graph = analyze(root, use_llm=args.llm, model=args.model, progress=_emit, full=args.full)
    graph.save(graph_path)
    _write_meta(root, graph)
    mode = "agent" if args.brief else args.mode
    md = render_context(graph, root, mode=mode)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        _emit(f"✓ context map → {args.output}")
    else:
        print(md)  # stdout: machine-consumable for agents / skills
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Handle the `generate` subcommand: write the full output bundle from one analysis pass."""
    from .output import generate_outputs, mirror_to_codeglance
    from .serve import serve_directory

    root = Path(args.path).resolve()
    if not root.is_dir():
        _emit(f"Error: not a directory: {root}")
        return 1
    out = Path(args.output).resolve() if args.output else root / GRAPH_DIR / "outputs"
    graph, outputs = generate_outputs(
        root,
        out,
        use_llm=args.llm,
        model=args.model,
        full=args.full,
        profile=args.profile,
        progress=_emit,
    )
    mirror_to_codeglance(root, outputs)
    stats = graph.stats()
    _emit("")
    _emit(f"✓ generated {len(outputs)} {args.profile} outputs for {graph.project.name}")
    _emit(f"  {stats['nodes']} nodes · {stats['edges']} edges · {stats['layers']} layers")
    _emit(f"  Output folder: {out}")
    if any(item.path.name == "index.html" for item in outputs):
        _emit(f"  Index: {out / 'index.html'}")
    if args.serve:
        serve_directory(out, host=args.host, port=args.port, open_browser=args.open)
    return 0


def _resolve_serve_dir(path: str, output_dir: str | None = None) -> Path:
    """Resolve the folder that `serve` should host."""
    base = Path(path).resolve()
    if output_dir:
        out = Path(output_dir)
        return out.resolve() if out.is_absolute() else (base / out).resolve()
    if (base / GRAPH_DIR).is_dir() and not any(base.glob("*.html")):
        return (base / GRAPH_DIR).resolve()
    return base


def cmd_serve(args: argparse.Namespace) -> int:
    """Handle the `serve` subcommand: host generated output artifacts from a local folder."""
    from .serve import serve_directory

    serve_dir = _resolve_serve_dir(args.path, args.dir)
    if not serve_dir.is_dir():
        _emit(f"Error: output folder not found: {serve_dir}")
        _emit("Run `codeglance generate .` first, or pass an existing folder such as `demo`.")
        return 1
    serve_directory(serve_dir, host=args.host, port=args.port, open_browser=args.open)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser with all subcommands and flags."""
    p = argparse.ArgumentParser(
        prog="codeglance",
        description="Turn a codebase into an interactive knowledge-graph HTML file (pure Python).",
    )
    p.add_argument("--version", action="version", version=f"codeglance {__version__}")
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

    w = sub.add_parser("wiki", help="generate a readable docs/wiki HTML page (non-graphical)")
    w.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    w.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    w.add_argument("--model", default=None, help="LLM model id")
    w.add_argument("-o", "--output", default=None, help="HTML output path")
    w.add_argument("--no-open", action="store_true", help="do not open the browser")
    w.add_argument("--full", action="store_true", help="re-analyze even if a graph already exists")
    w.set_defaults(func=cmd_wiki)

    c = sub.add_parser("context", help="print a compact dependency+summary codebase map (for AI agents)")
    c.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    c.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    c.add_argument("--model", default=None, help="LLM model id")
    c.add_argument("--mode", choices=("full", "agent"), default="full",
                   help="context format: full file/symbol map or compact agent handoff")
    c.add_argument("--brief", action="store_true", help="alias for --mode agent")
    c.add_argument("-o", "--output", default=None, help="write to a file instead of stdout")
    c.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    c.set_defaults(func=cmd_context)

    g = sub.add_parser("generate", help="generate graph, wiki, context, JSON, and an output index")
    g.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    g.add_argument("-o", "--output", "--out", default=None, help="output folder (default: .codeglance/outputs)")
    g.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    g.add_argument("--model", default=None, help="LLM model id")
    g.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    g.add_argument("--profile", choices=("minimal", "human", "agent", "all"), default="minimal",
                   help="output set: minimal (default), human, agent, or all")
    g.add_argument("--serve", action="store_true", help="serve the output folder after generation")
    g.add_argument("--host", default="127.0.0.1", help="serve host when --serve is used")
    g.add_argument("--port", type=int, default=8765, help="serve port when --serve is used")
    g.add_argument("--open", action="store_true", help="open the generated output index when serving")
    g.set_defaults(func=cmd_generate)

    s = sub.add_parser("serve", help="host generated HTML/Markdown/JSON outputs locally")
    s.add_argument("path", nargs="?", default=".", help="project or output directory (default: .)")
    s.add_argument("--dir", default=None, help="output directory relative to path, e.g. demo or .codeglance")
    s.add_argument("--host", default="127.0.0.1", help="bind host (use 0.0.0.0 for phone access)")
    s.add_argument("--port", type=int, default=8765, help="port to bind (default: 8765)")
    s.add_argument("--open", action="store_true", help="open the local index in a browser")
    s.set_defaults(func=cmd_serve)

    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: parse args (defaulting to `analyze`) and dispatch. Returns an exit code."""
    for stream in (sys.stdout, sys.stderr):  # ensure UTF-8 output (Windows consoles default to cp1252)
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    argv = list(sys.argv[1:] if argv is None else argv)
    # Make `analyze` the default command: `codeglance .` == `codeglance analyze .`
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
