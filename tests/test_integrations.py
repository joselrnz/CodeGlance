from pathlib import Path

import pytest

from codeglance.integrations import (
    InstallConflictError,
    apply_install_plan,
    create_install_plan,
    get_platform,
    list_platforms,
)


EXPECTED_PLATFORMS = (
    "codex",
    "claude",
    "cursor",
    "windsurf",
    "copilot",
    "gemini",
    "cline",
    "roo",
    "aider",
    "continue",
)


def test_registry_lists_supported_agent_platforms():
    assert list_platforms() == EXPECTED_PLATFORMS

    platform = get_platform("codex")
    assert platform.id == "codex"
    assert platform.display_name == "Codex"
    assert platform.files
    assert all(not Path(item.relative_path).is_absolute() for item in platform.files)

    with pytest.raises(KeyError):
        get_platform("unknown")


def test_dry_run_plan_reports_file_actions_without_writing(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["codex"], dry_run=True)

    assert plan.dry_run is True
    assert [action.status for action in plan.actions] == ["would_create"]
    assert plan.actions[0].platform == "codex"
    assert plan.actions[0].relative_path == "AGENTS.md"
    assert plan.actions[0].target_path == tmp_path / "AGENTS.md"
    assert "codeglance generate" in plan.actions[0].content
    assert "repo-relative" in plan.actions[0].content
    assert not (tmp_path / "AGENTS.md").exists()

    applied = apply_install_plan(plan)
    assert applied == []
    assert not (tmp_path / "AGENTS.md").exists()


def test_plan_actions_are_deterministic_and_repo_relative(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["continue", "codex", "claude"], dry_run=True)

    assert [(action.platform, action.relative_path) for action in plan.actions] == [
        ("codex", "AGENTS.md"),
        ("claude", "CLAUDE.md"),
        ("claude", ".claude/commands/codeglance.md"),
        ("continue", ".continue/rules/codeglance.md"),
    ]
    for action in plan.actions:
        assert not Path(action.relative_path).is_absolute()
        assert action.target_path == tmp_path / Path(action.relative_path)
        assert action.content.endswith("\n")


def test_install_prevents_overwrites_by_default(tmp_path):
    target = tmp_path / "AGENTS.md"
    target.write_text("keep this\n", encoding="utf-8")

    plan = create_install_plan(tmp_path, platforms=["codex"], dry_run=False)

    assert len(plan.actions) == 1
    assert plan.actions[0].status == "conflict"
    assert plan.has_conflicts is True

    with pytest.raises(InstallConflictError):
        apply_install_plan(plan)

    assert target.read_text(encoding="utf-8") == "keep this\n"


def test_install_can_create_and_overwrite_when_requested(tmp_path):
    create_plan = create_install_plan(tmp_path, platforms=["claude"], dry_run=False)
    created = apply_install_plan(create_plan)

    assert [item.relative_path for item in created] == [
        "CLAUDE.md",
        ".claude/commands/codeglance.md",
    ]
    assert (tmp_path / "CLAUDE.md").is_file()
    assert (tmp_path / ".claude" / "commands" / "codeglance.md").is_file()

    (tmp_path / "CLAUDE.md").write_text("old\n", encoding="utf-8")
    overwrite_plan = create_install_plan(tmp_path, platforms=["claude"], overwrite=True, dry_run=False)
    statuses = {action.relative_path: action.status for action in overwrite_plan.actions}

    assert statuses["CLAUDE.md"] == "overwrite"
    assert statuses[".claude/commands/codeglance.md"] == "overwrite"

    apply_install_plan(overwrite_plan)
    assert "Codeglance" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
