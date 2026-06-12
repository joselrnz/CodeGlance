"""Heuristic business process extraction from a Codeglance graph."""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path

from ..schema import BusinessFlow, Domain, KnowledgeGraph, Node, ProcessMap, ProcessStep

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "auth": ("auth", "login", "oauth", "token", "session", "identity"),
    "cart": ("cart", "checkout", "basket"),
    "payment": ("payment", "billing", "invoice", "stripe", "charge"),
    "order": ("order", "purchase", "fulfillment"),
    "notification": ("notification", "email", "sms", "message", "alert"),
    "catalog": ("catalog", "product", "inventory", "sku"),
    "user": ("user", "account", "profile", "customer"),
    "shipping": ("shipping", "shipment", "delivery"),
    "report": ("report", "analytics", "metric"),
}

_IGNORED_HINTS = {"util", "utils", "helper", "helpers", "lib", "common", "shared", "test", "tests"}
_ROLE_ORDER = {
    "controller": 10,
    "route": 15,
    "api": 20,
    "auth": 30,
    "service": 40,
    "domain": 50,
    "repository": 60,
    "notification": 90,
    "file": 70,
}

def extract_process_map(graph: KnowledgeGraph) -> ProcessMap:
    """Infer domains and process flows from graph nodes and dependency edges."""

    file_nodes = [node for node in graph.nodes if node.type == "file" and node.filePath]
    if not file_nodes:
        return ProcessMap(confidence=0.0)

    by_id = {node.id: node for node in file_nodes}
    domain_hits: dict[str, list[tuple[Node, str]]] = defaultdict(list)
    node_domain: dict[str, str] = {}

    for node in file_nodes:
        hit = _detect_domain(node)
        if not hit:
            continue
        key, reason = hit
        node_domain[node.id] = key
        domain_hits[key].append((node, reason))

    domains = [
        Domain(
            key=key,
            name=_title(key),
            node_ids=[node.id for node, _reason in hits],
            evidence=[f"{node.filePath}: {reason}" for node, reason in hits],
            confidence=min(1.0, 0.45 + 0.12 * len(hits)),
        )
        for key, hits in sorted(domain_hits.items())
    ]

    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        if edge.source in by_id and edge.target in by_id:
            adjacency[edge.source].append(edge.target)

    flows: list[BusinessFlow] = []
    for domain in domains:
        related_ids = _collect_related(domain.node_ids, adjacency, node_domain, limit=12)
        steps = _build_steps([by_id[nid] for nid in related_ids if nid in by_id], node_domain)
        if not steps:
            continue
        flows.append(
            BusinessFlow(
                id=f"flow:{domain.key}",
                name=f"{domain.name} Flow",
                domain_key=domain.key,
                steps=steps,
                node_ids=[step.node_id for step in steps],
                evidence=list(domain.evidence),
                confidence=round(min(1.0, domain.confidence + 0.04 * len(steps)), 3),
            )
        )

    evidence = [item for domain in domains for item in domain.evidence[:2]]
    confidence = round(sum(flow.confidence for flow in flows) / len(flows), 3) if flows else 0.0
    return ProcessMap(domains=domains, flows=flows, evidence=evidence, confidence=confidence)


def process_map_for_graph(graph: KnowledgeGraph) -> ProcessMap:
    """Return persisted process data when present; otherwise infer it from the graph."""

    if graph.domains or graph.flows:
        return graph.process_map
    return extract_process_map(graph)


def render_process_map(process_map: ProcessMap, project_name: str = "project") -> str:
    """Render a process map as Markdown for humans and AI agents."""

    lines = [
        f"# Business Process Map: {project_name}",
        "",
        f"- domains: {len(process_map.domains)}",
        f"- flows: {len(process_map.flows)}",
        f"- confidence: {process_map.confidence:g}",
        "",
        "## Domains",
    ]
    if not process_map.domains:
        lines.append("No business domains were inferred from the graph.")
    for domain in process_map.domains:
        lines.append(f"- **{domain.name}** (`{domain.key}`): {len(domain.node_ids)} node(s), confidence {domain.confidence:g}")
        for item in domain.evidence[:3]:
            lines.append(f"  - {item}")

    lines.append("")
    lines.append("## Flows")
    if not process_map.flows:
        lines.append("No ordered business flows were inferred from the graph.")
    for flow in process_map.flows:
        lines.append(f"### {flow.name}")
        lines.append(f"- domain: `{flow.domain_key}`")
        lines.append(f"- confidence: {flow.confidence:g}")
        for step in flow.steps:
            lines.append(f"{step.order}. **{step.label}** [{step.role}] - `{step.file_path}`")
    return "\n".join(lines).rstrip() + "\n"


def _detect_domain(node: Node) -> tuple[str, str] | None:
    path_text = " ".join([node.filePath, node.name]).lower()
    summary_text = node.summary.lower()
    tag_text = " ".join(node.tags).lower()
    text = " ".join([path_text, summary_text, tag_text])
    parts = {part for part in Path(node.filePath).parts for part in Path(part).stem.lower().replace("-", "_").split("_")}
    if parts & _IGNORED_HINTS and not any(keyword in text for keywords in _DOMAIN_KEYWORDS.values() for keyword in keywords):
        return None
    best: tuple[int, str, str] | None = None
    for key, keywords in _DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            score = 0
            if keyword in path_text:
                score += 4
            if keyword in tag_text:
                score += 2
            if keyword in summary_text:
                score += 1
            if score and (best is None or score > best[0]):
                best = (score, key, keyword)
    if best is None:
        return None
    _score, key, keyword = best
    return key, f"matched {keyword!r}"


def _collect_related(seed_ids: list[str], adjacency: dict[str, list[str]], node_domain: dict[str, str], limit: int) -> list[str]:
    seen: set[str] = set()
    queue: deque[str] = deque(seed_ids)
    ordered: list[str] = []
    while queue and len(ordered) < limit:
        node_id = queue.popleft()
        if node_id in seen:
            continue
        seen.add(node_id)
        if node_id in node_domain:
            ordered.append(node_id)
        for target in adjacency.get(node_id, []):
            if target not in seen:
                queue.append(target)
    return ordered


def _build_steps(nodes: list[Node], node_domain: dict[str, str]) -> list[ProcessStep]:
    ordered_nodes = sorted(nodes, key=lambda node: (_ROLE_ORDER.get(_role(node, node_domain.get(node.id, "")), 70), node.filePath))
    return [
        ProcessStep(
            order=index,
            label=_step_label(node),
            domain_key=node_domain.get(node.id, "unknown"),
            node_id=node.id,
            file_path=node.filePath,
            role=_role(node, node_domain.get(node.id, "")),
            evidence=[node.summary or node.filePath],
            confidence=0.75 if node.summary else 0.55,
        )
        for index, node in enumerate(ordered_nodes, 1)
    ]


def _role(node: Node, domain_key: str) -> str:
    text = node.filePath.lower()
    if domain_key == "auth":
        return "auth"
    if domain_key == "notification":
        return "notification"
    for role in ("controller", "route", "api", "service", "domain", "repository"):
        if role in text:
            return role
    return "file"


def _step_label(node: Node) -> str:
    stem = Path(node.filePath).stem.replace("_", " ").replace("-", " ").strip()
    return stem.title() if stem else node.name


def _title(key: str) -> str:
    return " ".join(part.capitalize() for part in key.replace("-", " ").split())


__all__ = [
    "BusinessFlow",
    "Domain",
    "ProcessMap",
    "ProcessStep",
    "extract_process_map",
    "process_map_for_graph",
    "render_process_map",
]
