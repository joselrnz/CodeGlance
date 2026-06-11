"""Central, typed rendering configuration.

Every tunable that used to be a magic number scattered across ``layout.py`` and ``render/__init__.py``
— card dimensions, grid gaps, the colour palette, the default theme — lives here on one frozen
dataclass. To customise the output you build a ``VizConfig`` and pass it in; nothing is hunted for
across files:

    from codeglance.config import VizConfig
    from codeglance.render import render_interactive
    html = render_interactive(graph, config=VizConfig(card_w=240, default_theme="ocean"))

``DEFAULT_CONFIG`` reproduces today's look exactly, so existing callers are unaffected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .enums import ThemeName

# Node card colour by type (mirrors the original dashboard palette).
_TYPE_COLORS: dict[str, str] = {
    "file": "#4a7c9b", "function": "#5a9e6f", "class": "#8b6fb0", "module": "#c08457",
    "concept": "#d4a574", "config": "#5eead4", "document": "#7dd3fc", "service": "#a78bfa",
    "table": "#6ee7b7", "endpoint": "#fdba74", "pipeline": "#fda4af", "schema": "#f0abfc",
    "resource": "#fca5a5", "variable": "#7fb3d5", "constant": "#e6b450",
}

# Layer/cluster container border colours, cycled by index.
_LAYER_PALETTE: tuple[str, ...] = (
    "#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb7185",
    "#22d3ee", "#a3e635", "#f59e0b", "#e879f9", "#4ade80", "#38bdf8",
    "#fca5a5", "#c084fc", "#2dd4bf", "#facc15",
)


@dataclass(frozen=True)
class VizConfig:
    """All visual + layout tunables for the renderers. Immutable; override by constructing a new one."""

    # --- node cards (structural graph) ---
    card_w: float = 244.0
    card_h: float = 92.0

    # --- swimlane layout (compute_layered_layout): gridded cards inside per-layer containers ---
    lane_gap_x: float = 26.0      # horizontal gap between cards in a lane
    lane_gap_y: float = 22.0      # vertical gap between card rows
    lane_pad: float = 18.0        # inner padding of a lane container
    lane_header: float = 36.0     # lane header band height
    lane_spacing: float = 48.0    # vertical gap between stacked lanes
    lane_left: float = 48.0       # left origin of the lane stack
    lane_top: float = 48.0        # top origin of the lane stack
    max_cols: int = 8             # max cards per row before wrapping

    # --- layer overview cards ---
    layer_card_w: float = 300.0
    layer_card_h: float = 150.0
    layer_gap_x: float = 48.0
    layer_gap_y: float = 44.0

    # --- domain map cards ---
    domain_card_w: float = 300.0
    domain_card_h: float = 150.0
    domain_gap_x: float = 60.0
    domain_gap_y: float = 70.0

    # --- knowledge (markdown) cards ---
    knowledge_card_w: float = 280.0
    knowledge_card_h: float = 150.0
    knowledge_gap_x: float = 60.0
    knowledge_gap_y: float = 70.0

    # --- colours ---
    type_colors: Mapping[str, str] = field(default_factory=lambda: dict(_TYPE_COLORS))
    default_type_color: str = "#94a3b8"
    layer_palette: tuple[str, ...] = _LAYER_PALETTE
    unassigned_color: str = "#64748b"

    # --- theme + source embedding ---
    default_theme: ThemeName = ThemeName.OCEAN   # project default (Dark Ocean) — the one place to change it
    max_source_bytes: int = 16_000

    # --- encapsulated accessors ("getters") ---
    def color_for_type(self, node_type: str) -> str:
        """Card colour for a node type, falling back to the neutral default."""
        return self.type_colors.get(node_type, self.default_type_color)

    def layer_color(self, index: int) -> str:
        """Palette colour for layer ``index`` (wraps around the palette)."""
        return self.layer_palette[index % len(self.layer_palette)]


# The default look — identical to the historic hardcoded values.
DEFAULT_CONFIG = VizConfig()
