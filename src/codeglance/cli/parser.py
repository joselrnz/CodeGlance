"""Argument parser construction for the codeglance CLI."""

from __future__ import annotations

import argparse

from .. import __version__
from ..commands import (
    cmd_analyze,
    cmd_agents,
    cmd_ask,
    cmd_context,
    cmd_dashboard,
    cmd_explain,
    cmd_generate,
    cmd_hippocampus,
    cmd_impact,
    cmd_init,
    cmd_onboard,
    cmd_processes,
    cmd_review,
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
    "hippocampus",
    "impact",
    "review",
    "onboard",
    "init",
    "ask",
    "processes",
    "agents",
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
    _add_init_parser(subcommands)
    _add_render_parser(subcommands)
    _add_dashboard_parser(subcommands)
    _add_wiki_parser(subcommands)
    _add_context_parser(subcommands)
    _add_explain_parser(subcommands)
    _add_hippocampus_parser(subcommands)
    _add_impact_parser(subcommands)
    _add_review_parser(subcommands)
    _add_onboard_parser(subcommands)
    _add_ask_parser(subcommands)
    _add_processes_parser(subcommands)
    _add_agents_parser(subcommands)
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


def _add_init_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("init", help="bootstrap CodeGlance config and local agent instructions")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("-o", "--output", "--out", default=".codeglance/outputs", help="generated output folder")
    cmd.add_argument(
        "--profile",
        choices=("minimal", "human", "agent", "all"),
        default="all",
        help="default output profile to write into .codeglance/config.json",
    )
    cmd.add_argument("--no-agents", action="store_true", help="only create .codeglance config/ignore files")
    cmd.add_argument(
        "--agents",
        default="default",
        help="agent/editor targets to install: default, all, or comma-separated ids",
    )
    cmd.add_argument("--list-agents", action="store_true", help="list supported agent/editor targets and exit")
    cmd.add_argument("--dry-run", action="store_true", help="show files that would be written without writing them")
    cmd.add_argument("--marketplace-manifests", action="store_true", help="also generate local integration manifest JSON files")
    cmd.add_argument("--force", action="store_true", help="overwrite files that already exist")
    cmd.add_argument("--generate", action="store_true", help="generate the configured output bundle after init")
    cmd.add_argument("--language", default="en", help="default UI/content language to write into .codeglance/config.json")
    cmd.add_argument("--ui-language", default=None, help="UI language override for generated HTML")
    cmd.add_argument("--content-language", default=None, help="future generated prose language; defaults to --language")
    cmd.add_argument(
        "--localize-generated-text",
        action="store_true",
        help="record that generated prose should localize when LLM enrichment is enabled",
    )
    cmd.set_defaults(func=cmd_init)


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


def _add_hippocampus_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("hippocampus", help="generate a context memory budget for agents")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("--max-items", type=int, default=6, help="maximum files per memory lane")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_hippocampus)


def _add_impact_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("impact", help="generate a changed-file dependency impact report")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_impact)


def _add_review_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("review", help="validate graph/output quality before sharing or pushing")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("--dir", default=None, help="generated output folder to validate (default: .codeglance/outputs)")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_review)


def _add_onboard_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("onboard", help="generate a project onboarding guide")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write Markdown to a file instead of stdout")
    cmd.set_defaults(func=cmd_onboard)


def _add_ask_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("ask", help="answer a natural-language question from graph evidence")
    cmd.add_argument("question", help="question to answer")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--format", choices=("markdown", "json"), default="markdown", help="output format")
    cmd.add_argument("--max-results", type=int, default=5, help="maximum cited evidence items")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM before retrieval")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write answer to a file instead of stdout")
    cmd.set_defaults(func=cmd_ask)


def _add_processes_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("processes", help="generate an explicit business domain/process map")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("--format", choices=("markdown", "json"), default="markdown", help="output format")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM before extraction")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("-o", "--output", default=None, help="write process map to a file instead of stdout")
    cmd.set_defaults(func=cmd_processes)


def _add_agents_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("agents", help="list, plan, or install agent/editor integration files")
    actions = cmd.add_subparsers(dest="action", required=True)

    actions.add_parser("list", help="list supported agent/editor targets").set_defaults(func=cmd_agents)

    for action, help_text in (
        ("plan", "show repo-relative files that would be installed"),
        ("install", "write repo-relative integration files"),
        ("validate", "validate installed integration files"),
    ):
        child = actions.add_parser(action, help=help_text)
        child.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
        child.add_argument("--platform", action="append", help="platform id, all, default, or comma list; repeat for multiple")
        child.add_argument("--all", action="store_true", help="target all supported platforms")
        child.add_argument("--marketplace-manifests", action="store_true", help="include local integration manifest JSON files")
        child.add_argument("--force", action="store_true", help="replace existing integration files")
        child.add_argument("--overwrite", action="store_true", help="deprecated alias for --force")
        child.add_argument("--dry-run", action="store_true", help="show install actions without writing files")
        child.set_defaults(func=cmd_agents)


def _add_generate_parser(subcommands: argparse._SubParsersAction) -> None:
    cmd = subcommands.add_parser("generate", help="generate graph, wiki, context, JSON, and an output index")
    cmd.add_argument("path", nargs="?", default=".", help="project directory (default: .)")
    cmd.add_argument("-o", "--output", "--out", default=None, help="output folder (default: .codeglance/outputs)")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM (needs ANTHROPIC_API_KEY)")
    cmd.add_argument("--model", default=None, help="LLM model id")
    cmd.add_argument("--full", action="store_true", help="force a full rebuild, ignoring fingerprints")
    cmd.add_argument("--language", default="en", help="UI language for generated HTML (default: en)")
    cmd.add_argument("--ui-language", default=None, help="UI language override for generated HTML")
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
    cmd.add_argument("--watch", action="store_true", help="regenerate outputs when project files change")
    cmd.add_argument("--interval", type=float, default=1.5, help="watch polling interval in seconds")
    cmd.add_argument("--llm", action="store_true", help="enrich summaries via an LLM while watching")
    cmd.add_argument("--model", default=None, help="LLM model id used with --llm")
    cmd.add_argument("--full", action="store_true", help="force full rebuilds when watch regenerates")
    cmd.add_argument(
        "--profile",
        choices=("minimal", "human", "agent", "all"),
        default="all",
        help="output set to generate when --watch is used",
    )
    cmd.add_argument("--quiet", action="store_true", help="suppress watch progress messages")
    cmd.set_defaults(func=cmd_serve)
