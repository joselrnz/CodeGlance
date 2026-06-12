"""Data model for the knowledge graph.

A portable, self-describing `knowledge-graph.json` schema:

    { version, project, nodes[], edges[], layers[], tour[], domains[], flows[] }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Enums are re-exported here so `schema` stays the one place to import the model's vocabulary.
from .enums import Complexity, EdgeType, FILE_LEVEL, NodeType, ThemeName, ENTITY_TYPES, values  # noqa: F401

SCHEMA_VERSION = "1.0.0"

# Allowed node types / file-level types — derived from the enums (single source of truth).
NODE_TYPES = values(NodeType)
FILE_LEVEL_TYPES = frozenset(t.value for t in FILE_LEVEL)

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

COMPLEXITY_VALUES = values(Complexity)


def edge_weight(edge_type: str) -> float:
    """Default layout weight for an edge type (from the reference table); ``0.5`` if unknown."""
    return EDGE_WEIGHTS.get(edge_type, DEFAULT_EDGE_WEIGHT)


@dataclass
class Node:
    """A single knowledge-graph node (file, function, class, config, document, ...).

    The first seven fields are the core schema. ``lineRange``, ``signature`` and ``docstring``
    are optional enrichments captured from source; they are only serialised when present.
    """

    id: str
    type: str
    name: str
    filePath: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    complexity: str = "moderate"
    lineRange: list[int] | None = None   # [startLine, endLine], 1-indexed (functions/classes)
    signature: str = ""                  # declaration line, e.g. "def f(x: int) -> str"
    docstring: str = ""                  # docstring / leading doc-comment pulled from source
    languageNotes: str = ""              # language-specific notes (preserved from original graphs)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict; optional fields are omitted when empty."""
        d: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "filePath": self.filePath,
            "summary": self.summary,
            "tags": list(self.tags),
            "complexity": self.complexity,
        }
        if self.lineRange:
            d["lineRange"] = list(self.lineRange)
        if self.signature:
            d["signature"] = self.signature
        if self.docstring:
            d["docstring"] = self.docstring
        if self.languageNotes:
            d["languageNotes"] = self.languageNotes
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Node":
        """Build a Node from a dict, tolerating missing/None optional fields."""
        lr = d.get("lineRange")
        return cls(
            id=d["id"],
            type=d.get("type", "file"),
            name=d.get("name", d["id"]),
            filePath=d.get("filePath", "") or "",
            summary=d.get("summary", "") or "",
            tags=list(d.get("tags") or []),
            complexity=d.get("complexity", "moderate") or "moderate",
            lineRange=list(lr) if isinstance(lr, (list, tuple)) and lr else None,
            signature=d.get("signature", "") or "",
            docstring=d.get("docstring", "") or "",
            languageNotes=d.get("languageNotes", "") or "",
        )


@dataclass
class Edge:
    """A directed relationship between two graph nodes."""

    source: str
    target: str
    type: str
    direction: str = "directed"
    weight: float = DEFAULT_EDGE_WEIGHT

    def to_dict(self) -> dict[str, Any]:
        """Serialise this edge to the portable JSON schema."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "direction": self.direction,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Edge":
        """Build an Edge from a dict, defaulting the weight from the edge type when omitted."""
        return cls(
            source=d["source"],
            target=d["target"],
            type=d.get("type", "related"),
            direction=d.get("direction", "directed") or "directed",
            weight=float(d.get("weight", edge_weight(d.get("type", "related")))),
        )

    @property
    def key(self) -> tuple[str, str, str]:
        """Stable de-duplication key for this edge."""
        return (self.source, self.target, self.type)


@dataclass
class Layer:
    """A visual/architectural grouping of related file nodes."""

    id: str
    name: str
    description: str = ""
    nodeIds: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise this layer to the portable JSON schema."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodeIds": list(self.nodeIds),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Layer":
        """Build a Layer from current or legacy dict shapes."""
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
    """A guided-tour waypoint that highlights one or more important nodes."""

    order: int
    title: str
    description: str = ""
    nodeIds: list[str] = field(default_factory=list)
    languageLesson: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise this tour step to the portable JSON schema."""
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
        """Build a TourStep from current or legacy dict shapes."""
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
    """Project-level metadata captured at analysis time."""

    name: str = "project"
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    description: str = ""
    analyzedAt: str = ""
    gitCommitHash: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialise project metadata to the portable JSON schema."""
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
        """Build Project metadata from a dict, tolerating missing optional fields."""
        return cls(
            name=d.get("name", "project"),
            languages=list(d.get("languages") or []),
            frameworks=list(d.get("frameworks") or []),
            description=d.get("description", "") or "",
            analyzedAt=d.get("analyzedAt", "") or "",
            gitCommitHash=d.get("gitCommitHash", "") or "",
        )


@dataclass(frozen=True)
class Domain:
    """A business capability inferred from paths, names, summaries, and tags."""

    key: str
    name: str
    node_ids: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise a domain to the graph schema."""
        return {
            "key": self.key,
            "name": self.name,
            "nodeIds": list(self.node_ids),
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Domain":
        """Build a Domain from current or legacy dict shapes."""
        return cls(
            key=d.get("key", "unknown"),
            name=d.get("name", d.get("key", "Unknown")),
            node_ids=list(d.get("nodeIds") or d.get("node_ids") or []),
            evidence=list(d.get("evidence") or []),
            confidence=float(d.get("confidence", 0.0) or 0.0),
        )


@dataclass(frozen=True)
class ProcessStep:
    """One evidence-backed step in an inferred business or technical flow."""

    order: int
    label: str
    domain_key: str
    node_id: str
    file_path: str
    role: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise a process step to the graph schema."""
        return {
            "order": self.order,
            "label": self.label,
            "domainKey": self.domain_key,
            "nodeId": self.node_id,
            "filePath": self.file_path,
            "role": self.role,
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProcessStep":
        """Build a ProcessStep from current or legacy dict shapes."""
        return cls(
            order=int(d.get("order", 0) or 0),
            label=d.get("label", "Step"),
            domain_key=d.get("domainKey") or d.get("domain_key", "unknown"),
            node_id=d.get("nodeId") or d.get("node_id", ""),
            file_path=d.get("filePath") or d.get("file_path", ""),
            role=d.get("role", "file"),
            evidence=list(d.get("evidence") or []),
            confidence=float(d.get("confidence", 0.0) or 0.0),
        )


@dataclass(frozen=True)
class BusinessFlow:
    """An ordered flow through business domains and implementation files."""

    id: str
    name: str
    domain_key: str
    steps: list[ProcessStep] = field(default_factory=list)
    node_ids: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise a business flow to the graph schema."""
        return {
            "id": self.id,
            "name": self.name,
            "domainKey": self.domain_key,
            "steps": [step.to_dict() for step in self.steps],
            "nodeIds": list(self.node_ids),
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BusinessFlow":
        """Build a BusinessFlow from current or legacy dict shapes."""
        return cls(
            id=d.get("id", "flow:unknown"),
            name=d.get("name", "Flow"),
            domain_key=d.get("domainKey") or d.get("domain_key", "unknown"),
            steps=[ProcessStep.from_dict(step) for step in d.get("steps") or []],
            node_ids=list(d.get("nodeIds") or d.get("node_ids") or []),
            evidence=list(d.get("evidence") or []),
            confidence=float(d.get("confidence", 0.0) or 0.0),
        )


@dataclass(frozen=True)
class ProcessMap:
    """Process-map bundle embedded in the graph and rendered as separate artifacts."""

    domains: list[Domain] = field(default_factory=list)
    flows: list[BusinessFlow] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def processes(self) -> list[BusinessFlow]:
        """Back-compatible alias for consumers that say process instead of flow."""
        return self.flows

    def to_dict(self) -> dict[str, Any]:
        """Serialise this process map, including the process alias."""
        return {
            "domains": [domain.to_dict() for domain in self.domains],
            "flows": [flow.to_dict() for flow in self.flows],
            "processes": [flow.to_dict() for flow in self.processes],
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProcessMap":
        """Build a process map from current or legacy dict shapes."""
        flows_raw = d.get("flows")
        if flows_raw is None:
            flows_raw = d.get("processes") or []
        return cls(
            domains=[Domain.from_dict(domain) for domain in d.get("domains") or []],
            flows=[BusinessFlow.from_dict(flow) for flow in flows_raw],
            evidence=list(d.get("evidence") or d.get("processEvidence") or []),
            confidence=float(d.get("confidence", d.get("processConfidence", 0.0)) or 0.0),
        )


@dataclass
class KnowledgeGraph:
    """Complete analyzed codebase graph, including code shape and inferred process flow."""

    project: Project = field(default_factory=Project)
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    layers: list[Layer] = field(default_factory=list)
    tour: list[TourStep] = field(default_factory=list)
    domains: list[Domain] = field(default_factory=list)
    flows: list[BusinessFlow] = field(default_factory=list)
    processEvidence: list[str] = field(default_factory=list)
    processConfidence: float = 0.0
    version: str = SCHEMA_VERSION

    @property
    def processes(self) -> list[BusinessFlow]:
        """Back-compatible alias for business flows."""
        return self.flows

    @property
    def process_map(self) -> ProcessMap:
        """Return process data as a bundled map object."""
        return ProcessMap(
            domains=self.domains,
            flows=self.flows,
            evidence=self.processEvidence,
            confidence=self.processConfidence,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise the full graph to the portable JSON schema."""
        return {
            "version": self.version,
            "project": self.project.to_dict(),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "layers": [layer.to_dict() for layer in self.layers],
            "tour": [t.to_dict() for t in self.tour],
            "domains": [domain.to_dict() for domain in self.domains],
            "flows": [flow.to_dict() for flow in self.flows],
            "processes": [flow.to_dict() for flow in self.processes],
            "processEvidence": list(self.processEvidence),
            "processConfidence": self.processConfidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "KnowledgeGraph":
        """Build a KnowledgeGraph from a dict, including legacy-tolerant children."""
        process_map = ProcessMap.from_dict(d.get("processMap") or d)
        return cls(
            version=d.get("version", SCHEMA_VERSION),
            project=Project.from_dict(d.get("project") or {}),
            nodes=[Node.from_dict(n) for n in d.get("nodes") or []],
            edges=[Edge.from_dict(e) for e in d.get("edges") or []],
            layers=[Layer.from_dict(layer) for layer in d.get("layers") or []],
            tour=[TourStep.from_dict(t) for t in sorted(d.get("tour") or [], key=lambda s: s.get("order", 0))],
            domains=process_map.domains,
            flows=process_map.flows,
            processEvidence=process_map.evidence,
            processConfidence=process_map.confidence,
        )

    # --- I/O ---------------------------------------------------------------
    def save(self, path: str | Path) -> None:
        """Write the graph as UTF-8 JSON, creating the parent folder if needed."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeGraph":
        """Load a KnowledgeGraph from a UTF-8 JSON file."""
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
            if n.type not in NODE_TYPES:
                warnings.append(f"Node '{n.id}' has unknown type '{n.type}'")
            if n.complexity not in COMPLEXITY_VALUES:
                warnings.append(f"Node '{n.id}' has unknown complexity '{n.complexity}'")
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
        for domain in self.domains:
            if not domain.key:
                issues.append("Domain missing key")
            for nid in domain.node_ids:
                if nid not in ids:
                    issues.append(f"Domain '{domain.key}' refs missing node '{nid}'")
        domain_keys = {domain.key for domain in self.domains}
        for flow in self.flows:
            if not flow.id:
                issues.append("Flow missing id")
            if flow.domain_key and domain_keys and flow.domain_key not in domain_keys:
                warnings.append(f"Flow '{flow.id}' refs unknown domain '{flow.domain_key}'")
            for nid in flow.node_ids:
                if nid not in ids:
                    issues.append(f"Flow '{flow.id}' refs missing node '{nid}'")
            for step in flow.steps:
                if step.node_id and step.node_id not in ids:
                    issues.append(f"Flow '{flow.id}' step {step.order} refs missing node '{step.node_id}'")
        return issues, warnings

    def stats(self) -> dict[str, Any]:
        """Return compact aggregate counts used by the CLI and renderers."""
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
            "domains": len(self.domains),
            "flows": len(self.flows),
            "processSteps": sum(len(flow.steps) for flow in self.flows),
            "nodeTypes": node_types,
            "edgeTypes": edge_types,
        }


def _kebab(s: str) -> str:
    """Convert a string to a kebab-case slug (alphanumerics joined by single hyphens)."""
    out = []
    for ch in s.strip().lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-") or "x"
