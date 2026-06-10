"""Render a canvas scene into simple text formats."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from .models import Canvas, Shape, ShapeKind
from .palette import resolve_color


def iter_shapes_by_layer(canvas: Canvas) -> Iterable[Shape]:
    """Yield shapes in the same order both renderers use."""
    yield from canvas.sorted_shapes()


def render_svg(canvas: Canvas) -> str:
    """Render a canvas as a standalone SVG string."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas.width} {canvas.height}">',
        f'<rect width="100%" height="100%" fill="{resolve_color(canvas.background)}"/>',
    ]
    for shape in iter_shapes_by_layer(canvas):
        color = resolve_color(shape.color)
        if shape.kind is ShapeKind.RECTANGLE:
            parts.append(
                f'<rect x="{shape.origin.x}" y="{shape.origin.y}" width="{shape.width}" '
                f'height="{shape.height}" rx="6" fill="{color}"/>'
            )
        elif shape.kind is ShapeKind.CIRCLE:
            radius = min(shape.width, shape.height) // 2
            cx = shape.origin.x + radius
            cy = shape.origin.y + radius
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>')
        elif shape.kind is ShapeKind.LABEL:
            parts.append(
                f'<text x="{shape.origin.x}" y="{shape.origin.y}" fill="{color}" '
                f'font-family="monospace" font-size="{shape.height}">{escape(shape.text)}</text>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def render_ascii(canvas: Canvas) -> str:
    """Render a rough fixed-grid preview for terminals."""
    grid = [[" " for _ in range(canvas.width)] for _ in range(canvas.height)]
    for shape in iter_shapes_by_layer(canvas):
        marker = _marker_for(shape)
        for y in range(shape.origin.y, min(canvas.height, shape.origin.y + shape.height)):
            for x in range(shape.origin.x, min(canvas.width, shape.origin.x + shape.width)):
                grid[y][x] = marker
        if shape.kind is ShapeKind.LABEL and shape.text:
            y = min(canvas.height - 1, shape.origin.y)
            for offset, char in enumerate(shape.text[: max(0, canvas.width - shape.origin.x)]):
                grid[y][shape.origin.x + offset] = char
    return "\n".join("".join(row).rstrip() for row in grid)


def _marker_for(shape: Shape) -> str:
    if shape.kind is ShapeKind.CIRCLE:
        return "o"
    if shape.kind is ShapeKind.LABEL:
        return "."
    return "#"
