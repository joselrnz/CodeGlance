"""Architectural layer detection via community detection (Louvain) over the file graph.

Operates on file-level nodes only (symbols are folded into their file). Each detected community
becomes a layer, named after the directory / tag that dominates its members.
"""

from __future__ import annotations

from collections import Counter

from ..schema import Edge, Layer, Node, FILE_LEVEL_TYPES, _kebab


def detect_layers(nodes: list[Node], edges: list[Edge]) -> list[Layer]:
    file_nodes = [n for n in nodes if n.type in FILE_LEVEL_TYPES]
    if not file_nodes:
        return []
    file_ids = {n.id for n in file_nodes}
    node_by_id = {n.id: n for n in file_nodes}

    try:
        import networkx as nx
        from networkx.algorithms.community import louvain_communities
    except Exception:
        return _fallback_by_directory(file_nodes)

    g = nx.Graph()
    g.add_nodes_from(file_ids)
    for e in edges:
        if e.source in file_ids and e.target in file_ids:
            w = g.get_edge_data(e.source, e.target, default={}).get("weight", 0)
            g.add_edge(e.source, e.target, weight=w + e.weight)

    try:
        communities = louvain_communities(g, weight="weight", seed=42)
    except Exception:
        return _fallback_by_directory(file_nodes)

    # Keep deterministic ordering: largest communities first.
    communities = sorted((sorted(c) for c in communities), key=len, reverse=True)
    layers: list[Layer] = []
    used_names: set[str] = set()
    for members in communities:
        if not members:
            continue
        name = _name_community([node_by_id[m] for m in members], used_names)
        used_names.add(name)
        layers.append(Layer(
            id=f"layer:{_kebab(name)}",
            name=name,
            description=_describe(name, members, node_by_id),
            nodeIds=list(members),
        ))
    return layers


GENERIC_DIRS = {
    "src", "lib", "app", "apps", "source", "sources", "packages", "pkg", "internal",
    "cmd", "main", "com", "org", "net", "io", "github",
}


def _name_community(members: list[Node], used: set[str]) -> str:
    dirs = Counter()
    tags = Counter()
    for n in members:
        path = n.filePath or n.id.split(":", 1)[-1]
        dir_segs = path.split("/")[:-1]  # directory parts only
        # Deepest meaningful directory segment (skip generic containers like src/lib/app and
        # the single dominant package dir, so sub-packages such as analyze/ render/ surface).
        meaningful = [s for s in dir_segs if s.lower() not in GENERIC_DIRS]
        chosen = meaningful[-1] if meaningful else (dir_segs[-1] if dir_segs else None)
        if chosen:
            dirs[chosen] += 1
        for t in n.tags:
            if t not in ("code", "config", "docs", "file"):
                tags[t] += 1
    if dirs:
        top = dirs.most_common(1)[0][0]
        name = _titleize(top)
        if name not in used:
            return name
    if tags:
        name = _titleize(tags.most_common(1)[0][0])
        if name not in used:
            return name
    # Disambiguate.
    base = _titleize(dirs.most_common(1)[0][0]) if dirs else "Module"
    i = 2
    while f"{base} {i}" in used:
        i += 1
    return f"{base} {i}"


def _titleize(s: str) -> str:
    parts = s.replace("_", " ").replace("-", " ").replace("/", " · ").split()
    return " ".join(p.capitalize() for p in parts) or "Core"


def _describe(name: str, members: list[str], node_by_id: dict) -> str:
    kinds = Counter(node_by_id[m].type for m in members)
    summary = ", ".join(f"{c} {k}" for k, c in kinds.most_common(3))
    return f"{name} layer — {len(members)} files ({summary})."


def _fallback_by_directory(file_nodes: list[Node]) -> list[Layer]:
    groups: dict[str, list[str]] = {}
    for n in file_nodes:
        path = n.filePath or n.id.split(":", 1)[-1]
        top = path.split("/")[0] if "/" in path else "(root)"
        groups.setdefault(top, []).append(n.id)
    layers = []
    for top, ids in sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True):
        name = _titleize(top)
        layers.append(Layer(
            id=f"layer:{_kebab(name)}", name=name,
            description=f"{name} layer — {len(ids)} files.", nodeIds=ids,
        ))
    return layers
