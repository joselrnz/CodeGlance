"""Serve generated artifact folders from the CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..api import generate_bundle
from ..serve import WatchConfig, serve_directory
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
    project_root = resolve_watch_root(args.path, args.dir, serve_dir)
    if args.watch and not serve_dir.exists():
        serve_dir.mkdir(parents=True, exist_ok=True)
    if not serve_dir.is_dir():
        emit(f"Error: output folder not found: {serve_dir}")
        emit("Run `codeglance generate .` first, or pass an existing folder such as `demo`.")
        return 1
    watch = None
    if args.watch:
        emit(f"[watch] Initial generation: {project_root} -> {serve_dir}")
        generate_bundle(
            project_root,
            serve_dir,
            use_llm=args.llm,
            model=args.model,
            full=args.full,
            profile=args.profile,
            progress=emit,
        )
        watch = WatchConfig(
            project_root=project_root,
            output_dir=serve_dir,
            profile=args.profile,
            use_llm=args.llm,
            model=args.model,
            full=args.full,
            interval=args.interval,
            quiet=args.quiet,
        )
    serve_directory(serve_dir, host=args.host, port=args.port, open_browser=args.open, watch=watch)
    return 0


def resolve_watch_root(path: str, output_dir: str | None, serve_dir: Path) -> Path:
    """Resolve the project root to watch for a served output directory."""
    base = Path(path).resolve()
    if output_dir:
        return base
    if base.is_dir() and (base / GRAPH_DIR).is_dir() and not any(base.glob("*.html")):
        return base
    resolved = serve_dir.resolve()
    if resolved.name == "outputs" and resolved.parent.name == GRAPH_DIR:
        return resolved.parent.parent.resolve()
    if resolved.name == GRAPH_DIR:
        return resolved.parent.resolve()
    return Path.cwd().resolve()
