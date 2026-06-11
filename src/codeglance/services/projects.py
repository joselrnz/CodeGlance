"""Project analysis and rendering workflows."""

from __future__ import annotations

from pathlib import Path

from ..graph import analyze
from ..models import KnowledgeGraph
from ..output import GeneratedOutput, generate_outputs, mirror_to_codeglance
from ..render import (
    render_context,
    render_explain,
    render_impact,
    render_interactive,
    render_onboarding,
    render_static,
    render_wiki,
)


def analyze_project(
    root: str | Path,
    *,
    use_llm: bool = False,
    model: str | None = None,
    full: bool = False,
    progress=None,
) -> KnowledgeGraph:
    """Analyze a project directory and return its knowledge graph."""
    return analyze(Path(root), use_llm=use_llm, model=model, full=full, progress=progress)


def load_graph(path: str | Path) -> KnowledgeGraph:
    """Load a `knowledge-graph.json` file."""
    return KnowledgeGraph.load(path)


def save_graph(graph: KnowledgeGraph, path: str | Path) -> None:
    """Save a graph to disk as UTF-8 JSON."""
    graph.save(path)


def render_html(graph: KnowledgeGraph, root: str | Path | None = None, *, static: bool = False) -> str:
    """Render a knowledge graph as self-contained HTML."""
    project_root = Path(root) if root is not None else None
    return render_static(graph, project_root) if static else render_interactive(graph, project_root)


def render_docs(graph: KnowledgeGraph, root: str | Path | None = None) -> str:
    """Render a human-readable single-file wiki."""
    return render_wiki(graph, Path(root) if root is not None else None)


def render_agent_context(graph: KnowledgeGraph, root: str | Path | None = None, *, mode: str = "agent") -> str:
    """Render markdown context for agents; `mode` is `agent` or `full`."""
    return render_context(graph, Path(root) if root is not None else None, mode=mode)


def explain_target(graph: KnowledgeGraph, target: str, root: str | Path | None = None) -> str:
    """Render a focused explanation for one graph target."""
    return render_explain(graph, Path(root) if root is not None else None, target)


def render_impact_report(graph: KnowledgeGraph, root: str | Path | None = None) -> str:
    """Render a changed-file impact report."""
    return render_impact(graph, Path(root) if root is not None else None)


def render_onboarding_guide(graph: KnowledgeGraph, root: str | Path | None = None) -> str:
    """Render a generated onboarding guide."""
    return render_onboarding(graph, Path(root) if root is not None else None)


def generate_bundle(
    root: str | Path,
    out_dir: str | Path,
    *,
    use_llm: bool = False,
    model: str | None = None,
    full: bool = False,
    profile: str = "minimal",
    progress=None,
    mirror: bool = True,
) -> tuple[KnowledgeGraph, list[GeneratedOutput]]:
    """Analyze once and write a generated output bundle."""
    project_root = Path(root).resolve()
    graph, outputs = generate_outputs(
        project_root,
        out_dir,
        use_llm=use_llm,
        model=model,
        full=full,
        profile=profile,
        progress=progress,
    )
    if mirror:
        mirror_to_codeglance(project_root, outputs)
    return graph, outputs
