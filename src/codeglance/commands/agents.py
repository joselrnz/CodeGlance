"""CLI command for agent/editor integration files."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..integrations import (
    InstallConflictError,
    apply_install_plan,
    create_install_plan,
    get_platform,
    list_platforms,
    parse_platforms,
    validate_installation,
)
from .common import emit


def cmd_agents(args: argparse.Namespace) -> int:
    """List, plan, install, or validate agent/editor integration files."""

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
            detail = f"\t{finding.detail}" if finding.detail else ""
            emit(f"{finding.status}\t{finding.platform}\t{finding.relative_path}{detail}")
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
