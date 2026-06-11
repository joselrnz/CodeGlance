"""Public Python API for analyzing and rendering codebases."""

from __future__ import annotations

from .services.projects import (
    analyze_project,
    explain_target,
    generate_bundle,
    load_graph,
    render_agent_context,
    render_docs,
    render_html,
    render_impact_report,
    render_onboarding_guide,
    save_graph,
)

__all__ = [
    "analyze_project",
    "explain_target",
    "generate_bundle",
    "load_graph",
    "render_agent_context",
    "render_docs",
    "render_html",
    "render_impact_report",
    "render_onboarding_guide",
    "save_graph",
]
