"""CLI coverage for Q&A, process maps, and agent integrations."""

from __future__ import annotations

import json
from pathlib import Path

from codeglance.cli.main import main
from codeglance.cli.parser import SUBCOMMANDS, build_parser


def test_cli_registers_competitive_foundation_commands():
    assert {"ask", "processes", "agents"} <= SUBCOMMANDS

    ask = build_parser().parse_args(["ask", "Where is billing?", ".", "--format", "json"])
    assert ask.command == "ask"
    assert ask.format == "json"

    agents = build_parser().parse_args(["agents", "plan", ".", "--platform", "codex"])
    assert agents.command == "agents"
    assert agents.action == "plan"
    assert agents.platform == ["codex"]

    init = build_parser().parse_args(["init", ".", "--agents", "codex,cursor", "--dry-run", "--marketplace-manifests"])
    assert init.command == "init"
    assert init.agents == "codex,cursor"
    assert init.dry_run is True
    assert init.marketplace_manifests is True

    validate = build_parser().parse_args(["agents", "validate", ".", "--platform", "all", "--marketplace-manifests"])
    assert validate.action == "validate"
    assert validate.platform == ["all"]


def test_ask_command_answers_from_graph_evidence(tmp_path, capsys):
    project = _sample_project(tmp_path)

    rc = main(["ask", "Where does checkout capture payment?", str(project), "--format", "json", "--full"])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert rc == 0
    assert payload["insufficient"] is False
    assert any("payment" in item["path"] for item in payload["evidence"])


def test_processes_command_outputs_domain_flow_json(tmp_path, capsys):
    project = _sample_project(tmp_path)

    rc = main(["processes", str(project), "--format", "json", "--full"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    domain_keys = {domain["key"] for domain in payload["domains"]}

    assert rc == 0
    assert {"cart", "payment"} <= domain_keys
    assert payload["flows"]


def test_agents_command_lists_and_dry_runs_install_plan(tmp_path, capsys):
    assert main(["agents", "list"]) == 0
    listed = capsys.readouterr().out
    assert "codex" in listed and "continue" in listed

    assert main(["agents", "plan", str(tmp_path), "--platform", "codex"]) == 0
    planned = capsys.readouterr().out
    assert "would_create" in planned
    assert "AGENTS.md" in planned
    assert not (tmp_path / "AGENTS.md").exists()

    assert main(["agents", "install", str(tmp_path), "--platform", "cursor", "--dry-run"]) == 0
    dry_install = capsys.readouterr().out
    assert "would_create" in dry_install
    assert ".cursor/rules/codeglance.mdc" in dry_install
    assert not (tmp_path / ".cursor" / "rules" / "codeglance.mdc").exists()


def test_init_agents_dry_run_install_and_validate(tmp_path, capsys):
    assert main(["init", str(tmp_path), "--agents", "codex,cursor", "--dry-run", "--marketplace-manifests"]) == 0
    dry = capsys.readouterr().err
    assert "would initialize" in dry
    assert ".agents/skills/codeglance/SKILL.md" in dry
    assert ".codeglance/marketplace/cursor.json" in dry
    assert not (tmp_path / ".codeglance" / "config.json").exists()
    assert not (tmp_path / "AGENTS.md").exists()

    assert main(["init", str(tmp_path), "--agents", "codex,cursor", "--force", "--marketplace-manifests"]) == 0
    written = capsys.readouterr().err
    assert "initialized CodeGlance" in written
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / ".agents" / "skills" / "codeglance" / "SKILL.md").is_file()
    assert (tmp_path / ".cursor" / "rules" / "codeglance.mdc").is_file()
    assert (tmp_path / ".codeglance" / "marketplace" / "cursor.json").is_file()

    assert main(["agents", "validate", str(tmp_path), "--platform", "codex,cursor", "--marketplace-manifests"]) == 0
    valid = capsys.readouterr().err
    assert "integration files valid" in valid


def _sample_project(tmp_path: Path) -> Path:
    project = tmp_path / "shop"
    (project / "src" / "api").mkdir(parents=True)
    (project / "src" / "services").mkdir(parents=True)
    (project / "src" / "api" / "cart_controller.py").write_text(
        "from services.payment_service import capture_payment\n\n"
        "def checkout():\n"
        "    return capture_payment()\n",
        encoding="utf-8",
    )
    (project / "src" / "services" / "payment_service.py").write_text(
        '"""Captures checkout payment and records invoice receipts."""\n\n'
        "def capture_payment():\n"
        "    return 'paid'\n",
        encoding="utf-8",
    )
    return project
