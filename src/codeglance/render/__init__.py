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
from ..config import DEFAULT_CONFIG, VizConfig

# Colour + sizing constants now live in VizConfig (codeglance/config.py). These module-level names
# remain as back-compat aliases sourced from the default config.
TYPE_COLORS = DEFAULT_CONFIG.type_colors
DEFAULT_TYPE_COLOR = DEFAULT_CONFIG.default_type_color
LAYER_PALETTE = DEFAULT_CONFIG.layer_palette
UNASSIGNED_COLOR = DEFAULT_CONFIG.unassigned_color
_UNASSIGNED_KEY = 1_000_000
_MAX_SOURCE_BYTES = DEFAULT_CONFIG.max_source_bytes


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


def _read_sources(graph: KnowledgeGraph, root: Path | None, config: VizConfig = DEFAULT_CONFIG) -> dict[str, str]:
    if root is None:
        return {}
    cap = config.max_source_bytes
    sources: dict[str, str] = {}
    wanted = {n.filePath for n in graph.nodes if n.filePath}
    for rel in wanted:
        p = root / rel
        try:
            if p.is_file() and p.stat().st_size <= cap * 4:
                sources[rel] = p.read_text(encoding="utf-8", errors="ignore")[:cap]
        except OSError:
            continue
    return sources


def _detect_install(root: Path | None) -> list[dict]:
    """Best-effort getting-started steps inferred from common manifest files at the project root."""
    if root is None:
        return []
    checks = [
        ("pyproject.toml", "Install (Python / pip):", "pip install ."),
        ("requirements.txt", "Install dependencies:", "pip install -r requirements.txt"),
        ("pnpm-lock.yaml", "Install (pnpm):", "pnpm install"),
        ("package.json", "Install (Node):", "npm install"),
        ("go.mod", "Build (Go):", "go build ./..."),
        ("Cargo.toml", "Build (Rust):", "cargo build"),
        ("Gemfile", "Install (Ruby):", "bundle install"),
        ("Dockerfile", "Build the container image:", "docker build -t app ."),
        ("Makefile", "Common tasks:", "make"),
    ]
    steps: list[dict] = []
    for fname, label, command in checks:
        if fname == "package.json" and (root / "pnpm-lock.yaml").is_file():
            continue  # prefer pnpm when its lockfile is present
        if (root / fname).is_file():
            steps.append({"label": label, "command": command})
    return steps


def _build_knowledge(graph: KnowledgeGraph, sources: dict, index_of: dict, config: VizConfig = DEFAULT_CONFIG) -> dict | None:
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
    KW, KH, GX, GY = config.knowledge_card_w, config.knowledge_card_h, config.knowledge_gap_x, config.knowledge_gap_y
    cols = max(1, int(_math.ceil(_math.sqrt(len(arts)))))
    nodes_vm = []
    for a in arts:
        r, c = divmod(a["i"], cols)
        nodes_vm.append({"i": a["i"], "name": a["name"], "file": a["file"], "summary": a["summary"],
                         "topics": a["topics"], "nTopics": len(a["topics"]),
                         "nLinks": out_count.get(a["i"], 0), "memberIdx": a["memberIdx"],
                         "color": config.layer_color(a["i"]),
                         "x": round(60 + c * (KW + GX) + KW / 2, 1),
                         "y": round(60 + r * (KH + GY) + KH / 2, 1)})
    return {"nodes": nodes_vm, "edges": edges, "cardW": KW, "cardH": KH}


def _build_layer_folders(
    graph: KnowledgeGraph,
    node_layer: dict[str, int],
    index_of: dict[str, int],
    config: VizConfig = DEFAULT_CONFIG,
) -> dict[str, dict]:
    """Build a nested folder drill-down model for large layer views."""
    import math as _math

    def norm(path: str) -> str:
        return path.replace("\\", "/").strip("/")

    def dominant_root(paths: list[str]) -> str:
        if not paths:
            return ""
        first = Counter(p.split("/", 1)[0] for p in paths if "/" in p)
        if not first:
            return ""
        name, count = first.most_common(1)[0]
        return f"{name}/" if count >= max(6, int(len(paths) * 0.6)) else ""

    def direct_child(prefix: str, path: str) -> str | None:
        if prefix and not path.startswith(prefix):
            return None
        rest = path[len(prefix):] if prefix else path
        if "/" not in rest:
            return None
        return rest.split("/", 1)[0]

    def has_child_folder(prefix: str, paths: list[str]) -> bool:
        return any(direct_child(prefix, p) for p in paths)

    by_layer: dict[int, list[str]] = {}
    nodes_by_path: dict[str, list[int]] = {}
    complexity_by_path: dict[str, str] = {}
    for n in graph.nodes:
        if not n.filePath:
            continue
        path = norm(n.filePath)
        if not path:
            continue
        nodes_by_path.setdefault(path, []).append(index_of[n.id])
        if n.type in FILE_LEVEL_TYPES:
            li = node_layer.get(n.id, -1)
            if li >= 0:
                by_layer.setdefault(li, []).append(path)
                complexity_by_path[path] = n.complexity

    folder_w, folder_h, gap_x, gap_y = 292, 132, 70, 58
    out: dict[str, dict] = {}
    for li, raw_paths in by_layer.items():
        paths = sorted(set(raw_paths))
        if len(paths) < 12:
            continue
        root = dominant_root(paths)
        groups: dict[str, list[dict]] = {}
        queue: list[tuple[str, int]] = [(root, 0)]
        seen: set[str] = set()
        while queue:
            prefix, depth = queue.pop(0)
            if prefix in seen or depth > 5:
                continue
            seen.add(prefix)
            scoped = [p for p in paths if p.startswith(prefix)]
            child_names = sorted({c for p in scoped if (c := direct_child(prefix, p))})
            entries: list[dict] = []
            for child in child_names:
                child_prefix = f"{prefix}{child}/"
                child_paths = [p for p in scoped if p.startswith(child_prefix)]
                file_count = len(child_paths)
                node_count = sum(len(nodes_by_path.get(p, [])) for p in child_paths)
                complexity = Counter(complexity_by_path.get(p, "moderate") for p in child_paths).most_common(1)[0][0]
                child_folder_count = len({c for p in child_paths if (c := direct_child(child_prefix, p))})
                entries.append({
                    "kind": "folder",
                    "name": child,
                    "prefix": child_prefix,
                    "parentPrefix": prefix,
                    "fileCount": file_count,
                    "nodeCount": node_count,
                    "folderCount": child_folder_count,
                    "hasChildren": child_folder_count > 0,
                    "complexity": complexity,
                    "summary": f"{file_count} files under {child_prefix.rstrip('/')}.",
                    "color": config.layer_color(li),
                })
                if child_folder_count:
                    queue.append((child_prefix, depth + 1))

            direct_paths = [p for p in scoped if "/" not in p[len(prefix):]]
            if direct_paths and (entries or len(direct_paths) > 1):
                entries.append({
                    "kind": "files",
                    "name": "Files here",
                    "prefix": prefix,
                    "parentPrefix": prefix,
                    "direct": True,
                    "fileCount": len(direct_paths),
                    "nodeCount": sum(len(nodes_by_path.get(p, [])) for p in direct_paths),
                    "folderCount": 0,
                    "hasChildren": False,
                    "complexity": Counter(complexity_by_path.get(p, "moderate") for p in direct_paths).most_common(1)[0][0],
                    "summary": f"{len(direct_paths)} file(s) directly in {prefix.rstrip('/') or 'project root'}.",
                    "color": config.layer_color(li),
                })

            if entries:
                entries.sort(key=lambda e: (e["kind"] != "folder", -e["fileCount"], e["name"].lower()))
                cols = max(1, int(_math.ceil(_math.sqrt(len(entries)))))
                for i, entry in enumerate(entries):
                    r, c = divmod(i, cols)
                    entry["x"] = round(60 + c * (folder_w + gap_x) + folder_w / 2, 1)
                    entry["y"] = round(60 + r * (folder_h + gap_y) + folder_h / 2, 1)
                groups[prefix] = entries

        if groups:
            out[str(li)] = {"root": root, "groups": groups}
    return out


def build_view_model(graph: KnowledgeGraph, root: Path | None = None, config: VizConfig = DEFAULT_CONFIG) -> dict:
    """Convert a KnowledgeGraph into the renderer-neutral view model used by all outputs."""
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
    positions, containers, card_w, card_h = compute_layered_layout(records, len(graph.layers), config)

    layer_colors = [config.layer_color(i) for i in range(len(graph.layers))]

    nodes_vm = []
    for n in graph.nodes:
        x, y = positions.get(n.id, (0.0, 0.0))
        nodes_vm.append({
            "id": n.id, "name": n.name, "type": n.type, "summary": n.summary,
            "path": n.filePath, "layer": node_layer[n.id],
            "color": config.color_for_type(n.type),
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
            name, color = "Unassigned", config.unassigned_color
        else:
            name, color = graph.layers[key].name, layer_colors[key]
        containers_vm.append({"name": name, "color": color, "layer": -1 if key == _UNASSIGNED_KEY else key,
                              "x": c["x"], "y": c["y"], "w": c["w"], "h": c["h"], "count": c["count"]})

    layers_vm = [{"id": layer.id, "name": layer.name, "description": layer.description,
                  "color": layer_colors[i], "count": len([n for n in layer.nodeIds if n in id_set])}
                 for i, layer in enumerate(graph.layers)]

    type_counts = Counter(n.type for n in graph.nodes)
    types_vm = [{"type": t, "color": config.color_for_type(t), "count": c}
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
    LW, LH, GX, GY = config.layer_card_w, config.layer_card_h, config.layer_gap_x, config.layer_gap_y
    cols = max(1, int(_math.ceil(_math.sqrt(len(layers_vm)))))
    layer_cards = []
    for i, layer in enumerate(layers_vm):
        r, c = divmod(i, cols)
        layer_cards.append({**layer, "i": i, "complexity": comp_by_layer.get(i, "moderate"),
                            "x": round(60 + c * (LW + GX) + LW / 2, 1),
                            "y": round(60 + r * (LH + GY) + LH / 2, 1)})
    pair: Counter = Counter()
    for s, t, _ty in clean_edges:
        ls, lt = node_layer.get(s, -1), node_layer.get(t, -1)
        if ls >= 0 and lt >= 0 and ls != lt:
            pair[(min(ls, lt), max(ls, lt))] += 1
    layer_edges = [{"a": a, "b": b, "count": n} for (a, b), n in pair.items()]
    layer_folders = _build_layer_folders(graph, node_layer, index_of, config)

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

    DW, DH, DGX, DGY = config.domain_card_w, config.domain_card_h, config.domain_gap_x, config.domain_gap_y
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
            "color": config.layer_color(i),
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

    sources = _read_sources(graph, root, config)
    knowledge = _build_knowledge(graph, sources, index_of, config)
    process_domains = [domain.to_dict() for domain in graph.domains]
    process_flows = [flow.to_dict() for flow in graph.flows]
    process_steps = [
        {**step.to_dict(), "flowId": flow.id, "flowName": flow.name}
        for flow in graph.flows
        for step in flow.steps
    ]

    return {
        "project": graph.project.to_dict(),
        "projectRoot": str(root.resolve()).replace("\\", "/") if root is not None else "",
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
        "layerFolders": layer_folders,
        "folderCardW": 292,
        "folderCardH": 132,
        "layerCardW": LW,
        "layerCardH": LH,
        "iconSvg": icon_svg,
        "iconExt": EXT_TO_KEY,
        "iconName": NAME_TO_KEY,
        "domains": domains_vm,
        "domainEdges": domain_edges_vm,
        "processDomains": process_domains,
        "processFlows": process_flows,
        "processes": process_flows,
        "processSteps": process_steps,
        "processEvidence": list(graph.processEvidence),
        "processConfidence": graph.processConfidence,
        "domainCardW": DW,
        "domainCardH": DH,
        "diffChanged": diff_changed,
        "hasDiff": bool(diff_changed),
        "knowledge": knowledge,
        "install": _detect_install(root),
        "defaultTheme": getattr(config.default_theme, "value", config.default_theme),
        "uiLanguage": config.ui_language,
    }


def render_interactive(graph: KnowledgeGraph, root: Path | None = None, config: VizConfig = DEFAULT_CONFIG) -> str:
    """Render the interactive, self-contained HTML canvas graph."""
    from .template import render_interactive_html
    return render_interactive_html(build_view_model(graph, root, config))


def render_static(graph: KnowledgeGraph, root: Path | None = None, config: VizConfig = DEFAULT_CONFIG) -> str:
    """Render the zero-JavaScript, self-contained static SVG HTML graph."""
    from .static import render_static_html
    return render_static_html(build_view_model(graph, root, config))


def render_wiki(graph: KnowledgeGraph, root: Path | None = None, config: VizConfig = DEFAULT_CONFIG) -> str:
    """Render a readable, low-jargon docs/wiki HTML page (overview, install, architecture, reference)."""
    from .wiki import render_wiki_html
    return render_wiki_html(build_view_model(graph, root, config))


def render_context(
    graph: KnowledgeGraph,
    root: Path | None = None,
    config: VizConfig = DEFAULT_CONFIG,
    mode: str = "full",
) -> str:
    """Render a compact, dependency-first Markdown 'codebase map' for AI agents (not a web page)."""
    from .context import render_context_md
    return render_context_md(build_view_model(graph, root, config), mode=mode)


def render_explain(graph: KnowledgeGraph, root: Path | None = None, target: str = "") -> str:
    """Render a focused Markdown explanation for a file, class, function, or node id."""
    from .workflows import render_explain as _render_explain
    return _render_explain(graph, root, target)


def render_impact(graph: KnowledgeGraph, root: Path | None = None) -> str:
    """Render a Markdown impact report for changed files and nearby dependencies."""
    from .workflows import render_impact as _render_impact
    return _render_impact(graph, root)


def render_review(graph: KnowledgeGraph, root: Path | None = None, output_dir: Path | None = None) -> str:
    """Render a Markdown graph/output quality review report."""
    from .workflows import render_review as _render_review
    return _render_review(graph, root, output_dir)


def render_onboarding(graph: KnowledgeGraph, root: Path | None = None) -> str:
    """Render a Markdown onboarding guide from the analyzed graph."""
    from .workflows import render_onboarding as _render_onboarding
    return _render_onboarding(graph, root)
