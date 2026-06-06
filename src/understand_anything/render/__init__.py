"""Rendering: turn a KnowledgeGraph into a single self-contained HTML file.

Two modes share one layout:
  - render_interactive(): canvas app with pan/zoom/search/tour (inlined JS, fully offline)
  - render_static():      zero-JavaScript inline SVG
"""

from __future__ import annotations

from collections import Counter

from ..layout import compute_layout
from ..schema import KnowledgeGraph

# Distinct, readable layer palette (dark-theme friendly).
PALETTE = [
    "#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb7185",
    "#22d3ee", "#a3e635", "#f59e0b", "#e879f9", "#4ade80", "#38bdf8",
    "#fca5a5", "#c084fc", "#2dd4bf", "#facc15",
]
UNASSIGNED_COLOR = "#64748b"


def build_view_model(graph: KnowledgeGraph) -> dict:
    node_ids = [n.id for n in graph.nodes]
    id_set = set(node_ids)
    index_of = {nid: i for i, nid in enumerate(node_ids)}

    # layer index per file-level node, then propagate to symbols via filePath.
    layer_index: dict[str, int] = {}
    for li, layer in enumerate(graph.layers):
        for nid in layer.nodeIds:
            if nid in id_set:
                layer_index[nid] = li
    path_layer: dict[str, int] = {}
    for n in graph.nodes:
        if n.id in layer_index and n.filePath:
            path_layer.setdefault(n.filePath, layer_index[n.id])

    node_layer: dict[str, int] = {}
    for n in graph.nodes:
        if n.id in layer_index:
            node_layer[n.id] = layer_index[n.id]
        elif n.filePath and n.filePath in path_layer:
            node_layer[n.id] = path_layer[n.filePath]
        else:
            node_layer[n.id] = -1

    deg: Counter = Counter()
    clean_edges = [(e.source, e.target, e.weight) for e in graph.edges
                   if e.source in id_set and e.target in id_set]
    for s, t, _w in clean_edges:
        deg[s] += 1
        deg[t] += 1

    layer_of = {nid: (node_layer[nid] if node_layer[nid] >= 0 else "_") for nid in node_ids}
    pos = compute_layout(node_ids, clean_edges, layer_of)

    layer_colors = [PALETTE[i % len(PALETTE)] for i in range(len(graph.layers))]

    nodes_vm = []
    for n in graph.nodes:
        li = node_layer[n.id]
        x, y = pos.get(n.id, (0.0, 0.0))
        nodes_vm.append({
            "id": n.id,
            "name": n.name,
            "type": n.type,
            "summary": n.summary,
            "path": n.filePath,
            "layer": li,
            "color": layer_colors[li] if li >= 0 else UNASSIGNED_COLOR,
            "x": x,
            "y": y,
            "deg": deg.get(n.id, 0),
        })

    edges_vm = [[index_of[s], index_of[t]] for s, t, _w in clean_edges]

    layers_vm = []
    for i, layer in enumerate(graph.layers):
        layers_vm.append({
            "id": layer.id,
            "name": layer.name,
            "description": layer.description,
            "color": layer_colors[i],
            "count": len([nid for nid in layer.nodeIds if nid in id_set]),
        })

    tour_vm = [{
        "title": s.title,
        "description": s.description,
        "nodeIds": [index_of[nid] for nid in s.nodeIds if nid in index_of],
    } for s in graph.tour]

    return {
        "project": graph.project.to_dict(),
        "stats": graph.stats(),
        "nodes": nodes_vm,
        "edges": edges_vm,
        "layers": layers_vm,
        "tour": tour_vm,
    }


def render_interactive(graph: KnowledgeGraph) -> str:
    from .template import render_interactive_html
    return render_interactive_html(build_view_model(graph))


def render_static(graph: KnowledgeGraph) -> str:
    from .static import render_static_html
    return render_static_html(build_view_model(graph))
