"""CLI entrypoints for codeglance."""

from .main import main
from .parser import build_parser
from ..commands import resolve_serve_dir as _resolve_serve_dir

__all__ = ["_resolve_serve_dir", "build_parser", "main"]
