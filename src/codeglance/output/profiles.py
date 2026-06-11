"""Output profile definitions and shared generated artifact metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

OUTPUT_PROFILES = {
    "minimal": (
        "llms.txt",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "glance.html",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    ),
    "human": (
        "llms.txt",
        "glance.html",
        "wiki.html",
        "onboarding.md",
        "impact.md",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    ),
    "agent": (
        "llms.txt",
        "agent.md",
        "onboarding.md",
        "impact.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
    ),
    "all": (
        "llms.txt",
        "glance.html",
        "graph.static.html",
        "wiki.html",
        "context.md",
        "agent.md",
        "onboarding.md",
        "impact.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    ),
}
LEGACY_OUTPUT_NAMES = {"graph.html"}
KNOWN_OUTPUT_NAMES = frozenset({name for names in OUTPUT_PROFILES.values() for name in names} | LEGACY_OUTPUT_NAMES)


@dataclass(frozen=True)
class GeneratedOutput:
    """A generated artifact written by `codeglance generate`."""

    label: str
    path: Path
    kind: str
