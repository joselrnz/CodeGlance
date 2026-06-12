"""Models for deterministic codebase question answering."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Evidence:
    """A cited excerpt returned by the lexical retriever."""

    node_id: str
    path: str
    title: str
    kind: str
    snippet: str
    score: float
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "path": self.path,
            "title": self.title,
            "kind": self.kind,
            "snippet": self.snippet,
            "score": self.score,
            "source": self.source,
        }


@dataclass(frozen=True)
class QueryResult:
    """The answer and evidence for a codebase question."""

    question: str
    answer: str
    evidence: list[Evidence] = field(default_factory=list)
    insufficient: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "question": self.question,
            "answer": self.answer,
            "insufficient": self.insufficient,
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class SearchDocument:
    """A normalized graph artifact that can be scored against a query."""

    id: str
    source: str
    title: str
    kind: str
    text: str
    node_ids: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)
