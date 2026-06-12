"""Data models for Codeglance agent/editor integrations."""

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


@dataclass(frozen=True)
class ValidationFinding:
    """A missing or changed integration file discovered by validation."""

    platform: str
    relative_path: str
    status: str
    detail: str = ""


@dataclass(frozen=True)
class ValidationReport:
    """Validation result for installed agent/editor guidance files."""

    root: Path
    platforms: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings


class InstallConflictError(FileExistsError):
    """Raised when an install plan would overwrite files without permission."""

    def __init__(self, conflicts: Iterable[FileAction]) -> None:
        self.conflicts = tuple(conflicts)
        paths = ", ".join(action.relative_path for action in self.conflicts)
        super().__init__(f"install plan has existing files: {paths}")
