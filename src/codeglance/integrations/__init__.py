"""Agent and editor integration install planning for Codeglance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class GuidanceFile:
    """A repo-relative guidance file template for an agent/editor platform."""

    relative_path: str
    content: str


@dataclass(frozen=True)
class Platform:
    """A supported agent/editor integration target."""

    id: str
    display_name: str
    description: str
    files: tuple[GuidanceFile, ...]


@dataclass(frozen=True)
class FileAction:
    """A planned filesystem action for a guidance file."""

    platform: str
    relative_path: str
    target_path: Path
    status: str
    content: str
    exists: bool


@dataclass(frozen=True)
class InstallPlan:
    """Deterministic install plan for one or more integration platforms."""

    root: Path
    platforms: tuple[str, ...]
    dry_run: bool
    overwrite: bool
    actions: tuple[FileAction, ...]

    @property
    def has_conflicts(self) -> bool:
        return any(action.status in {"conflict", "would_conflict"} for action in self.actions)


class InstallConflictError(FileExistsError):
    """Raised when an install plan would overwrite files without permission."""

    def __init__(self, conflicts: Iterable[FileAction]) -> None:
        self.conflicts = tuple(conflicts)
        paths = ", ".join(action.relative_path for action in self.conflicts)
        super().__init__(f"install plan has existing files: {paths}")


def _guidance(platform_name: str, *extra: str) -> str:
    lines = [
        f"# Codeglance guidance for {platform_name}",
        "",
        "Use Codeglance outputs as repo-relative context before broad edits.",
        "",
        "- Refresh context with `codeglance generate . --profile agent`.",
        "- Start with `.codeglance/outputs/agent.md` for compact agent guidance.",
        "- Use `.codeglance/outputs/llms.txt` for the generated artifact index.",
        "- Use `.codeglance/outputs/knowledge-graph.toon` for dependency-first structure.",
        "- Keep generated guidance repo-relative; do not add secrets or network-only setup.",
    ]
    if extra:
        lines.extend(("", *extra))
    return "\n".join(lines) + "\n"


_PLATFORMS: tuple[Platform, ...] = (
    Platform(
        id="codex",
        display_name="Codex",
        description="OpenAI Codex repository instructions.",
        files=(GuidanceFile("AGENTS.md", _guidance("Codex")),),
    ),
    Platform(
        id="claude",
        display_name="Claude",
        description="Claude Code repository memory and command shortcut.",
        files=(
            GuidanceFile("CLAUDE.md", _guidance("Claude")),
            GuidanceFile(
                ".claude/commands/codeglance.md",
                _guidance(
                    "Claude command",
                    "Run this when repository context may be stale:",
                    "",
                    "```sh",
                    "codeglance generate . --profile agent",
                    "```",
                ),
            ),
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
                + _guidance("Cursor"),
            ),
        ),
    ),
    Platform(
        id="windsurf",
        display_name="Windsurf",
        description="Windsurf project rule for Codeglance context.",
        files=(GuidanceFile(".windsurf/rules/codeglance.md", _guidance("Windsurf")),),
    ),
    Platform(
        id="copilot",
        display_name="GitHub Copilot",
        description="GitHub Copilot repository instructions.",
        files=(GuidanceFile(".github/copilot-instructions.md", _guidance("GitHub Copilot")),),
    ),
    Platform(
        id="gemini",
        display_name="Gemini",
        description="Gemini CLI repository guidance.",
        files=(GuidanceFile("GEMINI.md", _guidance("Gemini")),),
    ),
    Platform(
        id="cline",
        display_name="Cline",
        description="Cline project rule for Codeglance context.",
        files=(GuidanceFile(".clinerules/codeglance.md", _guidance("Cline")),),
    ),
    Platform(
        id="roo",
        display_name="Roo",
        description="Roo Code project rule for Codeglance context.",
        files=(GuidanceFile(".roo/rules-codeglance.md", _guidance("Roo")),),
    ),
    Platform(
        id="aider",
        display_name="Aider",
        description="Aider convention file for Codeglance context.",
        files=(GuidanceFile(".aider/codeglance.md", _guidance("Aider")),),
    ),
    Platform(
        id="continue",
        display_name="Continue",
        description="Continue rule for Codeglance context.",
        files=(GuidanceFile(".continue/rules/codeglance.md", _guidance("Continue")),),
    ),
)

_PLATFORM_BY_ID = {platform.id: platform for platform in _PLATFORMS}
_PLATFORM_ORDER = {platform.id: index for index, platform in enumerate(_PLATFORMS)}


def list_platforms() -> tuple[str, ...]:
    """Return supported platform IDs in deterministic registry order."""

    return tuple(platform.id for platform in _PLATFORMS)


def get_platform(platform_id: str) -> Platform:
    """Return platform metadata for a supported integration target."""

    try:
        return _PLATFORM_BY_ID[platform_id]
    except KeyError as exc:
        supported = ", ".join(list_platforms())
        raise KeyError(f"unknown integration platform {platform_id!r}; supported: {supported}") from exc


def create_install_plan(
    root: str | Path,
    *,
    platforms: Iterable[str] | None = None,
    overwrite: bool = False,
    dry_run: bool = True,
) -> InstallPlan:
    """Build a deterministic install plan without writing files."""

    root_path = Path(root).resolve()
    platform_ids = _normalize_platforms(platforms)
    actions: list[FileAction] = []

    for platform_id in platform_ids:
        platform = get_platform(platform_id)
        for file in platform.files:
            relative_path = _validate_relative_path(file.relative_path)
            target_path = root_path / relative_path
            exists = target_path.exists()
            status = _action_status(exists=exists, overwrite=overwrite, dry_run=dry_run)
            actions.append(
                FileAction(
                    platform=platform.id,
                    relative_path=relative_path.as_posix(),
                    target_path=target_path,
                    status=status,
                    content=file.content,
                    exists=exists,
                )
            )

    return InstallPlan(
        root=root_path,
        platforms=platform_ids,
        dry_run=dry_run,
        overwrite=overwrite,
        actions=tuple(actions),
    )


def apply_install_plan(plan: InstallPlan) -> list[FileAction]:
    """Apply a non-dry-run install plan and return written actions."""

    if plan.dry_run:
        return []

    conflicts = [action for action in plan.actions if action.status == "conflict"]
    if conflicts:
        raise InstallConflictError(conflicts)

    written: list[FileAction] = []
    for action in plan.actions:
        if action.status not in {"create", "overwrite"}:
            continue
        action.target_path.parent.mkdir(parents=True, exist_ok=True)
        action.target_path.write_text(action.content, encoding="utf-8", newline="\n")
        written.append(action)
    return written


def _normalize_platforms(platforms: Iterable[str] | None) -> tuple[str, ...]:
    if platforms is None:
        return list_platforms()

    unique = set(platforms)
    for platform_id in unique:
        get_platform(platform_id)
    return tuple(sorted(unique, key=_PLATFORM_ORDER.__getitem__))


def _validate_relative_path(relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"integration file path must be repo-relative: {relative_path!r}")
    return path


def _action_status(*, exists: bool, overwrite: bool, dry_run: bool) -> str:
    if exists and overwrite:
        return "would_overwrite" if dry_run else "overwrite"
    if exists:
        return "would_conflict" if dry_run else "conflict"
    return "would_create" if dry_run else "create"


__all__ = [
    "FileAction",
    "GuidanceFile",
    "InstallConflictError",
    "InstallPlan",
    "Platform",
    "apply_install_plan",
    "create_install_plan",
    "get_platform",
    "list_platforms",
]
