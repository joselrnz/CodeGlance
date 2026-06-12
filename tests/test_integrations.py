from pathlib import Path

import pytest

from codeglance.integrations import (
    InstallConflictError,
    apply_install_plan,
    create_install_plan,
    get_platform,
    list_platforms,
    parse_platforms,
    validate_installation,
)
from codeglance.integrations.templates import REQUIRED_CONTEXT_ARTIFACTS


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
    "augment",
    "zed",
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


def test_platform_selector_supports_default_all_and_comma_lists():
    assert parse_platforms("default") == ("codex", "claude")
    assert parse_platforms("cursor,copilot") == ("cursor", "copilot")
    assert parse_platforms(["copilot", "cursor"]) == ("cursor", "copilot")
    assert parse_platforms("all") == EXPECTED_PLATFORMS

    with pytest.raises(KeyError):
        parse_platforms("all,codex")


def test_dry_run_plan_reports_file_actions_without_writing(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["codex"], dry_run=True)

    assert plan.dry_run is True
    assert [action.status for action in plan.actions] == ["would_create", "would_create"]
    assert plan.actions[0].platform == "codex"
    assert plan.actions[0].relative_path == "AGENTS.md"
    assert plan.actions[0].target_path == tmp_path / "AGENTS.md"
    assert "codeglance generate" in plan.actions[0].content
    assert "repo-relative" in plan.actions[0].content
    for artifact in REQUIRED_CONTEXT_ARTIFACTS:
        assert artifact in plan.actions[0].content
    assert not (tmp_path / "AGENTS.md").exists()

    applied = apply_install_plan(plan)
    assert applied == []
    assert not (tmp_path / "AGENTS.md").exists()


def test_plan_actions_are_deterministic_and_repo_relative(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["continue", "codex", "claude"], dry_run=True)

    assert [(action.platform, action.relative_path) for action in plan.actions] == [
        ("codex", "AGENTS.md"),
        ("codex", ".agents/skills/codeglance/SKILL.md"),
        ("claude", ".claude/skills/codeglance/SKILL.md"),
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

    assert len(plan.actions) == 2
    assert plan.actions[0].status == "conflict"
    assert plan.has_conflicts is True

    with pytest.raises(InstallConflictError):
        apply_install_plan(plan)

    assert target.read_text(encoding="utf-8") == "keep this\n"


def test_install_can_create_and_overwrite_when_requested(tmp_path):
    create_plan = create_install_plan(tmp_path, platforms=["claude"], dry_run=False)
    created = apply_install_plan(create_plan)

    assert [item.relative_path for item in created] == [
        ".claude/skills/codeglance/SKILL.md",
        ".claude/commands/codeglance.md",
    ]
    assert (tmp_path / ".claude" / "skills" / "codeglance" / "SKILL.md").is_file()
    assert (tmp_path / ".claude" / "commands" / "codeglance.md").is_file()

    (tmp_path / ".claude" / "skills" / "codeglance" / "SKILL.md").write_text("old\n", encoding="utf-8")
    overwrite_plan = create_install_plan(tmp_path, platforms=["claude"], overwrite=True, dry_run=False)
    statuses = {action.relative_path: action.status for action in overwrite_plan.actions}

    assert statuses[".claude/skills/codeglance/SKILL.md"] == "overwrite"
    assert statuses[".claude/commands/codeglance.md"] == "overwrite"

    apply_install_plan(overwrite_plan)
    assert "Codeglance" in (tmp_path / ".claude" / "skills" / "codeglance" / "SKILL.md").read_text(encoding="utf-8")


def test_marketplace_manifests_are_optional_install_plan_files(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["cursor"], dry_run=True, marketplace_manifests=True)

    assert [action.relative_path for action in plan.actions] == [
        ".cursor/rules/codeglance.mdc",
        ".codeglance/marketplace/cursor.json",
    ]
    assert '"schema": "codeglance.integration"' in plan.actions[1].content
    assert '"platform": "cursor"' in plan.actions[1].content
    assert '"requiredArtifacts": [' in plan.actions[1].content
    assert ".codeglance/outputs/processes.md" in plan.actions[1].content


def test_augment_and_zed_have_repo_local_rule_files(tmp_path):
    plan = create_install_plan(tmp_path, platforms=["augment", "zed"], dry_run=True)

    assert [(action.platform, action.relative_path) for action in plan.actions] == [
        ("augment", ".augment-guidelines"),
        ("zed", ".rules"),
    ]
    assert "Augment Code" in plan.actions[0].content
    assert "Zed" in plan.actions[1].content
    for action in plan.actions:
        assert "codeglance generate" in action.content


def test_validate_reports_missing_and_modified_integration_files(tmp_path):
    missing = validate_installation(tmp_path, platforms=["codex"])
    assert [(item.status, item.relative_path) for item in missing.findings] == [
        ("missing", "AGENTS.md"),
        ("missing", ".agents/skills/codeglance/SKILL.md"),
    ]

    apply_install_plan(create_install_plan(tmp_path, platforms=["codex"], dry_run=False))
    clean = validate_installation(tmp_path, platforms=["codex"])
    assert clean.ok is True

    (tmp_path / "AGENTS.md").write_text("changed\n", encoding="utf-8")
    modified = validate_installation(tmp_path, platforms=["codex"])
    assert ("modified", "AGENTS.md", "") in [
        (item.status, item.relative_path, item.detail) for item in modified.findings
    ]
    assert ("missing_reference", "AGENTS.md", ".codeglance/outputs/llms.txt") in [
        (item.status, item.relative_path, item.detail) for item in modified.findings
    ]


def test_validate_checks_marketplace_manifest_contract(tmp_path):
    apply_install_plan(
        create_install_plan(
            tmp_path,
            platforms=["cursor"],
            marketplace_manifests=True,
            dry_run=False,
        )
    )
    clean = validate_installation(tmp_path, platforms=["cursor"], marketplace_manifests=True)
    assert clean.ok is True

    manifest = tmp_path / ".codeglance" / "marketplace" / "cursor.json"
    manifest.write_text('{"schema":"wrong","platform":"cursor"}\n', encoding="utf-8")
    report = validate_installation(tmp_path, platforms=["cursor"], marketplace_manifests=True)
    details = {(item.status, item.relative_path, item.detail) for item in report.findings}
    assert ("modified", ".codeglance/marketplace/cursor.json", "") in details
    assert ("invalid_manifest", ".codeglance/marketplace/cursor.json", "schema") in details
    assert ("invalid_manifest", ".codeglance/marketplace/cursor.json", "requiredArtifacts") in details


def test_all_platform_templates_reference_required_context_artifacts():
    for platform_id in EXPECTED_PLATFORMS:
        platform = get_platform(platform_id)
        for guidance_file in platform.files:
            for artifact in REQUIRED_CONTEXT_ARTIFACTS:
                assert artifact in guidance_file.content, (platform_id, guidance_file.relative_path, artifact)
