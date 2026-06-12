"""Public Python API for analyzing and rendering codebases."""

from __future__ import annotations

from .services.projects import (
    analyze_project,
    answer_question,
    explain_target,
    generate_bundle,
    load_graph,
    render_agent_context,
    render_docs,
    render_html,
    render_impact_report,
    render_onboarding_guide,
    render_review_report,
    render_process_report,
    save_graph,
)

__all__ = [
    "analyze_project",
    "answer_question",
    "explain_target",
    "generate_bundle",
    "load_graph",
    "render_agent_context",
    "render_docs",
    "render_html",
    "render_impact_report",
    "render_onboarding_guide",
    "render_process_report",
    "render_review_report",
    "save_graph",
]
