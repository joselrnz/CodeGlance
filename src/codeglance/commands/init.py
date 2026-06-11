"""Project bootstrap command for CodeGlance outputs and agent instructions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..api import generate_bundle
from .common import emit


def cmd_init(args: argparse.Namespace) -> int:
    """Create project-local CodeGlance config and optional agent/command files."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1

    written: list[Path] = []
    skipped: list[Path] = []

    def write(rel: str, content: str) -> None:
        path = root / rel
        if path.exists() and not args.force:
            skipped.append(path)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    write(".codeglance/config.json", _config_json(args.profile, args.output))
    write(".codeglance/.codeglanceignore", _ignore_text())

    if not args.no_agents:
        write("AGENTS.md", _agents_md(root.name))
        write(".agents/skills/codeglance/SKILL.md", _skill_md(root.name))
        write(".claude/skills/codeglance/SKILL.md", _skill_md(root.name))
        write(".claude/commands/codeglance.md", _slash_command_md(root.name))

    emit(f"✓ initialized CodeGlance in {root}")
    for path in written:
        emit(f"  wrote   {path.relative_to(root)}")
    for path in skipped:
        emit(f"  exists  {path.relative_to(root)} (use --force to overwrite)")

    if args.generate:
        emit("")
        graph, outputs = generate_bundle(root, root / args.output, full=False, profile=args.profile, progress=emit)
        stats = graph.stats()
        emit(f"✓ generated {len(outputs)} {args.profile} outputs")
        emit(f"  {stats['nodes']} nodes · {stats['edges']} edges · {stats['layers']} layers")
        emit(f"  Output folder: {root / args.output}")
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
            "graph": "knowledge-graph.toon",
        },
        "commands": {
            "generate": f"codeglance generate . --out {output} --profile {profile}",
            "serve": f"codeglance serve {output} --host 0.0.0.0 --port 8777",
            "context": "codeglance context . --mode agent -o AGENTS.md",
            "impact": f"codeglance impact . -o {output}/impact.md",
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


def _agents_md(project: str) -> str:
    return f"""# Agent Instructions

Use CodeGlance before broad source reads in `{project}`.

## Fast Path

1. Read `.codeglance/outputs/llms.txt` if it exists.
2. Read `.codeglance/outputs/agent.md` for the compact repo map.
3. Read `.codeglance/outputs/onboarding.md` for first-day orientation.
4. Read `.codeglance/outputs/impact.md` before reviewing or committing edits.
5. Open exact source files only after the generated map names them.

## Refresh

```bash
codeglance generate . --out .codeglance/outputs --profile all
```

## Focused Commands

```bash
codeglance explain <path-or-symbol>
codeglance impact . -o .codeglance/outputs/impact.md
codeglance onboard . -o .codeglance/outputs/onboarding.md
codeglance serve .codeglance/outputs --host 0.0.0.0 --port 8777
```

Keep generated files aligned with structural code changes.
"""


def _skill_md(project: str) -> str:
    return f"""---
name: codeglance
description: Use CodeGlance to understand `{project}` quickly with generated maps, onboarding docs, impact reports, and focused explanations before opening broad source files.
---

# CodeGlance

Use this skill when you need to understand the repository, plan a change, review impact, onboard a human, or answer "where is this handled?"

## Read Order

1. `.codeglance/outputs/llms.txt`
2. `.codeglance/outputs/agent.md`
3. `.codeglance/outputs/onboarding.md`
4. `.codeglance/outputs/impact.md` for edits/reviews
5. `.codeglance/outputs/knowledge-graph.toon`
6. selected source files only after the map identifies them

## Commands

```bash
codeglance generate . --out .codeglance/outputs --profile all
codeglance context . --mode agent -o AGENTS.md
codeglance explain <path-or-symbol>
codeglance impact . -o .codeglance/outputs/impact.md
codeglance onboard . -o .codeglance/outputs/onboarding.md
codeglance serve .codeglance/outputs --host 0.0.0.0 --port 8777
```

## Rules

- Map first, source last.
- Changed files first, broad search later.
- Use `explain` for a specific file/class/function.
- Use `impact` before committing or reviewing a change.
- Regenerate outputs after structural edits.
"""


def _slash_command_md(project: str) -> str:
    return f"""# /codeglance

Use CodeGlance to orient on `{project}` with low-token generated context before reading source.

Argument behavior:

- no argument: regenerate all outputs and summarize where to start
- `serve`: host `.codeglance/outputs` locally
- `impact`: refresh the impact report
- `onboard`: refresh the onboarding guide
- any other text: treat it as a path or symbol and run `codeglance explain`

Suggested implementation:

```bash
codeglance generate . --out .codeglance/outputs --profile all
codeglance impact . -o .codeglance/outputs/impact.md
codeglance onboard . -o .codeglance/outputs/onboarding.md
```

Then read:

1. `.codeglance/outputs/llms.txt`
2. `.codeglance/outputs/agent.md`
3. `.codeglance/outputs/onboarding.md`
4. `.codeglance/outputs/impact.md`

User argument:

```text
$ARGUMENTS
```
"""
