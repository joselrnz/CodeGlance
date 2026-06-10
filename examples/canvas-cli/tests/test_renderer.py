import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from canvas_cli.commands import render_canvas
from canvas_cli.models import Canvas, Point, Shape, ShapeKind
from canvas_cli.renderer import render_ascii, render_svg


def test_render_svg_contains_shapes():
    svg = render_canvas("svg")
    assert "<svg" in svg
    assert "<rect" in svg
    assert "<circle" in svg
    assert "canvas-cli" in svg


def test_render_ascii_marks_canvas():
    canvas = Canvas(width=8, height=4)
    canvas.add(Shape(ShapeKind.RECTANGLE, Point(1, 1), 3, 2, "blue"))

    preview = render_ascii(canvas)

    assert "###" in preview


def test_render_svg_escapes_label_text():
    canvas = Canvas(width=20, height=4)
    canvas.add(Shape(ShapeKind.LABEL, Point(1, 2), 0, 2, "paper", text="<tag>"))

    svg = render_svg(canvas)

    assert "&lt;tag&gt;" in svg
