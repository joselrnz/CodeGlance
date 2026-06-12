"""Interactive HTML renderer assembly.

The generated page remains a single self-contained HTML document, but the source is split
into template_parts/css.py, template_parts/markup.py, and template_parts/script.py so UI
changes stay reviewable.
"""

from __future__ import annotations

import json

from ..i18n import normalize_locale, text_direction, translate
from .template_parts import INTERACTIVE_TEMPLATE
from .template_parts.tokens import UI_TOKENS


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
    locale = normalize_locale(view_model.get("uiLanguage") or "en")
    stats = view_model.get("stats", {})
    subtitle = (
        f"{stats.get('nodes', 0)} nodes · {stats.get('edges', 0)} edges · "
        f"{len(view_model.get('layers', []))} layers"
    )
    tokens = {
        "__DATA_JSON__": data_json,
        "__HTML_LANG__": _h(locale),
        "__HTML_DIR__": text_direction(locale),
        "__PROJECT_NAME__": _h(name),
        "__SUBTITLE__": _h(subtitle),
        "__TITLE__": _h(f"{name} · Knowledge Graph"),
    }
    tokens.update({placeholder: _t(key, locale) for placeholder, key in UI_TOKENS.items()})
    html = INTERACTIVE_TEMPLATE
    for placeholder, value in tokens.items():
        html = html.replace(placeholder, value)
    return html


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _t(key: str, locale: str) -> str:
    return _h(translate(key, locale))
