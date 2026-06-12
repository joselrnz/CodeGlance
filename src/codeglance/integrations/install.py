"""Filesystem planning, application, and validation for integration files."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .models import (
    FileAction,
    GuidanceFile,
    InstallConflictError,
    InstallPlan,
    ValidationFinding,
    ValidationReport,
)
from .registry import get_platform, normalize_platforms
from .templates import REQUIRED_CONTEXT_ARTIFACTS, marketplace_manifest


def create_install_plan(
    root: str | Path,
    *,
    platforms: Iterable[str] | None = None,
    overwrite: bool = False,
    dry_run: bool = True,
    marketplace_manifests: bool = False,
) -> InstallPlan:
    """Build a deterministic install plan without writing files."""

    root_path = Path(root).resolve()
    platform_ids = normalize_platforms(platforms)
    actions: list[FileAction] = []

    for platform_id in platform_ids:
        platform = get_platform(platform_id)
        for file in _platform_files(platform_id, marketplace_manifests=marketplace_manifests):
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


def validate_installation(
    root: str | Path,
    *,
    platforms: Iterable[str] | None = None,
    marketplace_manifests: bool = False,
) -> ValidationReport:
    """Validate that selected integration files exist and match Codeglance templates."""

    root_path = Path(root).resolve()
    platform_ids = normalize_platforms(platforms)
    findings: list[ValidationFinding] = []

    for platform_id in platform_ids:
        platform = get_platform(platform_id)
        for file in _platform_files(platform_id, marketplace_manifests=marketplace_manifests):
            relative_path = _validate_relative_path(file.relative_path)
            target = root_path / relative_path
            if not target.exists():
                findings.append(ValidationFinding(platform.id, relative_path.as_posix(), "missing"))
                continue
            try:
                current = target.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(ValidationFinding(platform.id, relative_path.as_posix(), "unreadable"))
                continue
            if current != file.content:
                findings.append(ValidationFinding(platform.id, relative_path.as_posix(), "modified"))
            if relative_path.parts[:2] == (".codeglance", "marketplace"):
                findings.extend(_validate_marketplace_manifest(platform.id, relative_path.as_posix(), current))
            else:
                findings.extend(_validate_guidance_references(platform.id, relative_path.as_posix(), current))

    return ValidationReport(root_path, platform_ids, tuple(findings))


def _platform_files(platform_id: str, *, marketplace_manifests: bool) -> list[GuidanceFile]:
    platform = get_platform(platform_id)
    files = list(platform.files)
    if marketplace_manifests:
        files.append(marketplace_manifest(platform))
    return files


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


def _validate_guidance_references(platform_id: str, relative_path: str, content: str) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    for artifact in REQUIRED_CONTEXT_ARTIFACTS:
        if artifact not in content:
            findings.append(ValidationFinding(platform_id, relative_path, "missing_reference", artifact))
    return findings


def _validate_marketplace_manifest(platform_id: str, relative_path: str, content: str) -> list[ValidationFinding]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        return [ValidationFinding(platform_id, relative_path, "invalid_manifest", f"json: {exc.msg}")]

    findings: list[ValidationFinding] = []
    expected = {
        "schema": "codeglance.integration",
        "version": 1,
        "platform": platform_id,
        "entrypoint": ".codeglance/outputs/llms.txt",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            findings.append(ValidationFinding(platform_id, relative_path, "invalid_manifest", key))
    files = data.get("files")
    if not isinstance(files, list) or not files:
        findings.append(ValidationFinding(platform_id, relative_path, "invalid_manifest", "files"))
    commands = data.get("commands")
    if not isinstance(commands, dict) or "generate" not in commands or "ask" not in commands:
        findings.append(ValidationFinding(platform_id, relative_path, "invalid_manifest", "commands"))
    artifacts = data.get("requiredArtifacts")
    if not isinstance(artifacts, list) or any(artifact not in artifacts for artifact in REQUIRED_CONTEXT_ARTIFACTS):
        findings.append(ValidationFinding(platform_id, relative_path, "invalid_manifest", "requiredArtifacts"))
    return findings
