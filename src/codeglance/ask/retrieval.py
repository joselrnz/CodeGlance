"""Lexical retrieval over an existing KnowledgeGraph."""

from __future__ import annotations

from collections import Counter
import re

from ..schema import KnowledgeGraph
from .models import Evidence, QueryResult, SearchDocument

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "where",
    "which",
    "who",
    "why",
    "with",
}
_MIN_SCORE = 1.0


def build_documents(graph: KnowledgeGraph) -> list[SearchDocument]:
    """Build searchable documents from graph nodes, layers, and tour steps."""
    docs: list[SearchDocument] = []
    nodes_by_id = {node.id: node for node in graph.nodes}
    file_context = {
        node.filePath: node.summary
        for node in graph.nodes
        if node.type == "file" and node.filePath and node.summary
    }

    for node in graph.nodes:
        parts = [
            node.id,
            node.type,
            node.name,
            node.filePath,
            node.summary,
            node.signature,
            node.docstring,
            node.languageNotes,
            node.complexity,
            " ".join(node.tags),
        ]
        if node.type != "file" and node.filePath:
            parts.append(file_context.get(node.filePath, ""))
        docs.append(
            SearchDocument(
                id=f"node:{node.id}",
                source="node",
                title=node.name or node.id,
                kind=node.type,
                text=_join(parts),
                node_ids=[node.id],
                paths=[node.filePath] if node.filePath else [],
            )
        )

    for layer in graph.layers:
        node_ids = [node_id for node_id in layer.nodeIds if node_id in nodes_by_id]
        paths = _unique([nodes_by_id[node_id].filePath for node_id in node_ids if nodes_by_id[node_id].filePath])
        member_text = []
        for node_id in node_ids:
            node = nodes_by_id[node_id]
            member_text.append(_join([node.name, node.filePath, node.summary, " ".join(node.tags)]))
        docs.append(
            SearchDocument(
                id=f"layer:{layer.id}",
                source="layer",
                title=layer.name,
                kind="layer",
                text=_join([layer.id, layer.name, layer.description, " ".join(member_text)]),
                node_ids=node_ids,
                paths=paths,
            )
        )

    for step in sorted(graph.tour, key=lambda item: item.order):
        node_ids = [node_id for node_id in step.nodeIds if node_id in nodes_by_id]
        paths = _unique([nodes_by_id[node_id].filePath for node_id in node_ids if nodes_by_id[node_id].filePath])
        node_text = []
        for node_id in node_ids:
            node = nodes_by_id[node_id]
            node_text.append(_join([node.name, node.filePath, node.summary]))
        docs.append(
            SearchDocument(
                id=f"tour:{step.order}",
                source="tour",
                title=step.title,
                kind="tour",
                text=_join(
                    [
                        str(step.order),
                        step.title,
                        step.description,
                        step.languageLesson or "",
                        " ".join(node_text),
                    ]
                ),
                node_ids=node_ids,
                paths=paths,
            )
        )

    return docs


def search(question: str, graph: KnowledgeGraph, max_results: int = 5) -> QueryResult:
    """Return lexical matches from the graph without calling external services."""
    limit = max(0, max_results)
    query = question.strip()
    if not query or limit == 0:
        return _insufficient(question)

    query_tokens = _tokens(query)
    if not query_tokens:
        return _insufficient(question)

    scored = []
    for order, doc in enumerate(build_documents(graph)):
        score = _score(query, query_tokens, doc)
        if score >= _MIN_SCORE:
            scored.append((score, order, doc))

    scored.sort(key=lambda item: (_rank_group(item[2]), -item[0], item[1]))
    evidence = [_to_evidence(doc, score) for score, _order, doc in scored[:limit]]
    if not evidence:
        return _insufficient(question)

    return QueryResult(
        question=question,
        answer=_answer_from_evidence(evidence),
        evidence=evidence,
        insufficient=False,
    )


def _score(query: str, query_tokens: list[str], doc: SearchDocument) -> float:
    text = doc.text.lower()
    title = doc.title.lower()
    token_counts = Counter(_tokens(doc.text))
    score = 0.0
    for token in query_tokens:
        if token in token_counts:
            score += 1.0 + min(token_counts[token], 4) * 0.2
        if token in title:
            score += 1.0
        if any(token in path.lower() for path in doc.paths):
            score += 0.8
        if any(token in node_id.lower() for node_id in doc.node_ids):
            score += 0.5

    query_lower = query.lower()
    if len(query_tokens) > 1:
        if query_lower in text:
            score += 3.0
        bigrams = [" ".join(query_tokens[i : i + 2]) for i in range(len(query_tokens) - 1)]
        score += sum(1.0 for phrase in bigrams if phrase in text)

    if doc.source == "node" and doc.kind != "file":
        score += 0.35
    return round(score, 4)


def _rank_group(doc: SearchDocument) -> int:
    if doc.source == "node" and doc.kind != "file":
        return 0
    if doc.source == "node":
        return 1
    if doc.source == "layer":
        return 2
    return 3


def _to_evidence(doc: SearchDocument, score: float) -> Evidence:
    return Evidence(
        node_id=doc.node_ids[0] if doc.node_ids else doc.id,
        path=doc.paths[0] if doc.paths else "",
        title=doc.title,
        kind=doc.kind,
        snippet=_snippet(doc.text),
        score=score,
        source=doc.source,
    )


def _answer_from_evidence(evidence: list[Evidence]) -> str:
    first = evidence[0]
    location = f" in {first.path}" if first.path else ""
    return f"{first.title}{location}: {first.snippet}"


def _insufficient(question: str) -> QueryResult:
    return QueryResult(
        question=question,
        answer=f"There is not enough evidence in the knowledge graph to answer: {question}",
        evidence=[],
        insufficient=True,
    )


def _tokens(value: str) -> list[str]:
    return [token for token in (m.group(0).lower() for m in _TOKEN_RE.finditer(value)) if token not in _STOPWORDS]


def _snippet(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _join(parts: list[str]) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def _unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
