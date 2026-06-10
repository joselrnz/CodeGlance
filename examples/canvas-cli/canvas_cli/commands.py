"""Command handlers for the canvas CLI."""

from __future__ import annotations

from pathlib import Path

from .models import Canvas, Point, Shape, ShapeKind
from .renderer import render_ascii, render_svg


def build_demo_canvas() -> Canvas:
    """Create the default scene used when no input file is provided."""
    canvas = Canvas(width=48, height=16, background="ink")
    canvas.add(Shape(ShapeKind.RECTANGLE, Point(2, 2), 18, 5, "blue", layer=1))
    canvas.add(Shape(ShapeKind.CIRCLE, Point(25, 3), 8, 8, "green", layer=2))
    canvas.add(Shape(ShapeKind.RECTANGLE, Point(8, 9), 30, 4, "gold", layer=3))
    canvas.add(Shape(ShapeKind.LABEL, Point(11, 12), 0, 2, "paper", text="canvas-cli", layer=4))
    return canvas


def render_canvas(format_name: str) -> str:
    """Render the default canvas in the requested format."""
    canvas = build_demo_canvas()
    if format_name == "svg":
        return render_svg(canvas)
    if format_name == "ascii":
        return render_ascii(canvas)
    raise ValueError(f"unsupported format: {format_name}")


def write_output(content: str, output: str | None) -> None:
    """Write rendered content to a file or stdout."""
    if output:
        Path(output).write_text(content + "\n", encoding="utf-8")
        return
    print(content)
