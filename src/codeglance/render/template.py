"""Interactive HTML renderer assembly.

The generated page remains a single self-contained HTML document, but the source is split
into template_parts/css.py, template_parts/markup.py, and template_parts/script.py so UI
changes stay reviewable.
"""

from __future__ import annotations

import json

from .template_parts import INTERACTIVE_TEMPLATE


def render_interactive_html(view_model: dict) -> str:
    """Render a view model into the self-contained interactive HTML graph document."""
    data_json = (
        json.dumps(view_model, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    project = view_model.get("project", {})
    name = project.get("name", "project")
    stats = view_model.get("stats", {})
    subtitle = (
        f"{stats.get('nodes', 0)} nodes · {stats.get('edges', 0)} edges · "
        f"{len(view_model.get('layers', []))} layers"
    )
    return (
        INTERACTIVE_TEMPLATE
        .replace("__DATA_JSON__", data_json)
        .replace("__PROJECT_NAME__", _h(name))
        .replace("__SUBTITLE__", _h(subtitle))
        .replace("__TITLE__", _h(f"{name} · Knowledge Graph"))
    )


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
