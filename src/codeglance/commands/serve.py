"""Serve generated artifact folders from the CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..serve import serve_directory
from .common import GRAPH_DIR, emit


def resolve_serve_dir(path: str, output_dir: str | None = None) -> Path:
    """Resolve the folder that `serve` should host."""
    base = Path(path).resolve()
    if output_dir:
        out = Path(output_dir)
        return out.resolve() if out.is_absolute() else (base / out).resolve()
    if (base / GRAPH_DIR).is_dir() and not any(base.glob("*.html")):
        return (base / GRAPH_DIR).resolve()
    return base


def cmd_serve(args: argparse.Namespace) -> int:
    """Host generated output artifacts from a local folder."""
    serve_dir = resolve_serve_dir(args.path, args.dir)
    if not serve_dir.is_dir():
        emit(f"Error: output folder not found: {serve_dir}")
        emit("Run `codeglance generate .` first, or pass an existing folder such as `demo`.")
        return 1
    serve_directory(serve_dir, host=args.host, port=args.port, open_browser=args.open)
    return 0
