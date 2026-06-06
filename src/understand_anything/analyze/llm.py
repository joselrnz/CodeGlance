"""Optional LLM enrichment (hybrid mode).

Everything here is best-effort and fully optional. With no `anthropic` package or no API key,
`enrich()` is a no-op and the deterministic graph is used as-is. Provider-agnostic by design;
only the Anthropic path is wired up for now.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..schema import KnowledgeGraph, FILE_LEVEL_TYPES

DEFAULT_MODEL = "claude-sonnet-4-6"


def is_available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except Exception:
        return False


def availability_hint() -> str:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return "ANTHROPIC_API_KEY is not set."
    try:
        import anthropic  # noqa: F401
    except Exception:
        return "The 'anthropic' package is not installed (pip install understand-anything-py[llm])."
    return "available"


def enrich(graph: KnowledgeGraph, root: str | Path | None = None, model: str | None = None,
           batch_size: int = 18, progress=None, only_paths: set[str] | None = None) -> int:
    """Fill in better summaries for file-level nodes. Returns number of summaries updated.

    If `only_paths` is given, only nodes whose filePath is in that set are enriched (used for
    incremental runs so we don't re-spend tokens on unchanged files).
    """
    if not is_available():
        return 0
    import anthropic

    model = model or DEFAULT_MODEL
    root = Path(root) if root else None
    client = anthropic.Anthropic()

    targets = [n for n in graph.nodes if n.type in FILE_LEVEL_TYPES
               and (only_paths is None or n.filePath in only_paths)]
    updated = 0
    batches = [targets[i:i + batch_size] for i in range(0, len(targets), batch_size)]

    for bi, batch in enumerate(batches):
        if progress:
            progress(f"  LLM enrichment batch {bi + 1}/{len(batches)} ({len(batch)} files)")
        items = []
        for n in batch:
            snippet = _snippet(root / n.filePath) if root and n.filePath else ""
            items.append({"id": n.id, "path": n.filePath, "current": n.summary, "head": snippet})
        prompt = _build_prompt(graph.project.name, items)
        try:
            resp = client.messages.create(
                model=model, max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            mapping = _parse_json_object(text)
        except Exception as exc:  # network/parse/etc. — skip the batch, keep deterministic summaries
            if progress:
                progress(f"  (batch {bi + 1} skipped: {exc})")
            continue
        by_id = {n.id: n for n in batch}
        for nid, summ in mapping.items():
            node = by_id.get(nid)
            if node and isinstance(summ, str) and summ.strip():
                node.summary = summ.strip()[:300]
                updated += 1
    return updated


def name_layers(layers, nodes, model: str | None = None, progress=None) -> int:
    """Improve layer names/descriptions from member files. Mutates layers; returns count updated."""
    if not is_available() or not layers:
        return 0
    model = model or DEFAULT_MODEL
    node_by_id = {n.id: n for n in nodes}
    items = []
    for layer in layers:
        members = [node_by_id[i] for i in layer.nodeIds[:10] if i in node_by_id]
        sample = ", ".join(m.name for m in members[:8])
        items.append({"id": layer.id, "current": layer.name, "files": sample})
    listing = "\n".join(f"- {it['id']} (now: \"{it['current']}\"): {it['files']}" for it in items)
    prompt = (
        "Below are architectural layers of a codebase, each with a few member file names. "
        "Give each a clear, human-friendly layer name (2-4 words) and a one-sentence description "
        "of its responsibility.\n\n"
        "Return ONLY a JSON object mapping each layer id to {\"name\": ..., \"description\": ...}.\n\n"
        f"{listing}"
    )
    mapping = _complete_json(prompt, model, progress)
    updated = 0
    by_id = {l.id: l for l in layers}
    for lid, val in (mapping or {}).items():
        layer = by_id.get(lid)
        if layer and isinstance(val, dict):
            if val.get("name"):
                layer.name = str(val["name"])[:60]
            if val.get("description"):
                layer.description = str(val["description"])[:300]
            updated += 1
    return updated


def narrate_tour(tour, nodes, project_desc: str = "", model: str | None = None, progress=None) -> int:
    """Rewrite tour step titles/descriptions into a narrative. Mutates tour; returns count."""
    if not is_available() or not tour:
        return 0
    model = model or DEFAULT_MODEL
    node_by_id = {n.id: n for n in nodes}
    lines = []
    for i, step in enumerate(tour):
        names = ", ".join(node_by_id[i2].name for i2 in step.nodeIds if i2 in node_by_id) or "(none)"
        lines.append(f"{i}: now \"{step.title}\" — files: {names}")
    prompt = (
        f"You are writing a guided code tour for: {project_desc}\n\n"
        "For each step below, write an engaging title (3-6 words) and a 1-2 sentence description "
        "that explains what the reader learns and why it matters, in reading order.\n\n"
        "Return ONLY a JSON object mapping each step index (as a string) to "
        "{\"title\": ..., \"description\": ...}.\n\n"
        + "\n".join(lines)
    )
    mapping = _complete_json(prompt, model, progress)
    updated = 0
    for key, val in (mapping or {}).items():
        try:
            i = int(key)
        except (TypeError, ValueError):
            continue
        if 0 <= i < len(tour) and isinstance(val, dict):
            if val.get("title"):
                tour[i].title = str(val["title"])[:80]
            if val.get("description"):
                tour[i].description = str(val["description"])[:400]
            updated += 1
    return updated


def _complete_json(prompt: str, model: str, progress=None) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return _parse_json_object(text)
    except Exception as exc:
        if progress:
            progress(f"  (LLM step skipped: {exc})")
        return {}


def _snippet(path: Path, max_lines: int = 25) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:max_lines]
        return "\n".join(lines)[:1200]
    except OSError:
        return ""


def _build_prompt(project: str, items: list[dict]) -> str:
    listing = "\n\n".join(
        f"### {it['id']}\npath: {it['path']}\ncurrent: {it['current']}\nhead:\n```\n{it['head']}\n```"
        for it in items
    )
    return (
        f"You are documenting the codebase '{project}'. For each file below, write ONE concise, "
        "specific sentence (max 25 words) describing what it does and its role. Avoid generic "
        "phrasing like 'this file contains code'.\n\n"
        "Return ONLY a JSON object mapping each node id to its summary string. No prose, no markdown.\n\n"
        f"{listing}"
    )


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text[3:] else text
        text = text.lstrip("json").strip().strip("`").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        obj = json.loads(text[start:end + 1])
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}
