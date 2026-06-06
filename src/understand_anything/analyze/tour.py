"""Deterministic guided tour.

Picks a sensible reading order through the codebase: start at the README, then the entry point,
then the most-connected file in each layer. `--llm` can rewrite the narrative later.
"""

from __future__ import annotations

from collections import defaultdict

from ..schema import Edge, Layer, Node, TourStep, FILE_LEVEL_TYPES

_ENTRY_HINTS = (
    "main.py", "__main__.py", "app.py", "manage.py", "cli.py", "wsgi.py", "asgi.py", "run.py",
    "src/index.ts", "src/main.ts", "src/app.tsx", "index.js", "main.go", "src/main.rs",
)


def build_tour(nodes: list[Node], edges: list[Edge], layers: list[Layer], max_steps: int = 12) -> list[TourStep]:
    file_nodes = [n for n in nodes if n.type in FILE_LEVEL_TYPES]
    if not file_nodes:
        return []
    by_id = {n.id: n for n in nodes}

    degree: dict[str, int] = defaultdict(int)
    for e in edges:
        degree[e.source] += 1
        degree[e.target] += 1

    steps: list[TourStep] = []
    order = 1
    used: set[str] = set()

    # 1. README / top docs first.
    readme = next(
        (n for n in file_nodes if n.type == "document" and "readme" in (n.filePath or n.name).lower()),
        None,
    )
    if readme:
        steps.append(TourStep(order, "Project Overview",
                              "Start with the project's documentation to understand its purpose.",
                              [readme.id]))
        used.add(readme.id)
        order += 1

    # 2. Entry point.
    entry = None
    for hint in _ENTRY_HINTS:
        entry = next((n for n in file_nodes if (n.filePath or "").lower().endswith(hint)), None)
        if entry:
            break
    if entry and entry.id not in used:
        steps.append(TourStep(order, "Entry Point",
                              f"`{entry.filePath}` is where execution begins.", [entry.id]))
        used.add(entry.id)
        order += 1

    # 3. Most-connected file per layer.
    layers_sorted = sorted(layers, key=lambda l: len(l.nodeIds), reverse=True)
    for layer in layers_sorted:
        if len(steps) >= max_steps:
            break
        candidates = [nid for nid in layer.nodeIds if nid in by_id and nid not in used]
        if not candidates:
            continue
        hub = max(candidates, key=lambda nid: degree.get(nid, 0))
        node = by_id[hub]
        steps.append(TourStep(
            order, f"{layer.name}",
            f"The {layer.name} layer centers on `{node.filePath or node.name}`. {node.summary}".strip(),
            [hub],
        ))
        used.add(hub)
        order += 1

    return steps
