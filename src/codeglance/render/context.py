"""AI-context renderer — a compact, dependency-first "codebase map" for LLM agents.

Instead of a graph (for exploring) or a wiki (for humans), this emits terse Markdown an agent can
read **once** to grasp a repository: the most-connected files to read first, a file -> file
dependency list, and a one-line summary + defined symbols + imports/used-by for every file. No
source code, a small fraction of the tokens of the repo — so an agent understands the shape and
the wiring without crawling every line.
"""

from __future__ import annotations

from collections import defaultdict

_FILE_LEVEL = {"file", "config", "document", "service", "pipeline", "table", "schema", "resource", "endpoint"}
_SYMBOL = {"function", "class", "module"}


def _context_index(vm: dict) -> dict:
    """Build the shared file/dependency index used by the full and agent context renderers."""
    nodes = vm.get("nodes", []) or []
    edges = vm.get("edges", []) or []

    path_of = [n.get("path") or "" for n in nodes]
    defines: dict[str, list[str]] = defaultdict(list)
    summary_of: dict[str, str] = {}
    type_of: dict[str, str] = {}
    complexity_of: dict[str, str] = {}
    files: list[str] = []
    seen: set[str] = set()
    for i, n in enumerate(nodes):
        p = path_of[i]
        if not p:
            continue
        if n.get("type") in _FILE_LEVEL and p not in seen:
            seen.add(p)
            files.append(p)
            summary_of[p] = (n.get("summary") or "").strip()
            type_of[p] = n.get("type", "file")
            complexity_of[p] = n.get("complexity", "")
        if n.get("type") in _SYMBOL and n.get("name"):
            defines[p].append(n["name"])

    # cross-file dependencies, aggregated from the edges
    out_deps: dict[str, set] = defaultdict(set)
    in_deps: dict[str, set] = defaultdict(set)
    for a, b, _ty in edges:
        pa, pb = path_of[a], path_of[b]
        if pa and pb and pa != pb:
            out_deps[pa].add(pb)
            in_deps[pb].add(pa)
    for p in list(out_deps) + list(in_deps):  # include files only seen via edges
        if p and p not in seen:
            seen.add(p)
            files.append(p)
            summary_of.setdefault(p, "")
            type_of.setdefault(p, "file")
    files = sorted(set(files))

    return {
        "files": files,
        "out_deps": out_deps,
        "in_deps": in_deps,
        "defines": defines,
        "summary_of": summary_of,
        "type_of": type_of,
        "complexity_of": complexity_of,
    }


def _ranked_files(index: dict) -> list[str]:
    """Return files ordered by cross-file connectivity, highest first."""
    out_deps = index["out_deps"]
    in_deps = index["in_deps"]
    return sorted(index["files"], key=lambda p: (-(len(out_deps[p]) + len(in_deps[p])), p))


def render_context_md(vm: dict, mode: str = "full") -> str:
    """Render a view model into a compact dependency+summary Markdown map for AI context."""
    if mode == "agent":
        return render_agent_context_md(vm)

    project = vm.get("project", {})
    stats = vm.get("stats", {})
    index = _context_index(vm)
    files = index["files"]
    out_deps = index["out_deps"]
    in_deps = index["in_deps"]
    defines = index["defines"]
    summary_of = index["summary_of"]
    type_of = index["type_of"]
    complexity_of = index["complexity_of"]

    lines: list[str] = []
    name = project.get("name", "project")
    lines.append(f"# {name} — codebase map (AI context)")
    if project.get("description"):
        lines.append(f"> {project['description']}")
    langs = ", ".join(project.get("languages", []) or []) or "—"
    lines.append(f"{len(files)} files · {sum(len(v) for v in out_deps.values())} cross-file deps · "
                 f"{stats.get('layers', 0)} layers · languages: {langs}")
    lines.append("")

    # read-first: files ranked by total connections
    ranked = _ranked_files(index)
    hubs = [p for p in ranked if (len(out_deps[p]) + len(in_deps[p])) > 0][:8]
    if hubs:
        lines.append("## Read first (most-connected files)")
        for p in hubs:
            desc = f" — {summary_of[p]}" if summary_of.get(p) else ""
            lines.append(f"- `{p}`{desc}  ({len(out_deps[p])} out, {len(in_deps[p])} in)")
        lines.append("")

    # dependency map
    dep_files = sorted(p for p in files if out_deps[p])
    if dep_files:
        lines.append("## Dependency map (file -> depends on)")
        for p in dep_files:
            lines.append(f"- `{p}` -> " + ", ".join(sorted(out_deps[p])))
        lines.append("")

    # per-file detail
    lines.append("## Files")
    for p in files:
        cx = complexity_of.get(p, "")
        lines.append(f"### `{p}`  [{type_of.get(p, 'file')}" + (f" · {cx}" if cx else "") + "]")
        if summary_of.get(p):
            lines.append(summary_of[p])
        if defines.get(p):
            lines.append("defines: " + ", ".join(defines[p][:20]))
        rel = []
        if out_deps[p]:
            rel.append("imports: " + ", ".join(sorted(out_deps[p])))
        if in_deps[p]:
            rel.append("used-by: " + ", ".join(sorted(in_deps[p])))
        if rel:
            lines.append(" · ".join(rel))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_agent_context_md(vm: dict) -> str:
    """Render a very small, durable handoff for agents that should not read the whole repo."""
    nodes = vm.get("nodes", []) or []
    project = vm.get("project", {})
    stats = vm.get("stats", {})
    layers = vm.get("layers", []) or []
    index = _context_index(vm)
    files = index["files"]
    out_deps = index["out_deps"]
    in_deps = index["in_deps"]
    summary_of = index["summary_of"]

    name = project.get("name", "project")
    langs = ", ".join(project.get("languages", []) or []) or "unknown"
    dep_count = sum(len(v) for v in out_deps.values())
    analyzed_at = project.get("analyzedAt") or "unknown"
    commit = (project.get("gitCommitHash") or "")[:12] or "unknown"

    lines: list[str] = [
        f"# {name} — agent context",
    ]
    lines.extend([
        "",
        "## Snapshot",
        f"- files: {len(files)}; cross-file deps: {dep_count}; layers: {stats.get('layers', 0)}; languages: {langs}",
        f"- analyzed: {analyzed_at}; commit: {commit}",
        "- refresh after edits: `codeglance generate . --out .codeglance/outputs`",
        "- agent-only refresh: `codeglance context . --mode agent -o AGENTS.md`",
        "- human view: open `.codeglance/outputs/index.html` or run `codeglance serve .codeglance/outputs`",
        "",
        "## AI Reading Protocol",
        "- Map first; source last.",
        "- Changed files before broad search.",
        "- Follow Read First and Dependency Hotspots one hop at a time.",
        "- Open source only after this map points to it.",
        "- Test and regenerate after edits.",
        "",
        "## Context Budget",
        "- T1 `agent.md`: orientation.",
        "- T2 `context.md`: full map.",
        "- T3 selected source files.",
        "- T4 `knowledge-graph.json`: tools.",
        "",
    ])

    ranked = _ranked_files(index)
    hubs = [p for p in ranked if (len(out_deps[p]) + len(in_deps[p])) > 0][:5] or ranked[:5]
    if hubs:
        lines.append("## Read First")
        for p in hubs:
            summary = f" — {summary_of[p]}" if summary_of.get(p) else ""
            lines.append(f"- `{p}`{summary} ({len(out_deps[p])} out/{len(in_deps[p])} in)")
        lines.append("")

    if layers:
        lines.append("## Architecture")
        for layer in layers[:6]:
            desc = str(layer.get("description") or "").strip()
            if " layer " in f" {desc.lower()} " and "file" in desc.lower():
                desc = ""
            suffix = f" — {desc}" if desc else ""
            lines.append(f"- {layer.get('name', 'Layer')}: {layer.get('count', 0)} files{suffix}")
        lines.append("")

    changed_paths = []
    for i in vm.get("diffChanged", []) or []:
        if 0 <= i < len(nodes) and nodes[i].get("path"):
            changed_paths.append(nodes[i]["path"])
    changed_paths = sorted(set(changed_paths))
    if changed_paths:
        lines.append("## Changed Since Last Run")
        for p in changed_paths[:12]:
            summary = f" — {summary_of[p]}" if summary_of.get(p) else ""
            lines.append(f"- `{p}`{summary}")
        if len(changed_paths) > 12:
            lines.append(f"- ... {len(changed_paths) - 12} more")
        lines.append("")

    dep_files = [p for p in ranked if out_deps[p]][:5]
    if dep_files:
        lines.append("## Dependency Hotspots")
        for p in dep_files:
            deps = ", ".join(sorted(out_deps[p])[:5])
            suffix = " ..." if len(out_deps[p]) > 5 else ""
            lines.append(f"- `{p}` -> {deps}{suffix}")
        lines.append("")

    lines.extend([
        "## Agent Rules",
        "- Read this file first, then only open the files relevant to the requested change.",
        "- Prefer `codeglance context . --mode full` when you need the complete file/symbol map.",
        "- After code changes, regenerate the output bundle so human and agent views stay aligned.",
    ])
    return "\n".join(lines).rstrip() + "\n"
