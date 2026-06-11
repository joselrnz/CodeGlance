"""Argument parser construction for the codeglance CLI."""

from __future__ import annotations

import argparse

from .. import __version__
from ..commands import (
    cmd_analyze,
    cmd_context,
    cmd_dashboard,
    cmd_explain,
    cmd_generate,
    cmd_impact,
    cmd_onboard,
    cmd_render,
    cmd_serve,
    cmd_wiki,
)

SUBCOMMANDS = {
    "analyze",
    "render",
    "dashboard",
    "wiki",
    "context",
    "generate",
    "serve",
    "explain",
    "impact",
    "onboard",
}


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser with all subcommands and flags."""
    parser = argparse.ArgumentParser(
        prog="codeglance",
        description="Turn a codebase into an interactive knowledge-graph HTML file (pure Python).",
    )
    parser.add_argument("--version", action="version", version=f"codeglance {__version__}")
    subcommands = parser.add_subparsers(dest="command")

    _add_analyze_parser(subcommands)
    _add_render_parser(subcommands)
    _add_dashboard_parser(subcommands)
    _add_wiki_parser(subcommands)
    _add_context_parser(subcommands)
    _add_explain_parser(subcommands)
    _add_impact_parser(subcommands)
    _add_onboard_parser(subcommands)
    _add_generate_parser(subcommands)
    _add_serve_parser(subcommands)

    return parser


def _add_analyze_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("analyze", help="analyze a project and render an HTML graph")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id (default: claude-sonnet-4-6)")
    cmd.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    cmd.add_argument("-o", "--output", default=None, help="HTML output path")
    cmd.add_argument("--no-open", action="store_true", help="do not open the browser")
    cmd.add_argument("--graph-only", action="store_true", help="only write knowledge-graph.json, no HTML")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.set_defaults(func=cmd_analyze)


def _add_render_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("render", help="render an existing knowledge-graph.json to HTML")
    cmd.add_argument("graph", help="path to knowledge-graph.json")
    cmd.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    cmd.add_argument("-o", "--output", default=None, help="HTML output path")
    cmd.add_argument("--no-open", action="store_true", help="do not open the browser")
    cmd.set_defaults(func=cmd_render)


def _add_dashboard_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("dashboard", help="open the HTML view for a project's existing graph")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--static", action="store_true", help="zero-JavaScript static SVG output")
    cmd.add_argument("-o", "--output", default=None, help="HTML output path")
    cmd.add_argument("--no-open", action="store_true", help="do not open the browser")
    cmd.set_defaults(func=cmd_dashboard)


def _add_wiki_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("wiki", help="generate a readable docs/wiki HTML page (non-graphical)")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("-o", "--output", default=None, help="HTML output path")
    cmd.add_argument("--no-open", action="store_true", help="do not open the browser")
    cmd.add_argument("--full", action="store_true", help="re-analyze even if a graph already exists")
    cmd.set_defaults(func=cmd_wiki)


def _add_context_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("context", help="print a compact dependency+summary codebase map (for AI agents)")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument(
        "--mode",
        choices=("full", "agent"),
        default="full",
        help="context format: full file/symbol map or compact agent handoff",
    )
    cmd.add_argument("--brief", action="store_true", help="alias for --mode agent")
    cmd.add_argument("-o", "--output", default=None, help="write to a file instead of stdout")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.set_defaults(func=cmd_context)


def _add_explain_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("explain", help="explain one file, symbol, or graph node")
    cmd.add_argument("target", help="repo path, symbol name, or node id to explain")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_explain)


def _add_impact_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("impact", help="generate a changed-file dependency impact report")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_impact)


def _add_onboard_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("onboard", help="generate a project onboarding guide")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_onboard)


def _add_generate_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("generate", help="generate graph, wiki, context, JSON, and an output index")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("-o", "--output", "--out", default=None, help="output folder (default: .codeglance/outputs)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument(
        "--profile",
        choices=("minimal", "human", "agent", "all"),
        default="minimal",
        help="output set: minimal (default), human, agent, or all",
    )
    cmd.add_argument("--serve", action="store_true", help="serve the output folder after generation")
    cmd.add_argument("--host", default="127.0.0.1", help="serve host when --serve is used")
    cmd.add_argument("--port", type=int, default=8765, help="serve port when --serve is used")
    cmd.add_argument("--open", action="store_true", help="open the generated output index when serving")
    cmd.set_defaults(func=cmd_generate)


def _add_serve_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("serve", help="host generated HTML/Markdown/JSON outputs locally")
    cmd.add_argument("path", nargs="?", default=".", help="project or output directory (default: .)")
    cmd.add_argument("--dir", default=None, help="output directory relative to path, e.g. demo or .codeglance")
    cmd.add_argument("--host", default="127.0.0.1", help="bind host (use 0.0.0.0 for phone access)")
    cmd.add_argument("--port", type=int, default=8765, help="port to bind (default: 8765)")
    cmd.add_argument("--open", action="store_true", help="open the local index in a browser")
    cmd.set_defaults(func=cmd_serve)
