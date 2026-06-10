"""Compact TOON-style graph rendering for LLM context."""

from __future__ import annotations

import json

from ..schema import KnowledgeGraph


def build_knowledge_graph_toon(graph: KnowledgeGraph) -> str:
    """Build a compact TOON-style graph representation for LLM prompt context."""
    stats = graph.stats()
    lines = [
        "schema: codeglance.knowledge-graph.toon",
        "version: 1.0",
        "",
        "project:",
        f"  name: {_toon_value(graph.project.name)}",
        f"  languages[{len(graph.project.languages)}]: {_toon_list(graph.project.languages)}",
        f"  frameworks[{len(graph.project.frameworks)}]: {_toon_list(graph.project.frameworks)}",
        f"  analyzedAt: {_toon_value(graph.project.analyzedAt)}",
        f"  gitCommitHash: {_toon_value(graph.project.gitCommitHash)}",
        f"  description: {_toon_value(graph.project.description)}",
        "",
        "stats:",
        f"  nodes: {stats['nodes']}",
        f"  edges: {stats['edges']}",
        f"  layers: {stats['layers']}",
        f"  tourSteps: {stats['tourSteps']}",
        "",
        f"nodes[{len(graph.nodes)}]{{id,type,name,path,summary,complexity,tags}}:",
    ]
    for node in graph.nodes:
        lines.append(
            "  "
            + ",".join([
                _toon_value(node.id),
                _toon_value(node.type),
                _toon_value(node.name),
                _toon_value(node.filePath),
                _toon_value(node.summary),
                _toon_value(node.complexity),
                _toon_value("|".join(node.tags)),
            ])
        )
    lines.extend(["", f"edges[{len(graph.edges)}]{{source,target,type,weight}}:"])
    for edge in graph.edges:
        lines.append(
            "  "
            + ",".join([
                _toon_value(edge.source),
                _toon_value(edge.target),
                _toon_value(edge.type),
                f"{edge.weight:g}",
            ])
        )
    lines.extend(["", f"layers[{len(graph.layers)}]{{id,name,count,description}}:"])
    for layer in graph.layers:
        lines.append(
            "  "
            + ",".join([
                _toon_value(layer.id),
                _toon_value(layer.name),
                str(len(layer.nodeIds)),
                _toon_value(layer.description),
            ])
        )
    lines.extend(["", f"tour[{len(graph.tour)}]{{order,title,nodes,description}}:"])
    for step in graph.tour:
        lines.append(
            "  "
            + ",".join([
                str(step.order),
                _toon_value(step.title),
                _toon_value("|".join(step.nodeIds)),
                _toon_value(step.description),
            ])
        )
    return "\n".join(lines).rstrip() + "\n"


def _toon_list(values: list[str]) -> str:
    """Return a comma-separated TOON value list."""
    return ",".join(_toon_value(value) for value in values)


def _toon_value(value: object) -> str:
    """Return a compact scalar for TOON table cells, quoting only when needed."""
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if not text:
        return '""'
    if any(ch in text for ch in [",", ":", "{", "}", "[", "]", "#", '"']):
        return json.dumps(text, ensure_ascii=False)
    return text
