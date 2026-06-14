"""CLI command for domain/process maps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..api import analyze_project
from ..processes import process_map_for_graph, render_process_map
from .common import GRAPH_DIR, GRAPH_FILE, emit, write_meta
from .workflows import _write_or_print


def cmd_processes(args: argparse.Namespace) -> int:
    """Generate an explicit business process/domain map."""

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    process_map = process_map_for_graph(graph)
    if args.format == "json":
        rendered = json.dumps(process_map.to_dict(), indent=2, sort_keys=True)
    else:
        rendered = render_process_map(process_map, graph.project.name)
    return _write_or_print(rendered, args.output, "process map")
