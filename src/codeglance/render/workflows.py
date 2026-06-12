"""Deterministic workflow renderers: explain, impact, and onboarding reports."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

from ..schema import FILE_LEVEL_TYPES, KnowledgeGraph, Node

_SYMBOL_TYPES = {"class", "function", "module", "endpoint", "schema", "table", "resource"}


@dataclass(frozen=True)
class ReviewFinding:
    """One deterministic graph/output review finding."""

    severity: str
    title: str
    detail: str
    hint: str = ""


def render_review(graph: KnowledgeGraph, root: Path | None = None, output_dir: Path | None = None) -> str:
    """Render a Markdown quality report for the graph and generated outputs."""
    root = root.resolve() if root else None
    output_dir = output_dir.resolve() if output_dir else (root / ".codeglance" / "outputs" if root else None)
    findings = review_findings(graph, root, output_dir)
    counts = Counter(f.severity for f in findings)
    stats = graph.stats()
    file_nodes = [n for n in graph.nodes if n.type in FILE_LEVEL_TYPES and n.filePath]

    lines = [
        f"# Codeglance Review: {graph.project.name}",
        "",
        "## Summary",
        f"- status: {_review_status(counts)}",
        f"- issues: {counts['issue']}",
        f"- warnings: {counts['warning']}",
        f"- notes: {counts['note']}",
        f"- nodes: {stats['nodes']}",
        f"- edges: {stats['edges']}",
        f"- layers: {stats['layers']}",
        f"- file-level nodes: {len(file_nodes)}",
        f"- analyzed: {graph.project.analyzedAt or 'unknown'}",
        f"- commit: {(graph.project.gitCommitHash or 'unknown')[:12]}",
        "",
    ]
    if output_dir:
        lines.append(f"- output folder: `{_rel(root, output_dir)}`")
        lines.append("")

    if findings:
        for severity in ("issue", "warning", "note"):
            group = [f for f in findings if f.severity == severity]
            if not group:
                continue
            lines.extend(["", f"## {severity.title()}s"])
            for finding in group:
                lines.append(f"- **{finding.title}**: {finding.detail}")
                if finding.hint:
                    lines.append(f"  - Fix: {finding.hint}")
    else:
        lines.extend(["## Findings", "No review findings. The graph and generated outputs look consistent."])

    lines.extend([
        "",
        "## Pre-Push Checklist",
        "- Regenerate outputs after code structure changes.",
        "- Open `glance.html` and verify overview, folder drill-down, inspector, and terminal.",
        "- Open `index.html` and confirm expected HTML/Markdown/JSON artifacts are listed.",
        "- Run project tests and keep this report with the generated bundle when useful.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def review_findings(
    graph: KnowledgeGraph,
    root: Path | None = None,
    output_dir: Path | None = None,
) -> list[ReviewFinding]:
    """Return deterministic graph/output review findings."""
    findings: list[ReviewFinding] = []
    issues, warnings = graph.validate()
    findings.extend(ReviewFinding("issue", "Schema issue", issue) for issue in issues[:25])
    if len(issues) > 25:
        findings.append(ReviewFinding("issue", "Schema issue limit", f"{len(issues) - 25} more schema issues omitted."))
    missing_summary = [w for w in warnings if "missing summary" in w]
    orphan_warnings = [w for w in warnings if "has no edges" in w]
    other_warnings = [w for w in warnings if w not in missing_summary and w not in orphan_warnings]
    if missing_summary:
        findings.append(ReviewFinding(
            "warning",
            "Missing summaries",
            f"{len(missing_summary)} node(s) have no summary.",
            "Run with deterministic fallbacks or optional LLM enrichment for better context.",
        ))
    findings.extend(ReviewFinding("warning", "Schema warning", w) for w in other_warnings[:15])

    _review_source_files(graph, root, findings)
    _review_orphans(graph, orphan_warnings, findings)
    _review_layers(graph, findings)
    _review_folders(graph, findings)
    _review_outputs(graph, root, output_dir, findings)
    return findings


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


def _git_head(root: Path | None) -> str:
    if root is None:
        return ""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _review_status(counts: Counter[str]) -> str:
    if counts["issue"]:
        return "needs attention"
    if counts["warning"]:
        return "usable with warnings"
    return "clean"


def _review_source_files(graph: KnowledgeGraph, root: Path | None, findings: list[ReviewFinding]) -> None:
    if root is None:
        return
    missing = []
    for node in graph.nodes:
        if node.type in FILE_LEVEL_TYPES and node.filePath and not (root / node.filePath).is_file():
            missing.append(node.filePath)
    if missing:
        sample = ", ".join(f"`{p}`" for p in sorted(set(missing))[:8])
        findings.append(ReviewFinding(
            "issue",
            "Missing source files",
            f"{len(set(missing))} file-level node(s) point to files that no longer exist: {sample}.",
            "Regenerate the graph from the current checkout.",
        ))


def _review_orphans(graph: KnowledgeGraph, orphan_warnings: list[str], findings: list[ReviewFinding]) -> None:
    file_nodes = [n for n in graph.nodes if n.type in FILE_LEVEL_TYPES]
    if not graph.nodes:
        findings.append(ReviewFinding("issue", "Empty graph", "The graph has no nodes.", "Check the input path and ignore rules."))
        return
    if not graph.edges and len(graph.nodes) > 1:
        findings.append(ReviewFinding(
            "warning",
            "No graph edges",
            "The graph has multiple nodes but no relationships.",
            "Review import/dependency extraction for this language or repo shape.",
        ))
    if file_nodes:
        orphan_ids = {w.split("'")[1] for w in orphan_warnings if "'" in w}
        orphan_files = [n for n in file_nodes if n.id in orphan_ids]
        ratio = len(orphan_files) / len(file_nodes)
        if ratio >= 0.65 and len(file_nodes) >= 8:
            findings.append(ReviewFinding(
                "warning",
                "Orphan-heavy graph",
                f"{len(orphan_files)} of {len(file_nodes)} file-level nodes have no edges.",
                "This may be normal for docs/config repos; otherwise improve import/dependency detection.",
            ))


def _review_layers(graph: KnowledgeGraph, findings: list[ReviewFinding]) -> None:
    ids = {n.id for n in graph.nodes}
    edge_ids = {e.source for e in graph.edges} | {e.target for e in graph.edges}
    if not graph.layers and graph.nodes:
        findings.append(ReviewFinding(
            "warning",
            "No layers",
            "The graph has nodes but no architecture layers.",
            "Regenerate with current layer detection or inspect unusual repo layout.",
        ))
        return
    for layer in graph.layers:
        present = [nid for nid in layer.nodeIds if nid in ids]
        if len(present) > 120:
            findings.append(ReviewFinding(
                "note",
                "Large layer",
                f"`{layer.name}` contains {len(present)} node(s).",
                "Use folder drill-down and consider adding clearer package/domain grouping.",
            ))
        if present:
            orphan_count = len([nid for nid in present if nid not in edge_ids])
            if orphan_count / len(present) >= 0.75 and len(present) >= 12:
                findings.append(ReviewFinding(
                    "warning",
                    "Orphan-heavy layer",
                    f"`{layer.name}` has {orphan_count} of {len(present)} node(s) without edges.",
                    "Check whether this layer is mostly docs/config or whether dependency extraction is missing links.",
                ))


def _review_folders(graph: KnowledgeGraph, findings: list[ReviewFinding]) -> None:
    folders: Counter[str] = Counter()
    for node in graph.nodes:
        if node.type not in FILE_LEVEL_TYPES or not node.filePath:
            continue
        parts = node.filePath.split("/")
        if len(parts) >= 2:
            folders["/".join(parts[:2])] += 1
        elif parts:
            folders[parts[0]] += 1
    for folder, count in folders.most_common(8):
        if count >= 80:
            findings.append(ReviewFinding(
                "note",
                "Large folder",
                f"`{folder}` contains {count} file-level node(s).",
                "The folder drill view should stay nested; validate breadcrumbs and up navigation for this folder.",
            ))


def _review_outputs(
    graph: KnowledgeGraph,
    root: Path | None,
    output_dir: Path | None,
    findings: list[ReviewFinding],
) -> None:
    if output_dir is None:
        return
    expected = {
        "glance.html",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
        "llms.txt",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
    }
    if not output_dir.is_dir():
        findings.append(ReviewFinding(
            "warning",
            "Missing output folder",
            f"`{_rel(root, output_dir)}` does not exist.",
            "Run `codeglance generate . --out .codeglance/outputs`.",
        ))
        return
    missing = sorted(name for name in expected if not (output_dir / name).is_file())
    if missing:
        findings.append(ReviewFinding(
            "warning",
            "Incomplete output bundle",
            "Missing expected artifact(s): " + ", ".join(f"`{name}`" for name in missing) + ".",
            "Run `codeglance generate . --profile all` before sharing.",
        ))
    _review_output_meta(graph, root, output_dir, findings)
    glance = output_dir / "glance.html"
    if glance.is_file():
        text = glance.read_text(encoding="utf-8", errors="ignore")
        for marker in ("const DATA = ", 'id="btnReload"', "startOutputRefreshWatch"):
            if marker not in text:
                findings.append(ReviewFinding(
                    "warning",
                    "Glance HTML missing runtime marker",
                    f"`glance.html` does not contain `{marker}`.",
                    "Regenerate outputs with the current package version.",
                ))


def _review_output_meta(
    graph: KnowledgeGraph,
    root: Path | None,
    output_dir: Path,
    findings: list[ReviewFinding],
) -> None:
    meta_path = output_dir / "meta.json"
    if not meta_path.is_file():
        return
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        findings.append(ReviewFinding("issue", "Invalid metadata", "`meta.json` is not valid JSON."))
        return
    if meta.get("lastAnalyzedAt") != graph.project.analyzedAt:
        findings.append(ReviewFinding(
            "warning",
            "Stale metadata timestamp",
            "`meta.json` does not match the current graph analysis timestamp.",
            "Regenerate the output bundle.",
        ))
    if meta.get("version") != graph.version:
        findings.append(ReviewFinding(
            "warning",
            "Metadata version mismatch",
            f"`meta.json` version `{meta.get('version')}` does not match graph version `{graph.version}`.",
            "Regenerate the output bundle.",
        ))
    analyzed_files = sum(1 for n in graph.nodes if n.type in FILE_LEVEL_TYPES)
    if meta.get("analyzedFiles") != analyzed_files:
        findings.append(ReviewFinding(
            "warning",
            "Analyzed file count mismatch",
            f"`meta.json` reports {meta.get('analyzedFiles')} file(s), graph has {analyzed_files}.",
            "Regenerate the output bundle.",
        ))
    current = _git_head(root)
    meta_commit = meta.get("gitCommitHash") or ""
    if current and meta_commit and current != meta_commit:
        findings.append(ReviewFinding(
            "warning",
            "Output commit mismatch",
            f"`meta.json` was generated for `{meta_commit[:12]}`, current HEAD is `{current[:12]}`.",
            "Regenerate outputs after committing or before sharing.",
        ))


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


def _rel(root: Path | None, path: Path) -> str:
    if root is None:
        return path.as_posix()
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
