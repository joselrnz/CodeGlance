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
    "resource": "#fca5a5", "variable": "#7fb3d5", "constant": "#e6b450",
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


def _build_knowledge(graph: KnowledgeGraph, sources: dict, index_of: dict) -> dict | None:
    """Knowledge graph from markdown docs: articles (files) + topics (headings), linked by
    [[wikilinks]] (related) and [](links.md) (cites). Deterministic and fully offline."""
    import math as _math
    import re as _re

    _MD = ("md", "markdown", "mdx", "rst")
    md_nodes = [n for n in graph.nodes if n.filePath and "." in n.filePath
                and n.filePath.lower().rsplit(".", 1)[-1] in _MD]
    if len(md_nodes) < 2:
        return None

    head_re = _re.compile(r"^(#{1,6})\s+(.+?)\s*#*$", _re.M)
    wiki_re = _re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
    link_re = _re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

    def norm(s):
        return _re.sub(r"[^a-z0-9]+", "", s.lower())

    arts, key_to_i = [], {}
    for n in md_nodes:
        content = sources.get(n.filePath, "") or ""
        heads = head_re.findall(content)
        base = n.filePath.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        title = heads[0][1].strip() if heads else base
        topics = [h[1].strip() for h in heads[1:]][:6]
        summary = ""
        for ln in content.splitlines():
            s = ln.strip()
            if s and not s.startswith(("#", "-", "*", ">", "|", "`")):
                summary = s
                break
        i = len(arts)
        for k in {norm(title), norm(base)}:
            if k:
                key_to_i.setdefault(k, i)
        arts.append({"i": i, "name": title, "file": n.filePath, "summary": summary[:200],
                     "topics": topics, "memberIdx": index_of.get(n.id, -1), "content": content})

    edges, seen = [], set()
    for a in arts:
        refs = [(norm(m.group(1)), "related") for m in wiki_re.finditer(a["content"])]
        for m in link_re.finditer(a["content"]):
            tgt = m.group(1).split("#")[0]
            if "." in tgt and tgt.lower().rsplit(".", 1)[-1] in _MD:
                refs.append((norm(tgt.rsplit("/", 1)[-1].rsplit(".", 1)[0]), "cites"))
        for k, ty in refs:
            j = key_to_i.get(k)
            if j is not None and j != a["i"] and (a["i"], j) not in seen:
                seen.add((a["i"], j))
                edges.append({"a": a["i"], "b": j, "type": ty, "label": ty})

    out_count = Counter(e["a"] for e in edges)
    KW, KH, GX, GY = 280.0, 150.0, 60.0, 70.0
    cols = max(1, int(_math.ceil(_math.sqrt(len(arts)))))
    nodes_vm = []
    for a in arts:
        r, c = divmod(a["i"], cols)
        nodes_vm.append({"i": a["i"], "name": a["name"], "file": a["file"], "summary": a["summary"],
                         "topics": a["topics"], "nTopics": len(a["topics"]),
                         "nLinks": out_count.get(a["i"], 0), "memberIdx": a["memberIdx"],
                         "color": LAYER_PALETTE[a["i"] % len(LAYER_PALETTE)],
                         "x": round(60 + c * (KW + GX) + KW / 2, 1),
                         "y": round(60 + r * (KH + GY) + KH / 2, 1)})
    return {"nodes": nodes_vm, "edges": edges, "cardW": KW, "cardH": KH}


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
            "lineRange": n.lineRange, "signature": n.signature, "docstring": n.docstring,
            "languageNotes": n.languageNotes,
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

    # --- Overview level: one card per layer + aggregated inter-layer edges (drill-down model) ---
    import math as _math
    comp_by_layer: dict[int, str] = {}
    for i in range(len(graph.layers)):
        cs = [n.complexity for n in graph.nodes if node_layer.get(n.id) == i]
        comp_by_layer[i] = Counter(cs).most_common(1)[0][0] if cs else "moderate"
    LW, LH, GX, GY = 300.0, 150.0, 48.0, 44.0
    cols = max(1, int(_math.ceil(_math.sqrt(len(layers_vm)))))
    layer_cards = []
    for i, l in enumerate(layers_vm):
        r, c = divmod(i, cols)
        layer_cards.append({**l, "i": i, "complexity": comp_by_layer.get(i, "moderate"),
                            "x": round(60 + c * (LW + GX) + LW / 2, 1),
                            "y": round(60 + r * (LH + GY) + LH / 2, 1)})
    pair: Counter = Counter()
    for s, t, _ty in clean_edges:
        ls, lt = node_layer.get(s, -1), node_layer.get(t, -1)
        if ls >= 0 and lt >= 0 and ls != lt:
            pair[(min(ls, lt), max(ls, lt))] += 1
    layer_edges = [{"a": a, "b": b, "count": n} for (a, b), n in pair.items()]

    # Vendored devicon language icons — inline only the ones the project actually uses.
    from .icons import ICON_SVG, EXT_TO_KEY, NAME_TO_KEY
    used_keys: set[str] = set()
    for n in graph.nodes:
        if not n.filePath:
            continue
        base = n.filePath.split("/")[-1].lower()
        key = NAME_TO_KEY.get(base)
        if not key and "." in base:
            key = EXT_TO_KEY.get(base.rsplit(".", 1)[-1])
        if key:
            used_keys.add(key)
    used_keys |= {"_folder", "_folder_open", "_file"}  # folder/file glyphs for the tree
    icon_svg = {k: ICON_SVG[k] for k in used_keys if k in ICON_SVG}

    # --- Domain map (deterministic): group nodes by top-level package/service directory ---
    # A "domain" approximates a business area or microservice: the first meaningful path
    # segment of a file. Entities are the types/classes it defines; flows are the
    # cross-domain edges (imports/calls/depends_on) between domains.
    import re as _re
    _ROOTS = {"src", "app", "lib", "libs", "pkg", "internal", "cmd", "services", "service",
              "packages", "apps", "modules", "components", "source", "sources", "srcs"}

    def _domain_key(path: str | None) -> str | None:
        if not path:
            return None
        parts = path.replace("\\", "/").split("/")
        dirs = parts[:-1]
        if not dirs:
            return "(root)"
        for d in dirs:
            if d.lower() not in _ROOTS and not d.startswith("."):
                return d
        return dirs[-1]

    def _pretty(d: str) -> str:
        if d == "(root)":
            return "Project Root"
        s = _re.sub(r"[_\-]+", " ", d)
        s = _re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
        return s.strip().title() or d

    node_domain: dict[str, str] = {}
    for n in graph.nodes:
        k = _domain_key(n.filePath)
        if k is not None:
            node_domain[n.id] = k

    dom_keys: list[str] = []
    _seen_dom: set[str] = set()
    for n in graph.nodes:  # stable order = first appearance
        k = node_domain.get(n.id)
        if k and k not in _seen_dom:
            _seen_dom.add(k)
            dom_keys.append(k)
    dom_index = {k: i for i, k in enumerate(dom_keys)}

    _ENTITY_TYPES = {"class", "schema", "table", "resource"}
    dom_files: dict[str, list] = {k: [] for k in dom_keys}
    dom_members: dict[str, list] = {k: [] for k in dom_keys}
    dom_entities: dict[str, list] = {k: [] for k in dom_keys}
    dom_desc: dict[str, str] = {k: "" for k in dom_keys}
    for n in graph.nodes:
        k = node_domain.get(n.id)
        if not k:
            continue
        idx = index_of[n.id]
        dom_members[k].append(idx)
        if n.type in FILE_LEVEL_TYPES:
            dom_files[k].append(idx)
            s = (n.summary or "").strip()
            if s and len(s) > len(dom_desc[k]):
                dom_desc[k] = s
        if n.type in _ENTITY_TYPES:
            dom_entities[k].append((n.name, deg.get(n.id, 0)))

    flow_pair: dict[tuple, Counter] = {}
    for s, t, ty in clean_edges:
        ds, dt = node_domain.get(s), node_domain.get(t)
        if ds and dt and ds != dt:
            flow_pair.setdefault((ds, dt), Counter())[ty] += 1
    incident: Counter = Counter()
    for (ds, dt) in flow_pair:
        incident[ds] += 1
        incident[dt] += 1

    DW, DH, DGX, DGY = 300.0, 150.0, 60.0, 70.0
    dcols = max(1, int(_math.ceil(_math.sqrt(len(dom_keys) or 1))))
    domains_vm = []
    for i, k in enumerate(dom_keys):
        r, c = divmod(i, dcols)
        ranked = sorted(dom_entities[k], key=lambda x: -x[1])
        _se: set[str] = set()
        ents = [name for name, _d in ranked if not (name in _se or _se.add(name))]
        nfiles = len(dom_files[k])
        desc = dom_desc[k] or f"{nfiles} file(s), {len(ents)} entit{'y' if len(ents) == 1 else 'ies'}."
        domains_vm.append({
            "i": i, "key": k, "name": _pretty(k), "description": desc[:200],
            "entities": ents[:8], "nEntities": len(ents), "nFiles": nfiles,
            "flowCount": incident.get(k, 0),
            "color": LAYER_PALETTE[i % len(LAYER_PALETTE)],
            "members": dom_members[k][:60],
            "x": round(60 + c * (DW + DGX) + DW / 2, 1),
            "y": round(60 + r * (DH + DGY) + DH / 2, 1),
        })
    domain_edges_vm = []
    for (ds, dt), cnt in flow_pair.items():
        domain_edges_vm.append({"a": dom_index[ds], "b": dom_index[dt],
                                "label": cnt.most_common(1)[0][0], "count": sum(cnt.values())})

    _changed = getattr(graph, "changed", None) or set()
    diff_changed = [index_of[nid] for nid in _changed if nid in index_of]

    sources = _read_sources(graph, root)
    knowledge = _build_knowledge(graph, sources, index_of)

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
        "sources": sources,
        "cardW": card_w,
        "cardH": card_h,
        "layerCards": layer_cards,
        "layerEdges": layer_edges,
        "layerCardW": LW,
        "layerCardH": LH,
        "iconSvg": icon_svg,
        "iconExt": EXT_TO_KEY,
        "iconName": NAME_TO_KEY,
        "domains": domains_vm,
        "domainEdges": domain_edges_vm,
        "domainCardW": DW,
        "domainCardH": DH,
        "diffChanged": diff_changed,
        "hasDiff": bool(diff_changed),
        "knowledge": knowledge,
    }


def render_interactive(graph: KnowledgeGraph, root: Path | None = None) -> str:
    from .template import render_interactive_html
    return render_interactive_html(build_view_model(graph, root))


def render_static(graph: KnowledgeGraph, root: Path | None = None) -> str:
    from .static import render_static_html
    return render_static_html(build_view_model(graph, root))
