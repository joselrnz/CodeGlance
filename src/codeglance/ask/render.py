"""Render deterministic Q&A responses."""

from __future__ import annotations

import json

from ..schema import KnowledgeGraph
from .retrieval import search


def render_answer(
    question: str,
    graph: KnowledgeGraph,
    max_results: int = 5,
    format: str = "markdown",
) -> str:
    """Answer a codebase question with cited graph evidence."""
    result = search(question, graph, max_results=max_results)
    if format == "json":
        return json.dumps(result.to_dict(), indent=2, sort_keys=True)
    if format != "markdown":
        raise ValueError("format must be 'markdown' or 'json'")

    if result.insufficient:
        return "\n".join(
            [
                result.answer,
                "",
                "No matching nodes, layers, or tour steps were found.",
            ]
        )

    lines = [
        f"Based on the knowledge graph, {result.answer}",
        "",
        "## Evidence",
    ]
    for index, evidence in enumerate(result.evidence, start=1):
        citation = _citation(evidence.node_id, evidence.path)
        lines.append(f"{index}. {evidence.snippet} {citation}")
    return "\n".join(lines)


def _citation(node_id: str, path: str) -> str:
    parts = []
    if path:
        parts.append(f"`{path}`")
    if node_id:
        parts.append(f"`{node_id}`")
    if not parts:
        return ""
    return f"({' / '.join(parts)})"
