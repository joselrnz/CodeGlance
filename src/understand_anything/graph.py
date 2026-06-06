"""Orchestrates the full analysis pipeline into a KnowledgeGraph."""

from __future__ import annotations

import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import fingerprint as fp
from .analyze import layers as layers_mod
from .analyze import llm as llm_mod
from .analyze import tour as tour_mod
from .analyze.structural import build_structural
from .scan import scan
from .schema import KnowledgeGraph, Layer, Node, Project, FILE_LEVEL_TYPES, _kebab

GRAPH_PATH = ".understand-anything/knowledge-graph.json"

Progress = Callable[[str], None]


def _git_commit(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def _normalize_layers(layers: list[Layer], file_ids: list[str],
                      max_layers: int = 14, min_members: int = 2) -> list[Layer]:
    """Cap layer count, fold small communities into a 'Shared' layer, guarantee full coverage."""
    assigned: set[str] = set()
    keep: list[Layer] = []
    overflow: list[str] = []

    big = [l for l in layers if len(l.nodeIds) >= min_members]
    small = [l for l in layers if len(l.nodeIds) < min_members]
    big.sort(key=lambda l: len(l.nodeIds), reverse=True)

    for layer in big[: max_layers - 1]:
        members = [nid for nid in layer.nodeIds if nid not in assigned]
        if not members:
            continue
        assigned.update(members)
        layer.nodeIds = members
        keep.append(layer)

    for layer in big[max_layers - 1:] + small:
        overflow.extend(nid for nid in layer.nodeIds if nid not in assigned)

    # Any file node never placed (shouldn't happen, but be safe).
    for nid in file_ids:
        if nid not in assigned and nid not in overflow:
            overflow.append(nid)

    overflow = [nid for nid in overflow if nid not in assigned]
    if overflow:
        keep.append(Layer(
            id="layer:shared", name="Shared / Misc",
            description=f"Cross-cutting and standalone files ({len(overflow)} files).",
            nodeIds=overflow,
        ))
    return keep


def analyze(root: str | Path, use_llm: bool = False, model: str | None = None,
            progress: Progress | None = None, full: bool = False) -> KnowledgeGraph:
    root = Path(root).resolve()
    log = progress or (lambda _m: None)

    log("[1/5] Scanning project files...")
    scan_result = scan(root)
    log(f"      Found {len(scan_result.files)} files across {len(scan_result.languages)} languages"
        f" ({scan_result.filtered} ignored).")

    # --- Incremental diff against the previous run ------------------------------------------
    new_fp = fp.compute(scan_result.files, root)
    old_fp = {} if full else fp.load(root)
    old_graph = None
    graph_file = root / GRAPH_PATH
    if not full and graph_file.is_file():
        try:
            old_graph = KnowledgeGraph.load(graph_file)
        except Exception:
            old_graph = None

    changed_paths: set[str] = set()
    if old_fp:
        changed, added, removed = fp.diff(old_fp, new_fp)
        changed_paths = changed | added
        if not changed and not added and not removed and old_graph is not None:
            log("      Graph is up to date — nothing changed since last analysis.")
            fp.save(root, new_fp)
            return old_graph
        log(f"      Incremental: {len(changed)} changed, {len(added)} added, {len(removed)} removed.")

    log("[2/5] Extracting structure (files, functions, classes, imports)...")
    nodes, edges = build_structural(scan_result)
    log(f"      Built {len(nodes)} nodes and {len(edges)} edges.")

    # Reuse prior summaries for unchanged files (preserves earlier LLM enrichment for free).
    reused = 0
    if old_graph is not None:
        old_summary = {n.id: n.summary for n in old_graph.nodes if n.summary}
        for n in nodes:
            if n.filePath and (not changed_paths or n.filePath not in changed_paths):
                prior = old_summary.get(n.id)
                if prior and prior != n.summary:
                    n.summary = prior
                    reused += 1
        if reused:
            log(f"      Reused {reused} summaries from unchanged files.")

    if use_llm:
        hint = llm_mod.availability_hint()
        if hint == "available":
            # On an incremental run, only enrich files that actually changed.
            only = changed_paths if (old_fp and changed_paths) else None
            log("[2.5/5] Enriching summaries with LLM"
                + (f" ({len(only)} changed files)" if only else "") + "...")
            n = llm_mod.enrich(KnowledgeGraph(nodes=nodes, edges=edges,
                                              project=Project(name=scan_result.name)),
                               root=root, model=model, progress=log, only_paths=only)
            log(f"      Enriched {n} summaries.")
        else:
            log(f"[2.5/5] LLM enrichment requested but unavailable — {hint} Continuing deterministically.")

    log("[3/5] Detecting architectural layers...")
    file_ids = [n.id for n in nodes if n.type in FILE_LEVEL_TYPES]
    layers = _normalize_layers(layers_mod.detect_layers(nodes, edges), file_ids)
    log(f"      Identified {len(layers)} layers.")

    log("[4/5] Building guided tour...")
    tour = tour_mod.build_tour(nodes, edges, layers)
    log(f"      {len(tour)} tour steps.")

    if use_llm and llm_mod.is_available():
        log("      Polishing layer names and tour narrative with LLM...")
        nl = llm_mod.name_layers(layers, nodes, model=model, progress=log)
        nt = llm_mod.narrate_tour(tour, nodes, _describe_project(scan_result), model=model, progress=log)
        log(f"      LLM refined {nl} layer names and {nt} tour steps.")

    log("[5/5] Assembling knowledge graph...")
    project = Project(
        name=scan_result.name,
        languages=scan_result.languages,
        frameworks=scan_result.frameworks,
        description=_describe_project(scan_result),
        analyzedAt=datetime.now(timezone.utc).isoformat(),
        gitCommitHash=_git_commit(root),
    )
    graph = KnowledgeGraph(project=project, nodes=nodes, edges=edges, layers=layers, tour=tour)
    fp.save(root, new_fp)
    return graph


def _describe_project(scan_result) -> str:
    cats = Counter(f.category for f in scan_result.files)
    parts = ", ".join(f"{c} {k}" for k, c in cats.most_common())
    langs = ", ".join(scan_result.languages[:5]) or "mixed"
    return f"{scan_result.name}: {len(scan_result.files)} files ({parts}). Primary languages: {langs}."
