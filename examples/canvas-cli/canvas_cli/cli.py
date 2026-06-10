"""Command-line interface for the canvas renderer."""

from __future__ import annotations

import argparse

from .commands import render_canvas, write_output


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(prog="canvas-cli", description="Render a tiny demo canvas.")
    parser.add_argument("--format", choices=["svg", "ascii"], default="svg", help="output format")
    parser.add_argument("-o", "--output", help="optional output file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the canvas CLI."""
    args = build_parser().parse_args(argv)
    try:
        write_output(render_canvas(args.format), args.output)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return 0
