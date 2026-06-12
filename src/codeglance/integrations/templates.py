"""Template text for Codeglance agent/editor integrations."""

from __future__ import annotations

import json

from .models import GuidanceFile, Platform


def guidance(platform_name: str, *extra: str) -> str:
    """Return a common repo guidance document for an agent/editor platform."""

    lines = [
        f"# CodeGlance guidance for {platform_name}",
        "",
        "Use CodeGlance outputs as repo-relative context before broad edits.",
        "",
        "- Refresh context with `codeglance generate . --profile agent`.",
        "- Start with `.codeglance/outputs/agent.md` for compact agent guidance.",
        "- Use `.codeglance/outputs/llms.txt` for the generated artifact index.",
        "- Use `.codeglance/outputs/knowledge-graph.toon` for dependency-first structure.",
        "- Use `.codeglance/outputs/impact.md` before changing shared code.",
        "- Use `.codeglance/outputs/review.md` before pushing or sharing outputs.",
        "- Keep generated guidance repo-relative; do not add secrets or network-only setup.",
    ]
    if extra:
        lines.extend(("", *extra))
    return "\n".join(lines) + "\n"


def skill_guidance(platform_name: str) -> str:
    """Return a Codex/Claude-style skill file."""

    return (
        "---\n"
        "name: codeglance\n"
        f"description: Use Codeglance generated context before broad edits in {platform_name}.\n"
        "---\n\n"
        "# Codeglance\n\n"
        "Use this skill when you need to understand the repository, plan a change, review impact, "
        "or answer where code lives without reading the whole tree.\n\n"
        "## Read Order\n\n"
        "1. `.codeglance/outputs/llms.txt`\n"
        "2. `.codeglance/outputs/agent.md`\n"
        "3. `.codeglance/outputs/processes.md`\n"
        "4. `.codeglance/outputs/impact.md`\n"
        "5. `.codeglance/outputs/review.md`\n"
        "6. `.codeglance/outputs/knowledge-graph.toon`\n\n"
        "## Refresh\n\n"
        "```bash\n"
        "codeglance generate . --out .codeglance/outputs --profile all\n"
        "```\n\n"
        "Map first, source last. Open exact files only after Codeglance names them.\n"
    )


def command_guidance(platform_name: str) -> str:
    """Return a slash-command or command-palette guidance document."""

    return guidance(
        platform_name,
        "Refresh low-token context before broad edits:",
        "",
        "```bash",
        "codeglance generate . --out .codeglance/outputs --profile all",
        "codeglance ask \"Where should I start?\" . --format markdown",
        "```",
    )


def marketplace_manifest(platform: Platform) -> GuidanceFile:
    """Return a local JSON manifest describing a generated platform adapter."""

    data = {
        "schema": "codeglance.integration",
        "version": 1,
        "platform": platform.id,
        "displayName": platform.display_name,
        "description": platform.description,
        "files": [file.relative_path for file in platform.files],
        "entrypoint": ".codeglance/outputs/llms.txt",
        "commands": {
            "generate": "codeglance generate . --out .codeglance/outputs --profile all",
            "serve": "codeglance serve . --dir .codeglance/outputs --host 0.0.0.0 --port 8777",
            "ask": "codeglance ask \"Where should I start?\" . --format markdown",
        },
    }
    return GuidanceFile(
        f".codeglance/marketplace/{platform.id}.json",
        json.dumps(data, indent=2, sort_keys=True) + "\n",
    )
