"""Run analysis once and write selected generated artifacts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..config import VizConfig
from ..graph import analyze
from ..i18n import normalize_locale
from ..processes import process_map_for_graph, render_process_map
from ..render import (
    render_context,
    render_hippocampus,
    render_impact,
    render_interactive,
    render_onboarding,
    render_review,
    render_static,
    render_wiki,
)
from ..schema import FILE_LEVEL_TYPES, KnowledgeGraph
from .index import build_output_index
from .llm import build_llm_context_schema, build_llms_txt
from .profiles import GeneratedOutput, KNOWN_OUTPUT_NAMES, OUTPUT_PROFILES
from .toon import build_knowledge_graph_toon


def generate_outputs(
    root: str | Path,
    out_dir: str | Path,
    use_llm: bool = False,
    model: str | None = None,
    full: bool = False,
    profile: str = "minimal",
    ui_language: str = "en",
    progress=None,
) -> tuple[KnowledgeGraph, list[GeneratedOutput]]:
    """Analyze `root` once and write all human/agent outputs into `out_dir`."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"project root not found: {root}")
    if profile not in OUTPUT_PROFILES:
        profiles = ", ".join(sorted(OUTPUT_PROFILES))
        raise ValueError(f"unknown output profile {profile!r}; expected one of: {profiles}")

    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    _clear_known_outputs(out)

    graph = analyze(root, use_llm=use_llm, model=model, progress=progress, full=full)
    viz_config = VizConfig(ui_language=normalize_locale(ui_language))
    all_outputs = [
        GeneratedOutput("LLM entrypoint", out / "llms.txt", "Text"),
        GeneratedOutput("Glance interactive visual", out / "glance.html", "HTML"),
        GeneratedOutput("Static graph", out / "graph.static.html", "HTML"),
        GeneratedOutput("Wiki", out / "wiki.html", "HTML"),
        GeneratedOutput("Business process map", out / "processes.md", "Markdown"),
        GeneratedOutput("Business process map JSON", out / "processes.json", "JSON"),
        GeneratedOutput("Full agent context", out / "context.md", "Markdown"),
        GeneratedOutput("Compact agent context", out / "agent.md", "Markdown"),
        GeneratedOutput("Hippocampus context memory", out / "hippocampus.md", "Markdown"),
        GeneratedOutput("Onboarding guide", out / "onboarding.md", "Markdown"),
        GeneratedOutput("Impact report", out / "impact.md", "Markdown"),
        GeneratedOutput("Review report", out / "review.md", "Markdown"),
        GeneratedOutput("LLM context schema", out / "llm-context.schema.json", "JSON"),
        GeneratedOutput("Knowledge graph TOON", out / "knowledge-graph.toon", "TOON"),
        GeneratedOutput("Knowledge graph JSON", out / "knowledge-graph.json", "JSON"),
        GeneratedOutput("Metadata", out / "meta.json", "JSON"),
        GeneratedOutput("Output index", out / "index.html", "HTML"),
    ]
    selected = set(OUTPUT_PROFILES[profile])
    outputs = [item for item in all_outputs if item.path.name in selected]

    if "llms.txt" in selected:
        (out / "llms.txt").write_text(build_llms_txt(root, outputs), encoding="utf-8")
    if "glance.html" in selected:
        (out / "glance.html").write_text(render_interactive(graph, root, config=viz_config), encoding="utf-8")
    if "graph.static.html" in selected:
        (out / "graph.static.html").write_text(render_static(graph, root), encoding="utf-8")
    if "wiki.html" in selected:
        (out / "wiki.html").write_text(render_wiki(graph, root), encoding="utf-8")
    if "processes.md" in selected or "processes.json" in selected:
        process_map = process_map_for_graph(graph)
        if "processes.md" in selected:
            (out / "processes.md").write_text(render_process_map(process_map, graph.project.name), encoding="utf-8")
        if "processes.json" in selected:
            (out / "processes.json").write_text(json.dumps(process_map.to_dict(), indent=2), encoding="utf-8")
    if "context.md" in selected:
        (out / "context.md").write_text(render_context(graph, root, mode="full"), encoding="utf-8")
    if "agent.md" in selected:
        (out / "agent.md").write_text(render_context(graph, root, mode="agent"), encoding="utf-8")
    if "hippocampus.md" in selected:
        (out / "hippocampus.md").write_text(render_hippocampus(graph, root), encoding="utf-8")
    if "onboarding.md" in selected:
        (out / "onboarding.md").write_text(render_onboarding(graph, root), encoding="utf-8")
    if "impact.md" in selected:
        (out / "impact.md").write_text(render_impact(graph, root), encoding="utf-8")
    if "llm-context.schema.json" in selected:
        (out / "llm-context.schema.json").write_text(
            json.dumps(build_llm_context_schema(root, outputs), indent=2),
            encoding="utf-8",
        )
    if "knowledge-graph.toon" in selected:
        (out / "knowledge-graph.toon").write_text(build_knowledge_graph_toon(graph), encoding="utf-8")
    if "knowledge-graph.json" in selected:
        graph.save(out / "knowledge-graph.json")
    if "meta.json" in selected:
        _write_meta(out / "meta.json", graph)
    if "index.html" in selected:
        (out / "index.html").write_text(build_output_index(root, outputs), encoding="utf-8")
    if "review.md" in selected:
        (out / "review.md").write_text(render_review(graph, root, out), encoding="utf-8")

    return graph, outputs


def mirror_to_codeglance(root: Path, outputs: list[GeneratedOutput]) -> None:
    """Copy generated graph metadata back to `.codeglance` for dashboard compatibility."""
    target = root / ".codeglance"
    target.mkdir(exist_ok=True)
    for name in ("knowledge-graph.json", "meta.json"):
        src = next((item.path for item in outputs if item.path.name == name), None)
        if src and src.is_file():
            shutil.copy2(src, target / name)


def _clear_known_outputs(out: Path) -> None:
    """Remove stale files from previous profile runs without touching unrelated files."""
    for name in KNOWN_OUTPUT_NAMES:
        path = out / name
        if path.is_file():
            path.unlink()


def _write_meta(path: Path, graph: KnowledgeGraph) -> None:
    meta = {
        "lastAnalyzedAt": graph.project.analyzedAt,
        "gitCommitHash": graph.project.gitCommitHash,
        "version": graph.version,
        "analyzedFiles": sum(1 for n in graph.nodes if n.type in FILE_LEVEL_TYPES),
    }
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
