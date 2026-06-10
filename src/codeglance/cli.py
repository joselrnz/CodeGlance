"""Command-line interface for codeglance."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .commands import (
    cmd_analyze,
    cmd_context,
    cmd_dashboard,
    cmd_generate,
    cmd_render,
    cmd_serve,
    cmd_wiki,
    resolve_serve_dir,
)

_SUBCOMMANDS = {"analyze", "render", "dashboard", "wiki", "context", "generate", "serve"}
_resolve_serve_dir = resolve_serve_dir


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
    c.add_argument(
        "--mode",
        choices=("full", "agent"),
        default="full",
        help="context format: full file/symbol map or compact agent handoff",
    )
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
    g.add_argument(
        "--profile",
        choices=("minimal", "human", "agent", "all"),
        default="minimal",
        help="output set: minimal (default), human, agent, or all",
    )
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
    """Parse args, default to `analyze`, and dispatch to a command handler."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    argv = list(sys.argv[1:] if argv is None else argv)
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
