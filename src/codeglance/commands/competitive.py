"""CLI commands for Q&A, process maps, and agent integrations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..api import analyze_project
from ..ask import render_answer
from ..integrations import (
    InstallConflictError,
    apply_install_plan,
    create_install_plan,
    get_platform,
    list_platforms,
    parse_platforms,
    validate_installation,
)
from ..processes import extract_process_map, render_process_map
from .common import GRAPH_DIR, GRAPH_FILE, emit, write_meta
from .workflows import _write_or_print


def cmd_ask(args: argparse.Namespace) -> int:
    """Answer a natural-language question using graph evidence."""

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    answer = render_answer(args.question, graph, max_results=args.max_results, format=args.format)
    return _write_or_print(answer, args.output, "Q&A answer")


def cmd_processes(args: argparse.Namespace) -> int:
    """Generate an explicit business process/domain map."""

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    process_map = extract_process_map(graph)
    if args.format == "json":
        rendered = json.dumps(process_map.to_dict(), indent=2, sort_keys=True)
    else:
        rendered = render_process_map(process_map, graph.project.name)
    return _write_or_print(rendered, args.output, "process map")


def cmd_agents(args: argparse.Namespace) -> int:
    """List, plan, or install agent/editor integration files."""

    if args.action == "list":
        for platform_id in list_platforms():
            platform = get_platform(platform_id)
            print(f"{platform.id}\t{platform.display_name}\t{platform.description}")
        return 0

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    try:
        platforms = list_platforms() if getattr(args, "all", False) else parse_platforms(args.platform)
    except KeyError as exc:
        emit(f"Error: {exc}")
        return 1

    if args.action == "validate":
        report = validate_installation(
            root,
            platforms=platforms,
            marketplace_manifests=args.marketplace_manifests,
        )
        if report.ok:
            emit(f"✓ integration files valid for {', '.join(report.platforms)}")
            return 0
        for finding in report.findings:
            emit(f"{finding.status}\t{finding.platform}\t{finding.relative_path}")
        return 1

    dry_run = args.action == "plan" or args.dry_run
    plan = create_install_plan(
        root,
        platforms=platforms,
        overwrite=args.overwrite or args.force,
        dry_run=dry_run,
        marketplace_manifests=args.marketplace_manifests,
    )
    _print_plan(plan)
    if dry_run:
        return 0
    try:
        written = apply_install_plan(plan)
    except InstallConflictError as exc:
        emit(f"Error: {exc}")
        emit("Use --overwrite if you intentionally want to replace existing integration files.")
        return 1
    emit(f"✓ wrote {len(written)} integration file(s)")
    return 0


def _print_plan(plan) -> None:
    for action in plan.actions:
        print(f"{action.status}\t{action.platform}\t{action.relative_path}")
