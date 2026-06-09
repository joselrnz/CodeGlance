"""Enumerations for the knowledge-graph schema and renderer.

Every enum here is ``str``-based: a member compares equal to and serialises as its underlying
string (``NodeType.FILE == "file"`` is ``True``), so the JSON wire format is unchanged and any
code that still passes plain strings keeps working. This gives one source of truth for the
project's categorical values — types, complexity, edge kinds, themes — with autocomplete and
typo-protection, without a migration.
"""

from __future__ import annotations

from enum import Enum


class NodeType(str, Enum):
    """The 13 node types in the knowledge-graph schema."""

    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    CONCEPT = "concept"
    CONFIG = "config"
    DOCUMENT = "document"
    SERVICE = "service"
    TABLE = "table"
    ENDPOINT = "endpoint"
    PIPELINE = "pipeline"
    SCHEMA = "schema"
    RESOURCE = "resource"


class Complexity(str, Enum):
    """Per-node complexity rating, shown as a colour-coded tag on cards."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class EdgeType(str, Enum):
    """Relationship kinds between nodes (default weights live in ``schema.EDGE_WEIGHTS``)."""

    CONTAINS = "contains"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    CALLS = "calls"
    EXPORTS = "exports"
    IMPORTS = "imports"
    DEPENDS_ON = "depends_on"
    CONFIGURES = "configures"
    TRIGGERS = "triggers"
    TESTED_BY = "tested_by"
    DOCUMENTS = "documents"
    SERVES = "serves"
    ROUTES = "routes"
    DEPLOYS = "deploys"
    PROVISIONS = "provisions"
    MIGRATES = "migrates"
    DEFINES_SCHEMA = "defines_schema"
    RELATED = "related"


class ThemeName(str, Enum):
    """Built-in visual themes (the interactive renderer also ships these as JS presets)."""

    GOLD = "gold"
    OCEAN = "ocean"
    FOREST = "forest"
    ROSE = "rose"
    LIGHT = "light"


# Node types that map to a whole file (vs. a symbol defined inside one).
FILE_LEVEL: frozenset[NodeType] = frozenset({
    NodeType.FILE, NodeType.CONFIG, NodeType.DOCUMENT, NodeType.SERVICE,
    NodeType.PIPELINE, NodeType.TABLE, NodeType.SCHEMA, NodeType.RESOURCE, NodeType.ENDPOINT,
})

# Types that represent a domain "entity" (a thing with structure), surfaced as entity chips.
ENTITY_TYPES: frozenset[NodeType] = frozenset({
    NodeType.CLASS, NodeType.SCHEMA, NodeType.TABLE, NodeType.RESOURCE,
})


def values(enum_cls: type[Enum]) -> frozenset[str]:
    """Return an enum's member values as a ``frozenset`` for fast membership checks."""
    return frozenset(member.value for member in enum_cls)
