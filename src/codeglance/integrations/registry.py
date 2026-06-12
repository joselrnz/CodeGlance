"""Supported Codeglance agent/editor integration platforms."""

from __future__ import annotations

from collections.abc import Iterable

from .models import GuidanceFile, Platform
from .templates import command_guidance, guidance, skill_guidance

DEFAULT_PLATFORM_IDS = ("codex", "claude")

_PLATFORMS: tuple[Platform, ...] = (
    Platform(
        id="codex",
        display_name="Codex",
        description="OpenAI Codex repository instructions.",
        files=(
            GuidanceFile("AGENTS.md", guidance("Codex")),
            GuidanceFile(".agents/skills/codeglance/SKILL.md", skill_guidance("Codex")),
        ),
    ),
    Platform(
        id="claude",
        display_name="Claude",
        description="Claude Code repository memory and command shortcut.",
        files=(
            GuidanceFile(".claude/skills/codeglance/SKILL.md", skill_guidance("Claude")),
            GuidanceFile(".claude/commands/codeglance.md", command_guidance("Claude command")),
        ),
    ),
    Platform(
        id="cursor",
        display_name="Cursor",
        description="Cursor project rule for Codeglance context.",
        files=(
            GuidanceFile(
                ".cursor/rules/codeglance.mdc",
                "---\ndescription: Use Codeglance repo-relative context\nalwaysApply: true\n---\n\n"
                + guidance("Cursor"),
            ),
        ),
    ),
    Platform(
        id="windsurf",
        display_name="Windsurf",
        description="Windsurf project rule for Codeglance context.",
        files=(GuidanceFile(".windsurf/rules/codeglance.md", guidance("Windsurf")),),
    ),
    Platform(
        id="copilot",
        display_name="GitHub Copilot",
        description="GitHub Copilot repository instructions.",
        files=(GuidanceFile(".github/copilot-instructions.md", guidance("GitHub Copilot")),),
    ),
    Platform(
        id="gemini",
        display_name="Gemini",
        description="Gemini CLI repository guidance.",
        files=(GuidanceFile("GEMINI.md", guidance("Gemini")),),
    ),
    Platform(
        id="cline",
        display_name="Cline",
        description="Cline project rule for Codeglance context.",
        files=(GuidanceFile(".clinerules/codeglance.md", guidance("Cline")),),
    ),
    Platform(
        id="roo",
        display_name="Roo",
        description="Roo Code project rule for Codeglance context.",
        files=(GuidanceFile(".roo/rules/codeglance.md", guidance("Roo")),),
    ),
    Platform(
        id="aider",
        display_name="Aider",
        description="Aider convention file for Codeglance context.",
        files=(GuidanceFile(".aider/codeglance.md", guidance("Aider")),),
    ),
    Platform(
        id="continue",
        display_name="Continue",
        description="Continue rule for Codeglance context.",
        files=(GuidanceFile(".continue/rules/codeglance.md", guidance("Continue")),),
    ),
)

_PLATFORM_BY_ID = {platform.id: platform for platform in _PLATFORMS}
_PLATFORM_ORDER = {platform.id: index for index, platform in enumerate(_PLATFORMS)}


def list_platforms() -> tuple[str, ...]:
    """Return supported platform IDs in deterministic registry order."""

    return tuple(platform.id for platform in _PLATFORMS)


def default_platforms() -> tuple[str, ...]:
    """Return the default platforms installed by `codeglance init`."""

    return DEFAULT_PLATFORM_IDS


def get_platform(platform_id: str) -> Platform:
    """Return platform metadata for a supported integration target."""

    try:
        return _PLATFORM_BY_ID[platform_id]
    except KeyError as exc:
        supported = ", ".join(list_platforms())
        raise KeyError(f"unknown integration platform {platform_id!r}; supported: {supported}") from exc


def normalize_platforms(platforms: Iterable[str] | None) -> tuple[str, ...]:
    """Return platform IDs in deterministic registry order."""

    if platforms is None:
        return list_platforms()

    unique = set(platforms)
    for platform_id in unique:
        get_platform(platform_id)
    return tuple(sorted(unique, key=_PLATFORM_ORDER.__getitem__))


def parse_platforms(value: str | Iterable[str] | None, *, default: Iterable[str] | None = None) -> tuple[str, ...]:
    """Parse comma-separated platform selectors, including `default` and `all`."""

    if value is None:
        return normalize_platforms(default)
    raw_values = [value] if isinstance(value, str) else list(value)
    tokens: list[str] = []
    for item in raw_values:
        tokens.extend(part.strip().lower() for part in str(item).split(",") if part.strip())
    if not tokens:
        return normalize_platforms(default)
    if "all" in tokens:
        if len(set(tokens)) > 1:
            raise KeyError("platform selector 'all' cannot be combined with other platforms")
        return list_platforms()
    expanded: list[str] = []
    for token in tokens:
        if token == "default":
            expanded.extend(DEFAULT_PLATFORM_IDS)
        else:
            expanded.append(token)
    return normalize_platforms(expanded)
