"""Data model for the knowledge graph.

Mirrors the original Understand-Anything `knowledge-graph.json` schema exactly so graphs are
interchangeable between the two tools:

    { version, project, nodes[], edges[], layers[], tour[] }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"

# 13 node types from the original schema.
NODE_TYPES = {
    "file", "function", "class", "module", "concept", "config", "document",
    "service", "table", "endpoint", "pipeline", "schema", "resource",
}

# File-level node types (everything that maps to a whole file, vs. a symbol inside one).
FILE_LEVEL_TYPES = {
    "file", "config", "document", "service", "pipeline", "table", "schema", "resource", "endpoint",
}

# Default edge weights by type (from the original SKILL reference table).
EDGE_WEIGHTS: dict[str, float] = {
    "contains": 1.0,
    "inherits": 0.9, "implements": 0.9,
    "calls": 0.8, "exports": 0.8, "defines_schema": 0.8,
    "imports": 0.7, "deploys": 0.7, "migrates": 0.7,
    "depends_on": 0.6, "configures": 0.6, "triggers": 0.6,
    "tested_by": 0.5, "documents": 0.5, "provisions": 0.5, "serves": 0.5, "routes": 0.5,
}
DEFAULT_EDGE_WEIGHT = 0.5

COMPLEXITY_VALUES = {"simple", "moderate", "complex"}


def edge_weight(edge_type: str) -> float:
    return EDGE_WEIGHTS.get(edge_type, DEFAULT_EDGE_WEIGHT)


@dataclass
class Node:
    id: str
    type: str
    name: str
    filePath: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    complexity: str = "moderate"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "filePath": self.filePath,
            "summary": self.summary,
            "tags": list(self.tags),
            "complexity": self.complexity,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Node":
        return cls(
            id=d["id"],
            type=d.get("type", "file"),
            name=d.get("name", d["id"]),
            filePath=d.get("filePath", "") or "",
            summary=d.get("summary", "") or "",
            tags=list(d.get("tags") or []),
            complexity=d.get("complexity", "moderate") or "moderate",
        )


@dataclass
class Edge:
    source: str
    target: str
    type: str
    direction: str = "directed"
    weight: float = DEFAULT_EDGE_WEIGHT

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "direction": self.direction,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Edge":
        return cls(
            source=d["source"],
            target=d["target"],
            type=d.get("type", "related"),
            direction=d.get("direction", "directed") or "directed",
            weight=float(d.get("weight", edge_weight(d.get("type", "related")))),
        )

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source, self.target, self.type)


@dataclass
class Layer:
    id: str
    name: str
    description: str = ""
    nodeIds: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodeIds": list(self.nodeIds),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Layer":
        node_ids = d.get("nodeIds") or d.get("nodes") or []
        # Tolerate `nodes` entries that are objects with an `id` field.
        node_ids = [n["id"] if isinstance(n, dict) else n for n in node_ids]
        return cls(
            id=d.get("id") or f"layer:{_kebab(d.get('name', 'layer'))}",
            name=d.get("name", "Layer"),
            description=d.get("description", "") or "",
            nodeIds=list(node_ids),
        )


@dataclass
class TourStep:
    order: int
    title: str
    description: str = ""
    nodeIds: list[str] = field(default_factory=list)
    languageLesson: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "order": self.order,
            "title": self.title,
            "description": self.description,
            "nodeIds": list(self.nodeIds),
        }
        if self.languageLesson:
            d["languageLesson"] = self.languageLesson
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TourStep":
        node_ids = d.get("nodeIds") or d.get("nodesToInspect") or []
        return cls(
            order=int(d.get("order", 0)),
            title=d.get("title", "Step"),
            description=d.get("description") or d.get("whyItMatters", "") or "",
            nodeIds=list(node_ids),
            languageLesson=d.get("languageLesson"),
        )


@dataclass
class Project:
    name: str = "project"
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    description: str = ""
    analyzedAt: str = ""
    gitCommitHash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "languages": list(self.languages),
            "frameworks": list(self.frameworks),
            "description": self.description,
            "analyzedAt": self.analyzedAt,
            "gitCommitHash": self.gitCommitHash,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Project":
        return cls(
            name=d.get("name", "project"),
            languages=list(d.get("languages") or []),
            frameworks=list(d.get("frameworks") or []),
            description=d.get("description", "") or "",
            analyzedAt=d.get("analyzedAt", "") or "",
            gitCommitHash=d.get("gitCommitHash", "") or "",
        )


@dataclass
class KnowledgeGraph:
    project: Project = field(default_factory=Project)
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    layers: list[Layer] = field(default_factory=list)
    tour: list[TourStep] = field(default_factory=list)
    version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project": self.project.to_dict(),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "layers": [l.to_dict() for l in self.layers],
            "tour": [t.to_dict() for t in self.tour],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "KnowledgeGraph":
        return cls(
            version=d.get("version", SCHEMA_VERSION),
            project=Project.from_dict(d.get("project") or {}),
            nodes=[Node.from_dict(n) for n in d.get("nodes") or []],
            edges=[Edge.from_dict(e) for e in d.get("edges") or []],
            layers=[Layer.from_dict(l) for l in d.get("layers") or []],
            tour=[TourStep.from_dict(t) for t in sorted(d.get("tour") or [], key=lambda s: s.get("order", 0))],
        )

    # --- I/O ---------------------------------------------------------------
    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeGraph":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    # --- Validation --------------------------------------------------------
    def validate(self) -> tuple[list[str], list[str]]:
        """Return (issues, warnings). Drops nothing — pure inspection."""
        issues: list[str] = []
        warnings: list[str] = []
        ids: set[str] = set()
        for i, n in enumerate(self.nodes):
            if not n.id:
                issues.append(f"Node[{i}] missing id")
                continue
            if n.id in ids:
                issues.append(f"Duplicate node id '{n.id}'")
            ids.add(n.id)
            if not n.summary:
                warnings.append(f"Node '{n.id}' missing summary")
        with_edges: set[str] = set()
        for i, e in enumerate(self.edges):
            if e.source not in ids:
                issues.append(f"Edge[{i}] source '{e.source}' not found")
            if e.target not in ids:
                issues.append(f"Edge[{i}] target '{e.target}' not found")
            with_edges.add(e.source)
            with_edges.add(e.target)
        for n in self.nodes:
            if n.id not in with_edges:
                warnings.append(f"Node '{n.id}' has no edges (orphan)")
        for layer in self.layers:
            for nid in layer.nodeIds:
                if nid not in ids:
                    issues.append(f"Layer '{layer.id}' refs missing node '{nid}'")
        for step in self.tour:
            for nid in step.nodeIds:
                if nid not in ids:
                    issues.append(f"Tour step {step.order} refs missing node '{nid}'")
        return issues, warnings

    def stats(self) -> dict[str, Any]:
        node_types: dict[str, int] = {}
        for n in self.nodes:
            node_types[n.type] = node_types.get(n.type, 0) + 1
        edge_types: dict[str, int] = {}
        for e in self.edges:
            edge_types[e.type] = edge_types.get(e.type, 0) + 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "layers": len(self.layers),
            "tourSteps": len(self.tour),
            "nodeTypes": node_types,
            "edgeTypes": edge_types,
        }


def _kebab(s: str) -> str:
    out = []
    for ch in s.strip().lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-") or "x"
