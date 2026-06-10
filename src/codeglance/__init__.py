"""codeglance — turn any codebase into an interactive knowledge-graph HTML file you can open in a browser."""

__version__ = "0.0.1"

from .api import analyze_project, generate_bundle, load_graph, render_agent_context, render_docs, render_html, save_graph
from .schema import KnowledgeGraph, Node, Edge, Layer, TourStep  # noqa: F401
from .enums import NodeType, Complexity, EdgeType, ThemeName  # noqa: F401
from .config import VizConfig, DEFAULT_CONFIG  # noqa: F401

__all__ = [
    "__version__",
    "analyze_project",
    "Complexity",
    "DEFAULT_CONFIG",
    "Edge",
    "EdgeType",
    "generate_bundle",
    "KnowledgeGraph",
    "Layer",
    "load_graph",
    "Node",
    "NodeType",
    "render_agent_context",
    "render_docs",
    "render_html",
    "save_graph",
    "ThemeName",
    "TourStep",
    "VizConfig",
]
