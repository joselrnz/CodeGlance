"""Generate a complete local output folder from one analysis pass."""

from __future__ import annotations

import html
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .graph import analyze
from .render import render_context, render_interactive, render_static, render_wiki
from .schema import COMPLEXITY_VALUES, EDGE_WEIGHTS, FILE_LEVEL_TYPES, NODE_TYPES, KnowledgeGraph

OUTPUT_PROFILES = {
    "minimal": (
        "llms.txt",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "glance.html",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    ),
    "human": ("llms.txt", "glance.html", "wiki.html", "knowledge-graph.json", "meta.json", "index.html"),
    "agent": (
        "llms.txt",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
    ),
    "all": (
        "llms.txt",
        "glance.html",
        "graph.static.html",
        "wiki.html",
        "context.md",
        "agent.md",
        "llm-context.schema.json",
        "knowledge-graph.toon",
        "knowledge-graph.json",
        "meta.json",
        "index.html",
    ),
}
LEGACY_OUTPUT_NAMES = {"graph.html"}
KNOWN_OUTPUT_NAMES = frozenset({name for names in OUTPUT_PROFILES.values() for name in names} | LEGACY_OUTPUT_NAMES)


@dataclass(frozen=True)
class GeneratedOutput:
    """A generated artifact written by `codeglance generate`."""

    label: str
    path: Path
    kind: str


def generate_outputs(
    root: str | Path,
    out_dir: str | Path,
    use_llm: bool = False,
    model: str | None = None,
    full: bool = False,
    profile: str = "minimal",
    progress=None,
) -> tuple[KnowledgeGraph, list[GeneratedOutput]]:
    """Analyze `root` once and write all human/agent outputs into `out_dir`."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"project root not found: {root}")
    if profile not in OUTPUT_PROFILES:
        profiles = ", ".join(sorted(OUTPUT_PROFILES))
        raise ValueError(f"unknown output profile {profile!r}; expected one of: {profiles}")
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    _clear_known_outputs(out)

    graph = analyze(root, use_llm=use_llm, model=model, progress=progress, full=full)
    all_outputs = [
        GeneratedOutput("LLM entrypoint", out / "llms.txt", "Text"),
        GeneratedOutput("Glance interactive visual", out / "glance.html", "HTML"),
        GeneratedOutput("Static graph", out / "graph.static.html", "HTML"),
        GeneratedOutput("Wiki", out / "wiki.html", "HTML"),
        GeneratedOutput("Full agent context", out / "context.md", "Markdown"),
        GeneratedOutput("Compact agent context", out / "agent.md", "Markdown"),
        GeneratedOutput("LLM context schema", out / "llm-context.schema.json", "JSON"),
        GeneratedOutput("Knowledge graph TOON", out / "knowledge-graph.toon", "TOON"),
        GeneratedOutput("Knowledge graph JSON", out / "knowledge-graph.json", "JSON"),
        GeneratedOutput("Metadata", out / "meta.json", "JSON"),
        GeneratedOutput("Output index", out / "index.html", "HTML"),
    ]
    selected = set(OUTPUT_PROFILES[profile])
    outputs = [item for item in all_outputs if item.path.name in selected]

    if "llms.txt" in selected:
        (out / "llms.txt").write_text(build_llms_txt(root, outputs), encoding="utf-8")
    if "glance.html" in selected:
        (out / "glance.html").write_text(render_interactive(graph, root), encoding="utf-8")
    if "graph.static.html" in selected:
        (out / "graph.static.html").write_text(render_static(graph, root), encoding="utf-8")
    if "wiki.html" in selected:
        (out / "wiki.html").write_text(render_wiki(graph, root), encoding="utf-8")
    if "context.md" in selected:
        (out / "context.md").write_text(render_context(graph, root, mode="full"), encoding="utf-8")
    if "agent.md" in selected:
        (out / "agent.md").write_text(render_context(graph, root, mode="agent"), encoding="utf-8")
    if "llm-context.schema.json" in selected:
        (out / "llm-context.schema.json").write_text(
            json.dumps(build_llm_context_schema(root, outputs), indent=2),
            encoding="utf-8",
        )
    if "knowledge-graph.toon" in selected:
        (out / "knowledge-graph.toon").write_text(build_knowledge_graph_toon(graph), encoding="utf-8")
    if "knowledge-graph.json" in selected:
        graph.save(out / "knowledge-graph.json")
    if "meta.json" in selected:
        _write_meta(out / "meta.json", graph)
    if "index.html" in selected:
        (out / "index.html").write_text(build_output_index(root, outputs), encoding="utf-8")
    return graph, outputs


def build_llms_txt(root: Path, outputs: list[GeneratedOutput]) -> str:
    """Build a tiny LLM entrypoint that points agents to the right generated artifacts."""
    by_name = {item.path.name: item for item in outputs}
    lines = [
        f"# {root.name}",
        "",
        "> Generated by codeglance. Read this file first, then follow the smallest useful context tier.",
        "",
        "## Read Order",
    ]
    read_order = [
        ("agent.md", "compact repo map, read order, dependency hotspots, and agent rules"),
        ("llm-context.schema.json", "machine-readable contract for this output bundle"),
        ("knowledge-graph.toon", "compact TOON graph for LLM prompt context"),
        ("context.md", "full markdown map when compact context is not enough"),
        ("knowledge-graph.json", "complete graph for tools and structured retrieval"),
        ("glance.html", "interactive visual codebase map for inspection"),
        ("wiki.html", "human-readable architecture wiki"),
    ]
    for name, description in read_order:
        if name in by_name:
            lines.append(f"- `{name}` - {description}")
    lines.extend([
        "",
        "## Rules",
        "- Start with `agent.md`; do not read full source unless the map points to specific files.",
        "- Use `llm-context.schema.json` to understand artifact meanings and graph fields.",
        "- Use `knowledge-graph.toon` for compact prompt context; use JSON for parsers/tools.",
        "- Regenerate with `codeglance generate . --out .codeglance/outputs` after structural edits.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def build_llm_context_schema(root: Path, outputs: list[GeneratedOutput]) -> dict:
    """Build the structured LLM contract for generated context artifacts."""
    generated = sorted(item.path.name for item in outputs)
    return {
        "schema": "codeglance.llm-context",
        "version": "1.0",
        "project": root.name,
        "purpose": "Help coding agents understand a repository with minimal token use before opening source.",
        "readOrder": [
            "llms.txt",
            "agent.md",
            "llm-context.schema.json",
            "context.md",
            "knowledge-graph.toon",
            "knowledge-graph.json",
            "selected source files",
        ],
        "generatedArtifacts": generated,
        "artifactContracts": [
            {
                "path": "llms.txt",
                "format": "text",
                "tier": 0,
                "audience": "agent",
                "contains": ["read order", "artifact pointers", "usage rules"],
            },
            {
                "path": "agent.md",
                "format": "markdown",
                "tier": 1,
                "audience": "agent",
                "contains": [
                    "snapshot",
                    "AI reading protocol",
                    "context budget",
                    "read-first files",
                    "architecture layers",
                    "changed files",
                    "dependency hotspots",
                ],
                "doesNotContain": ["full source code", "complete per-file catalog"],
            },
            {
                "path": "context.md",
                "format": "markdown",
                "tier": 2,
                "audience": "agent",
                "contains": ["read-first files", "file dependency map", "per-file summaries", "symbols"],
                "useWhen": "Use when agent.md is not enough to choose files.",
            },
            {
                "path": "knowledge-graph.toon",
                "format": "toon",
                "tier": 3,
                "audience": "agent",
                "contains": ["project", "stats", "nodes table", "edges table", "layers table", "tour table"],
                "useWhen": "Use when an LLM needs structured graph context with fewer repeated field names than JSON.",
            },
            {
                "path": "knowledge-graph.json",
                "format": "json",
                "tier": 4,
                "audience": "tool",
                "contains": ["project", "nodes", "edges", "layers", "tour"],
                "useWhen": "Use for structured retrieval, graph traversal, and custom tools.",
            },
            {
                "path": "glance.html",
                "format": "html",
                "tier": "human",
                "audience": "human",
                "contains": ["interactive graph", "search", "filters", "guided tour"],
            },
        ],
        "agentProtocol": [
            "Read llms.txt and agent.md first.",
            "Inspect changed files before broad search.",
            "Follow dependency hotspots one hop at a time.",
            "Open source only after the generated map names specific files.",
            "Run targeted tests and regenerate outputs after code shape changes.",
        ],
        "knowledgeGraphSchema": {
            "version": "semantic version for this graph file",
            "project": {
                "name": "repository or folder name",
                "languages": "detected language ids",
                "frameworks": "detected framework ids",
                "description": "short generated repository summary",
                "analyzedAt": "ISO timestamp",
                "gitCommitHash": "current commit hash when available",
            },
            "nodes": {
                "id": "stable unique node id",
                "type": "one of nodeTypes",
                "name": "display name",
                "filePath": "repo-relative path when applicable",
                "summary": "short deterministic or LLM-enriched summary",
                "tags": "language/category/path tags",
                "complexity": "one of complexityValues",
                "lineRange": "optional [startLine, endLine]",
                "signature": "optional declaration signature",
                "docstring": "optional source docstring or leading comment",
            },
            "edges": {
                "source": "source node id",
                "target": "target node id",
                "type": "relationship type",
                "direction": "usually directed",
                "weight": "layout/relevance weight",
            },
            "layers": {
                "id": "stable layer id",
                "name": "architecture/group name",
                "description": "short layer summary",
                "nodeIds": "node ids in this layer",
            },
            "tour": {
                "order": "display order",
                "title": "tour step title",
                "description": "why this step matters",
                "nodeIds": "nodes to inspect",
            },
        },
        "nodeTypes": sorted(NODE_TYPES),
        "fileLevelNodeTypes": sorted(FILE_LEVEL_TYPES),
        "complexityValues": sorted(COMPLEXITY_VALUES),
        "edgeTypes": sorted(EDGE_WEIGHTS),
        "outputProfiles": {key: list(value) for key, value in OUTPUT_PROFILES.items()},
    }


def build_knowledge_graph_toon(graph: KnowledgeGraph) -> str:
    """Build a compact TOON-style graph representation for LLM prompt context."""
    stats = graph.stats()
    lines = [
        "schema: codeglance.knowledge-graph.toon",
        "version: 1.0",
        "",
        "project:",
        f"  name: {_toon_value(graph.project.name)}",
        f"  languages[{len(graph.project.languages)}]: {_toon_list(graph.project.languages)}",
        f"  frameworks[{len(graph.project.frameworks)}]: {_toon_list(graph.project.frameworks)}",
        f"  analyzedAt: {_toon_value(graph.project.analyzedAt)}",
        f"  gitCommitHash: {_toon_value(graph.project.gitCommitHash)}",
        f"  description: {_toon_value(graph.project.description)}",
        "",
        "stats:",
        f"  nodes: {stats['nodes']}",
        f"  edges: {stats['edges']}",
        f"  layers: {stats['layers']}",
        f"  tourSteps: {stats['tourSteps']}",
        "",
        f"nodes[{len(graph.nodes)}]{{id,type,name,path,summary,complexity,tags}}:",
    ]
    for node in graph.nodes:
        lines.append(
            "  "
            + ",".join([
                _toon_value(node.id),
                _toon_value(node.type),
                _toon_value(node.name),
                _toon_value(node.filePath),
                _toon_value(node.summary),
                _toon_value(node.complexity),
                _toon_value("|".join(node.tags)),
            ])
        )
    lines.extend(["", f"edges[{len(graph.edges)}]{{source,target,type,weight}}:"])
    for edge in graph.edges:
        lines.append(
            "  "
            + ",".join([
                _toon_value(edge.source),
                _toon_value(edge.target),
                _toon_value(edge.type),
                f"{edge.weight:g}",
            ])
        )
    lines.extend(["", f"layers[{len(graph.layers)}]{{id,name,count,description}}:"])
    for layer in graph.layers:
        lines.append(
            "  "
            + ",".join([
                _toon_value(layer.id),
                _toon_value(layer.name),
                str(len(layer.nodeIds)),
                _toon_value(layer.description),
            ])
        )
    lines.extend(["", f"tour[{len(graph.tour)}]{{order,title,nodes,description}}:"])
    for step in graph.tour:
        lines.append(
            "  "
            + ",".join([
                str(step.order),
                _toon_value(step.title),
                _toon_value("|".join(step.nodeIds)),
                _toon_value(step.description),
            ])
        )
    return "\n".join(lines).rstrip() + "\n"


def _toon_list(values: list[str]) -> str:
    """Return a comma-separated TOON value list."""
    return ",".join(_toon_value(value) for value in values)


def _toon_value(value: object) -> str:
    """Return a compact scalar for TOON table cells, quoting only when needed."""
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if not text:
        return '""'
    if any(ch in text for ch in [",", ":", "{", "}", "[", "]", "#", '"']):
        return json.dumps(text, ensure_ascii=False)
    return text


def build_output_index(root: Path, outputs: list[GeneratedOutput]) -> str:
    """Build an offline-friendly index for a generated output folder."""
    rows = []
    for item in outputs:
        rel = item.path.name
        rows.append(
            '<a class="item" href="{href}">'
            '<span class="kind">{kind}</span>'
            '<span class="name">{name}</span>'
            '<span class="label">{label}</span>'
            "</a>".format(
                href=html.escape(rel),
                kind=html.escape(item.kind),
                name=html.escape(rel),
                label=html.escape(item.label),
            )
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>codeglance outputs · {html.escape(root.name)}</title>
<style>
  :root {{ color-scheme:dark; --bg:#0b0f14; --panel:#141b24; --line:#263342;
    --text:#e8edf2; --muted:#94a3b8; --accent:#5ba4cf; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ width:min(920px,100%); margin:0 auto; padding:22px; }}
  header {{ padding:12px 0 18px; border-bottom:1px solid var(--line); margin-bottom:16px; }}
  h1 {{ margin:0 0 6px; font-size:24px; letter-spacing:0; }}
  .sub {{ color:var(--muted); font-size:13px; word-break:break-word; }}
  .list {{ display:grid; gap:9px; }}
  .item {{ display:grid; grid-template-columns:96px 1fr 1.4fr; gap:12px; align-items:center;
    min-height:48px; padding:10px 12px; color:var(--text); text-decoration:none;
    background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
  .item:hover {{ border-color:var(--accent); }}
  .kind {{ color:var(--accent); font-size:11px; font-weight:700; text-transform:uppercase; }}
  .name {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:13px; }}
  .label {{ color:var(--muted); font-size:13px; }}
  footer {{ color:var(--muted); font-size:12px; padding:18px 0 4px; }}
  @media (max-width:640px) {{
    main {{ padding:16px; }}
    .item {{ grid-template-columns:1fr; gap:4px; }}
  }}
</style>
</head>
<body>
<main>
  <header>
    <h1>codeglance outputs</h1>
    <div class="sub">{html.escape(str(root))}</div>
  </header>
  <section class="list">{''.join(rows)}</section>
  <footer>Generated {html.escape(time.strftime("%Y-%m-%d %H:%M"))}</footer>
</main>
</body>
</html>
"""


def mirror_to_codeglance(root: Path, outputs: list[GeneratedOutput]) -> None:
    """Copy generated graph metadata back to `.codeglance` for dashboard compatibility."""
    target = root / ".codeglance"
    target.mkdir(exist_ok=True)
    for name in ("knowledge-graph.json", "meta.json"):
        src = next((item.path for item in outputs if item.path.name == name), None)
        if src and src.is_file():
            shutil.copy2(src, target / name)


def _clear_known_outputs(out: Path) -> None:
    """Remove stale files from previous profile runs without touching unrelated files."""
    for name in KNOWN_OUTPUT_NAMES:
        path = out / name
        if path.is_file():
            path.unlink()


def _write_meta(path: Path, graph: KnowledgeGraph) -> None:
    meta = {
        "lastAnalyzedAt": graph.project.analyzedAt,
        "gitCommitHash": graph.project.gitCommitHash,
        "version": graph.version,
        "analyzedFiles": sum(1 for n in graph.nodes if n.type in FILE_LEVEL_TYPES),
    }
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
