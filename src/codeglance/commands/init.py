"""Project bootstrap command for CodeGlance outputs and agent instructions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..api import generate_bundle
from ..integrations import (
    create_install_plan,
    default_platforms,
    get_platform,
    list_platforms,
    parse_platforms,
)
from .common import emit


def cmd_init(args: argparse.Namespace) -> int:
    """Create project-local CodeGlance config and optional agent/command files."""
    if args.list_agents:
        for platform_id in list_platforms():
            platform = get_platform(platform_id)
            emit(f"{platform.id}\t{platform.display_name}\t{platform.description}")
        return 0

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1

    written: list[Path] = []
    skipped: list[Path] = []

    def write(rel: str, content: str) -> None:
        path = root / rel
        if args.dry_run:
            skipped.append(path)
            return
        if path.exists() and not args.force:
            skipped.append(path)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    write(".codeglance/config.json", _config_json(args.profile, args.output))
    write(".codeglance/.codeglanceignore", _ignore_text())

    if not args.no_agents:
        try:
            platforms = parse_platforms(args.agents, default=default_platforms())
            plan = create_install_plan(
                root,
                platforms=platforms,
                overwrite=args.force,
                dry_run=args.dry_run,
                marketplace_manifests=args.marketplace_manifests,
            )
        except KeyError as exc:
            emit(f"Error: {exc}")
            return 1
        for action in plan.actions:
            emit(f"  {action.status:<15} {action.platform:<10} {action.relative_path}")
        if not args.dry_run:
            for action in plan.actions:
                if action.status == "conflict":
                    skipped.append(action.target_path)
                    continue
                if action.status not in {"create", "overwrite"}:
                    continue
                action.target_path.parent.mkdir(parents=True, exist_ok=True)
                action.target_path.write_text(action.content, encoding="utf-8", newline="\n")
                written.append(action.target_path)

    prefix = "would initialize" if args.dry_run else "initialized"
    emit(f"✓ {prefix} CodeGlance in {root}")
    for path in written:
        emit(f"  wrote   {path.relative_to(root)}")
    for path in skipped:
        label = "would   " if args.dry_run else "exists "
        emit(f"  {label} {path.relative_to(root)}" + ("" if args.dry_run else " (use --force to overwrite)"))

    if args.generate and not args.dry_run:
        emit("")
        graph, outputs = generate_bundle(root, root / args.output, full=False, profile=args.profile, progress=emit)
        stats = graph.stats()
        emit(f"✓ generated {len(outputs)} {args.profile} outputs")
        emit(f"  {stats['nodes']} nodes · {stats['edges']} edges · {stats['layers']} layers")
        emit(f"  Output folder: {root / args.output}")
    elif args.generate and args.dry_run:
        emit("")
        emit(f"Would generate `{args.profile}` outputs into {root / args.output}")
    else:
        emit("")
        emit(f"Next: run `codeglance generate . --out {args.output} --profile {args.profile}`")
    return 0


def _config_json(profile: str, output: str) -> str:
    data = {
        "schema": "codeglance.config",
        "version": 1,
        "outputDir": output,
        "profile": profile,
        "agent": {
            "entrypoint": "llms.txt",
            "compactContext": "agent.md",
            "onboarding": "onboarding.md",
            "impact": "impact.md",
            "review": "review.md",
            "graph": "knowledge-graph.toon",
        },
        "commands": {
            "generate": f"codeglance generate . --out {output} --profile {profile}",
            "serve": f"codeglance serve {output} --host 0.0.0.0 --port 8777",
            "context": "codeglance context . --mode agent -o AGENTS.md",
            "impact": f"codeglance impact . -o {output}/impact.md",
            "review": f"codeglance review . -o {output}/review.md",
            "onboard": f"codeglance onboard . -o {output}/onboarding.md",
        },
    }
    return json.dumps(data, indent=2) + "\n"


def _ignore_text() -> str:
    return """# Extra CodeGlance ignore patterns for this repository.
# Keep generated artifacts, dependency folders, build outputs, and local caches out of scans.

.codeglance/
.git/
.hg/
.svn/
node_modules/
vendor/
dist/
build/
target/
.venv/
venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.terraform/
*.pyc
*.log
"""
