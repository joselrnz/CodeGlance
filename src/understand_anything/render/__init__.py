"""Rendering: turn a KnowledgeGraph into a single self-contained HTML file.

Two modes share one layered layout:
  - render_interactive(): canvas app with cards, layer containers, code panel, search, tour
  - render_static():      zero-JavaScript inline SVG
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from ..layout import compute_layered_layout
from ..schema import KnowledgeGraph, FILE_LEVEL_TYPES

# Node colors by TYPE (mirrors the original dashboard palette).
TYPE_COLORS = {
    "file": "#4a7c9b", "function": "#5a9e6f", "class": "#8b6fb0", "module": "#c08457",
    "concept": "#d4a574", "config": "#5eead4", "document": "#7dd3fc", "service": "#a78bfa",
    "table": "#6ee7b7", "endpoint": "#fdba74", "pipeline": "#fda4af", "schema": "#f0abfc",
    "resource": "#fca5a5",
}
DEFAULT_TYPE_COLOR = "#94a3b8"

# Layer container border palette.
LAYER_PALETTE = [
    "#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb7185",
    "#22d3ee", "#a3e635", "#f59e0b", "#e879f9", "#4ade80", "#38bdf8",
    "#fca5a5", "#c084fc", "#2dd4bf", "#facc15",
]
UNASSIGNED_COLOR = "#64748b"
_UNASSIGNED_KEY = 1_000_000

_MAX_SOURCE_BYTES = 16_000


def _layer_index(graph: KnowledgeGraph) -> tuple[dict, dict]:
    """Return (node_id -> layer index, filePath -> layer index)."""
    id_set = {n.id for n in graph.nodes}
    layer_of: dict[str, int] = {}
    for li, layer in enumerate(graph.layers):
        for nid in layer.nodeIds:
            if nid in id_set:
                layer_of[nid] = li
    path_layer: dict[str, int] = {}
    for n in graph.nodes:
        if n.id in layer_of and n.filePath:
            path_layer.setdefault(n.filePath, layer_of[n.id])
    node_layer: dict[str, int] = {}
    for n in graph.nodes:
        if n.id in layer_of:
            node_layer[n.id] = layer_of[n.id]
        elif n.filePath and n.filePath in path_layer:
            node_layer[n.id] = path_layer[n.filePath]
        else:
            node_layer[n.id] = -1
    return node_layer, path_layer


def _read_sources(graph: KnowledgeGraph, root: Path | None) -> dict[str, str]:
    if root is None:
        return {}
    sources: dict[str, str] = {}
    wanted = {n.filePath for n in graph.nodes if n.filePath}
    for rel in wanted:
        p = root / rel
        try:
            if p.is_file() and p.stat().st_size <= _MAX_SOURCE_BYTES * 4:
                sources[rel] = p.read_text(encoding="utf-8", errors="ignore")[:_MAX_SOURCE_BYTES]
        except OSError:
            continue
    return sources


def build_view_model(graph: KnowledgeGraph, root: Path | None = None) -> dict:
    node_ids = [n.id for n in graph.nodes]
    id_set = set(node_ids)
    index_of = {nid: i for i, nid in enumerate(node_ids)}
    node_layer, _ = _layer_index(graph)

    deg: Counter = Counter()
    clean_edges = [(e.source, e.target, e.type) for e in graph.edges
                   if e.source in id_set and e.target in id_set]
    for s, t, _ty in clean_edges:
        deg[s] += 1
        deg[t] += 1

    records = [{"id": n.id, "layer": node_layer[n.id], "type": n.type,
                "filePath": n.filePath, "name": n.name} for n in graph.nodes]
    positions, containers, card_w, card_h = compute_layered_layout(records, len(graph.layers))

    layer_colors = [LAYER_PALETTE[i % len(LAYER_PALETTE)] for i in range(len(graph.layers))]

    nodes_vm = []
    for n in graph.nodes:
        x, y = positions.get(n.id, (0.0, 0.0))
        nodes_vm.append({
            "id": n.id, "name": n.name, "type": n.type, "summary": n.summary,
            "path": n.filePath, "layer": node_layer[n.id],
            "color": TYPE_COLORS.get(n.type, DEFAULT_TYPE_COLOR),
            "complexity": n.complexity, "tags": n.tags,
            "x": x, "y": y, "deg": deg.get(n.id, 0),
        })

    edges_vm = [[index_of[s], index_of[t], ty] for s, t, ty in clean_edges]

    containers_vm = []
    for c in containers:
        key = c["layerKey"]
        if key == _UNASSIGNED_KEY or key >= len(graph.layers):
            name, color = "Unassigned", UNASSIGNED_COLOR
        else:
            name, color = graph.layers[key].name, layer_colors[key]
        containers_vm.append({"name": name, "color": color, "layer": -1 if key == _UNASSIGNED_KEY else key,
                              "x": c["x"], "y": c["y"], "w": c["w"], "h": c["h"], "count": c["count"]})

    layers_vm = [{"id": l.id, "name": l.name, "description": l.description,
                  "color": layer_colors[i], "count": len([n for n in l.nodeIds if n in id_set])}
                 for i, l in enumerate(graph.layers)]

    type_counts = Counter(n.type for n in graph.nodes)
    types_vm = [{"type": t, "color": TYPE_COLORS.get(t, DEFAULT_TYPE_COLOR), "count": c}
                for t, c in type_counts.most_common()]

    tour_vm = [{"title": s.title, "description": s.description,
                "nodeIds": [index_of[nid] for nid in s.nodeIds if nid in index_of]}
               for s in graph.tour]

    top_connected = sorted(nodes_vm, key=lambda n: n["deg"], reverse=True)[:8]
    top_vm = [{"name": n["name"], "type": n["type"], "deg": n["deg"], "i": index_of[n["id"]]}
              for n in top_connected]

    return {
        "project": graph.project.to_dict(),
        "stats": graph.stats(),
        "nodes": nodes_vm,
        "edges": edges_vm,
        "containers": containers_vm,
        "layers": layers_vm,
        "types": types_vm,
        "tour": tour_vm,
        "topConnected": top_vm,
        "sources": _read_sources(graph, root),
        "cardW": card_w,
        "cardH": card_h,
    }


def render_interactive(graph: KnowledgeGraph, root: Path | None = None) -> str:
    from .template import render_interactive_html
    return render_interactive_html(build_view_model(graph, root))


def render_static(graph: KnowledgeGraph, root: Path | None = None) -> str:
    from .static import render_static_html
    return render_static_html(build_view_model(graph, root))
