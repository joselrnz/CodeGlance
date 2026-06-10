"""Domain models for a small 2D canvas."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ShapeKind(str, Enum):
    """Supported drawable shape types."""

    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    LABEL = "label"


@dataclass(frozen=True)
class Point:
    """A 2D coordinate on the canvas."""

    x: int
    y: int


@dataclass(frozen=True)
class Shape:
    """A drawable item placed on a canvas."""

    kind: ShapeKind
    origin: Point
    width: int
    height: int
    color: str
    text: str = ""
    layer: int = 0


@dataclass
class Canvas:
    """A bounded scene made of ordered shapes."""

    width: int
    height: int
    background: str = "ink"
    shapes: list[Shape] = field(default_factory=list)

    def add(self, shape: Shape) -> None:
        """Append a shape to the scene."""
        self.shapes.append(shape)

    def sorted_shapes(self) -> list[Shape]:
        """Return shapes in render order."""
        return sorted(self.shapes, key=lambda shape: (shape.layer, shape.kind.value))
