"""Stable public model facade.

Internally these classes live in `schema.py`. This module gives SDK users a
clear, Pydantic-style import target without adding a runtime Pydantic dependency.
"""

from __future__ import annotations

from .schema import (
    COMPLEXITY_VALUES,
    DEFAULT_EDGE_WEIGHT,
    EDGE_WEIGHTS,
    FILE_LEVEL_TYPES,
    NODE_TYPES,
    SCHEMA_VERSION,
    Edge,
    KnowledgeGraph,
    Layer,
    Node,
    Project,
    TourStep,
    edge_weight,
)

__all__ = [
    "COMPLEXITY_VALUES",
    "DEFAULT_EDGE_WEIGHT",
    "EDGE_WEIGHTS",
    "FILE_LEVEL_TYPES",
    "NODE_TYPES",
    "SCHEMA_VERSION",
    "Edge",
    "KnowledgeGraph",
    "Layer",
    "Node",
    "Project",
    "TourStep",
    "edge_weight",
]
