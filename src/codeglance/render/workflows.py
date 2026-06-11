"""Deterministic workflow renderers: explain, impact, and onboarding reports."""

from __future__ import annotations

import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path

from ..schema import FILE_LEVEL_TYPES, KnowledgeGraph, Node

_SYMBOL_TYPES = {"class", "function", "module", "endpoint", "schema", "table", "resource"}


def render_explain(graph: KnowledgeGraph, root: Path | None = None, target: str = "") -> str:
    """Render a focused Markdown explanation for one file, class, function, or node id."""
    if not target:
        raise ValueError("target is required")
    node = _find_node(graph, target)
    if node is None:
        choices = ", ".join(_display_node(n) for n in graph.nodes[:12])
        raise ValueError(f"target not found: {target}. Try one of: {choices}")

    outgoing, incoming = _adjacency(graph)
    layer_of = _node_layers(graph)
    file_nodes = _file_nodes(graph)
    file_node = file_nodes.get(node.filePath or node.id)
    peers = _symbols_in_file(graph, node.filePath) if node.filePath else []

    lines = [
        f"# Explain: {node.name}",
        "",
        f"- type: `{node.type}`",
        f"- id: `{node.id}`",
    ]
    if node.filePath:
        lines.append(f"- path: `{node.filePath}`")
    if node.lineRange:
        lines.append(f"- lines: {node.lineRange[0]}-{node.lineRange[-1]}")
    layer = layer_of.get(node.id) or (layer_of.get(file_node.id) if file_node else None)
    if layer:
        lines.append(f"- layer: {layer.name}")
    lines.append("")

    lines.append("## What It Does")
    lines.append(_sentence(node.summary) or "No summary was captured for this node yet.")
    if node.signature:
        lines.extend(["", "## Signature", "```text", node.signature, "```"])
    if node.docstring:
        lines.extend(["", "## Documentation", node.docstring.strip()])

    if peers:
        lines.extend(["", "## Same File Symbols"])
        for peer in peers[:20]:
            marker = " (selected)" if peer.id == node.id else ""
            lines.append(f"- `{peer.name}` [{peer.type}]{marker}")

    lines.extend(["", "## Relationships"])
    _append_edges(lines, "Depends On", [graph.nodes[i] for i, _ty in outgoing[node.id]], outgoing[node.id])
    _append_edges(lines, "Used By", [graph.nodes[i] for i, _ty in incoming[node.id]], incoming[node.id])

    if node.filePath:
        lines.extend(["", "## Source Preview"])
        snippet = _source_preview(root, node)
        if snippet:
            lines.extend(["```text", snippet.rstrip(), "```"])
        else:
            lines.append("Source preview is unavailable for this target.")

    lines.extend([
        "",
        "## Suggested Next Reads",
    ])
    suggested = _next_reads(graph, node, outgoing, incoming)
    if suggested:
        for n in suggested[:8]:
            lines.append(f"- `{_display_node(n)}` - {_sentence(n.summary)}")
    else:
        lines.append("- No nearby graph nodes found.")
    return "\n".join(lines).rstrip() + "\n"


def render_impact(graph: KnowledgeGraph, root: Path | None = None) -> str:
    """Render a Markdown impact report for changed files and dependency ripples."""
    changed_paths = _changed_paths(graph, root)
    outgoing, incoming = _adjacency(graph)
    file_nodes = {n.filePath: n for n in graph.nodes if n.filePath and n.type in FILE_LEVEL_TYPES}
    layer_of = _node_layers(graph)

    lines = [
        f"# Impact Report: {graph.project.name}",
        "",
        f"- analyzed: {graph.project.analyzedAt or 'unknown'}",
        f"- commit: {(graph.project.gitCommitHash or 'unknown')[:12]}",
        f"- changed files: {len(changed_paths)}",
        "",
    ]

    if changed_paths:
        lines.append("## Changed Files")
        for path in changed_paths[:30]:
            node = file_nodes.get(path)
            summary = f" - {_sentence(node.summary)}" if node and node.summary else ""
            lines.append(f"- `{path}`{summary}")
        if len(changed_paths) > 30:
            lines.append(f"- ... {len(changed_paths) - 30} more")
        lines.append("")
    else:
        lines.extend([
            "## Changed Files",
            "No changed files were detected from the fingerprint diff or current git working tree.",
            "",
        ])

    impacted: dict[str, set[str]] = defaultdict(set)
    touched_layers: Counter[str] = Counter()
    for path in changed_paths:
        node = file_nodes.get(path)
        if not node:
            continue
        layer = layer_of.get(node.id)
        if layer:
            touched_layers[layer.name] += 1
        for near in _walk_neighbors(graph, node.id, outgoing, incoming, depth=2):
            if near.filePath and near.filePath != path:
                impacted[path].add(near.filePath)
                near_layer = layer_of.get(near.id)
                if near_layer:
                    touched_layers[near_layer.name] += 1

    lines.append("## Likely Ripple Areas")
    if touched_layers:
        for name, count in touched_layers.most_common(12):
            lines.append(f"- {name}: {count} touched or nearby node(s)")
    else:
        lines.append("- No layer ripple detected.")
    lines.append("")

    lines.append("## Dependency Ripples")
    if impacted:
        for path, paths in sorted(impacted.items())[:20]:
            lines.append(f"### `{path}`")
            for dep in sorted(paths)[:12]:
                lines.append(f"- `{dep}`")
            if len(paths) > 12:
                lines.append(f"- ... {len(paths) - 12} more")
            lines.append("")
    else:
        lines.append("No cross-file dependency ripple was detected.")
        lines.append("")

    lines.extend([
        "## Review Checklist",
        "- Inspect changed files first.",
        "- Check direct importers and imported files before broad search.",
        "- Run tests for touched layers.",
        "- Regenerate CodeGlance outputs after structural edits.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_onboarding(graph: KnowledgeGraph, root: Path | None = None) -> str:
    """Render a human-friendly onboarding guide from the graph."""
    outgoing, incoming = _adjacency(graph)
    file_nodes = [n for n in graph.nodes if n.type in FILE_LEVEL_TYPES and n.filePath]
    ranked = sorted(file_nodes, key=lambda n: (-(len(outgoing[n.id]) + len(incoming[n.id])), n.filePath))
    languages = ", ".join(graph.project.languages) or "unknown"
    frameworks = ", ".join(graph.project.frameworks) or "none detected"

    lines = [
        f"# Onboarding Guide: {graph.project.name}",
        "",
        "## Project Snapshot",
        f"- files analyzed: {len(file_nodes)}",
        f"- nodes: {len(graph.nodes)}",
        f"- edges: {len(graph.edges)}",
        f"- layers: {len(graph.layers)}",
        f"- languages: {languages}",
        f"- frameworks: {frameworks}",
        "",
        "## Start Here",
    ]
    for node in ranked[:8]:
        lines.append(f"- `{node.filePath}` - {_sentence(node.summary)}")
    lines.append("")

    if graph.layers:
        lines.append("## Architecture Layers")
        layer_node_ids = {n.id for n in graph.nodes}
        for layer in graph.layers:
            count = len([nid for nid in layer.nodeIds if nid in layer_node_ids])
            desc = _sentence(layer.description) or f"{count} file(s)."
            lines.append(f"- {layer.name}: {desc}")
        lines.append("")

    if graph.tour:
        lines.append("## Guided Reading Order")
        for step in sorted(graph.tour, key=lambda s: s.order):
            targets = ", ".join(_short_id(nid) for nid in step.nodeIds[:3])
            suffix = f" (`{targets}`)" if targets else ""
            lines.append(f"{step.order}. {step.title}{suffix} - {_sentence(step.description)}")
        lines.append("")

    lines.extend([
        "## First-Day Workflow",
        "1. Open `glance.html` and stay in Overview until the layer names make sense.",
        "2. Run the guided Tour.",
        "3. Switch to Drill before Explore so files/classes are clear before functions.",
        "4. Click a hub file and read the Inspector relationships.",
        "5. Use `codeglance explain <path-or-symbol>` for focused questions.",
        "6. Use `codeglance impact` before committing changes.",
        "",
        "## Agent Workflow",
        "1. Read `llms.txt`.",
        "2. Read `agent.md`.",
        "3. Use `knowledge-graph.toon` for compact graph context.",
        "4. Open exact source files only after the graph points to them.",
        "5. Regenerate outputs after edits.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _find_node(graph: KnowledgeGraph, target: str) -> Node | None:
    query = target.replace("\\", "/").lower()
    candidates = graph.nodes
    for node in candidates:
        if node.id.lower() == query or node.filePath.lower() == query:
            return node
    for node in candidates:
        if node.name.lower() == query:
            return node
    for node in candidates:
        haystack = f"{node.id} {node.filePath} {node.name}".replace("\\", "/").lower()
        if query in haystack:
            return node
    return None


def _adjacency(graph: KnowledgeGraph) -> tuple[dict[str, list[tuple[int, str]]], dict[str, list[tuple[int, str]]]]:
    index = {node.id: i for i, node in enumerate(graph.nodes)}
    outgoing: dict[str, list[tuple[int, str]]] = defaultdict(list)
    incoming: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for edge in graph.edges:
        if edge.source in index and edge.target in index:
            outgoing[edge.source].append((index[edge.target], edge.type))
            incoming[edge.target].append((index[edge.source], edge.type))
    return outgoing, incoming


def _node_layers(graph: KnowledgeGraph) -> dict[str, object]:
    layer_of = {}
    for layer in graph.layers:
        for node_id in layer.nodeIds:
            layer_of[node_id] = layer
    file_layer = {}
    for node in graph.nodes:
        if node.id in layer_of and node.filePath:
            file_layer.setdefault(node.filePath, layer_of[node.id])
    for node in graph.nodes:
        if node.id not in layer_of and node.filePath in file_layer:
            layer_of[node.id] = file_layer[node.filePath]
    return layer_of


def _file_nodes(graph: KnowledgeGraph) -> dict[str, Node]:
    out = {}
    for node in graph.nodes:
        if node.type in FILE_LEVEL_TYPES:
            out[node.filePath or node.id] = node
    return out


def _symbols_in_file(graph: KnowledgeGraph, path: str) -> list[Node]:
    return [node for node in graph.nodes if node.filePath == path and node.type in _SYMBOL_TYPES]


def _append_edges(lines: list[str], title: str, nodes: list[Node], typed_edges: list[tuple[int, str]]) -> None:
    lines.append(f"### {title}")
    if not nodes:
        lines.append("- None detected.")
        return
    for node, (_idx, edge_type) in zip(nodes[:12], typed_edges[:12]):
        lines.append(f"- `{_display_node(node)}` via `{edge_type}`")
    if len(nodes) > 12:
        lines.append(f"- ... {len(nodes) - 12} more")


def _next_reads(
    graph: KnowledgeGraph,
    node: Node,
    outgoing: dict[str, list[tuple[int, str]]],
    incoming: dict[str, list[tuple[int, str]]],
) -> list[Node]:
    seen = {node.id}
    out = []
    for idx, _ty in outgoing[node.id] + incoming[node.id]:
        near = graph.nodes[idx]
        key = near.filePath or near.id
        if key in seen:
            continue
        seen.add(key)
        out.append(near)
    return out


def _walk_neighbors(
    graph: KnowledgeGraph,
    start_id: str,
    outgoing: dict[str, list[tuple[int, str]]],
    incoming: dict[str, list[tuple[int, str]]],
    depth: int,
) -> list[Node]:
    visited = {start_id}
    result: list[Node] = []
    q = deque([(start_id, 0)])
    while q:
        node_id, dist = q.popleft()
        if dist >= depth:
            continue
        for idx, _ty in outgoing[node_id] + incoming[node_id]:
            node = graph.nodes[idx]
            if node.id in visited:
                continue
            visited.add(node.id)
            result.append(node)
            q.append((node.id, dist + 1))
    return result


def _changed_paths(graph: KnowledgeGraph, root: Path | None) -> list[str]:
    changed_ids = getattr(graph, "changed", None) or set()
    paths = {node.filePath for node in graph.nodes if node.id in changed_ids and node.filePath}
    paths.update(_git_changed_paths(root))
    known = {node.filePath for node in graph.nodes if node.filePath}
    return sorted(path for path in paths if path in known)


def _git_changed_paths(root: Path | None) -> set[str]:
    if root is None:
        return set()
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return set()
    if out.returncode != 0:
        return set()
    return {line.strip().replace("\\", "/") for line in out.stdout.splitlines() if line.strip()}


def _source_preview(root: Path | None, node: Node, radius: int = 8) -> str:
    if root is None or not node.filePath:
        return ""
    path = root / node.filePath
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    if node.lineRange:
        start = max(1, node.lineRange[0] - radius)
        end = min(len(lines), node.lineRange[-1] + radius)
    else:
        start, end = 1, min(len(lines), 80)
    width = len(str(end))
    return "\n".join(f"{i:>{width}}  {lines[i - 1]}" for i in range(start, end + 1))


def _display_node(node: Node) -> str:
    if node.filePath and node.name and node.name not in {node.filePath, Path(node.filePath).name}:
        return f"{node.filePath}:{node.name}"
    return node.filePath or node.name or node.id


def _short_id(node_id: str) -> str:
    return node_id.split(":", 1)[-1]


def _sentence(text: str | None) -> str:
    value = (text or "").strip().replace("\n", " ")
    return value if value else ""
