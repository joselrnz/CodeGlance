"""CLI command for graph-evidence Q&A."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..api import analyze_project
from ..ask import render_answer
from .common import GRAPH_DIR, GRAPH_FILE, emit, write_meta
from .workflows import _write_or_print


def cmd_ask(args: argparse.Namespace) -> int:
    """Answer a natural-language question using graph evidence."""

    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    graph = analyze_project(root, use_llm=args.llm, model=args.model, progress=emit, full=args.full)
    graph.save(root / GRAPH_DIR / GRAPH_FILE)
    write_meta(root, graph)
    answer = render_answer(args.question, graph, max_results=args.max_results, format=args.format)
    return _write_or_print(answer, args.output, "Q&A answer")
