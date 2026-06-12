"""Generate output-bundle CLI command."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..api import generate_bundle
from ..serve import serve_directory
from .common import GRAPH_DIR, emit


def cmd_generate(args: argparse.Namespace) -> int:
    """Write the selected output bundle from one analysis pass."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        emit(f"Error: not a directory: {root}")
        return 1
    out = Path(args.output).resolve() if args.output else root / GRAPH_DIR / "outputs"
    graph, outputs = generate_bundle(
        root,
        out,
        use_llm=args.llm,
        model=args.model,
        full=args.full,
        profile=args.profile,
        ui_language=args.ui_language or args.language,
        progress=emit,
    )
    stats = graph.stats()
    emit("")
    emit(f"✓ generated {len(outputs)} {args.profile} outputs for {graph.project.name}")
    emit(f"  {stats['nodes']} nodes · {stats['edges']} edges · {stats['layers']} layers")
    if args.ui_language or args.language:
        emit(f"  UI language: {args.ui_language or args.language}")
    emit(f"  Output folder: {out}")
    if any(item.path.name == "index.html" for item in outputs):
        emit(f"  Index: {out / 'index.html'}")
    if args.serve:
        serve_directory(out, host=args.host, port=args.port, open_browser=args.open)
    return 0
