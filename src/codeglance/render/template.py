"""Interactive HTML renderer assembly.

The generated page remains a single self-contained HTML document, but the source is split
into template_parts/css.py, template_parts/markup.py, and template_parts/script.py so UI
changes stay reviewable.
"""

from __future__ import annotations

import json

from ..i18n import normalize_locale, text_direction, translate
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
    locale = normalize_locale(view_model.get("uiLanguage") or "en")
    stats = view_model.get("stats", {})
    subtitle = (
        f"{stats.get('nodes', 0)} nodes · {stats.get('edges', 0)} edges · "
        f"{len(view_model.get('layers', []))} layers"
    )
    return (
        INTERACTIVE_TEMPLATE
        .replace("__DATA_JSON__", data_json)
        .replace("__HTML_LANG__", _h(locale))
        .replace("__HTML_DIR__", text_direction(locale))
        .replace("__PROJECT_NAME__", _h(name))
        .replace("__SUBTITLE__", _h(subtitle))
        .replace("__TITLE__", _h(f"{name} · Knowledge Graph"))
        .replace("__NAV_OVERVIEW__", _t("nav.overview", locale))
        .replace("__NAV_DRILL__", _t("nav.drill", locale))
        .replace("__NAV_EXPLORE__", _t("nav.explore", locale))
        .replace("__NAV_TOUR__", _t("nav.tour", locale))
        .replace("__MAP_STRUCTURAL__", _t("map.structural", locale))
        .replace("__MAP_DOMAIN__", _t("map.domain", locale))
        .replace("__MAP_KNOWLEDGE__", _t("map.knowledge", locale))
        .replace("__ACTION_FIT__", _t("action.fit", locale))
        .replace("__ACTION_PATH__", _t("action.path", locale))
        .replace("__ACTION_FILTER__", _t("action.filter", locale))
        .replace("__ACTION_EXPORT__", _t("action.export", locale))
        .replace("__ACTION_FLOW__", _t("action.flow", locale))
        .replace("__ACTION_THEME__", _t("action.theme", locale))
        .replace("__ACTION_REFRESH__", _t("action.refresh", locale))
        .replace("__ACTION_HELP__", _t("action.help", locale))
        .replace("__ACTION_DIFF__", _t("action.diff", locale))
        .replace("__ACTION_FUNCTIONS__", _t("action.functions", locale))
        .replace("__ACTION_FACETS__", _t("action.facets", locale))
        .replace("__DETAIL_FILES__", _t("detail.files", locale))
        .replace("__DETAIL_CLASSES__", _t("detail.classes", locale))
        .replace("__SEARCH_FUZZY__", _t("search.fuzzy", locale))
        .replace("__SEARCH_SEMANTIC__", _t("search.semantic", locale))
        .replace("__SEARCH_NODES__", _t("label.search_nodes", locale))
        .replace("__LABEL_TOOLS__", _t("label.tools", locale))
        .replace("__LABEL_ANALYSIS__", _t("label.analysis", locale))
        .replace("__LABEL_DETAIL__", _t("label.detail", locale))
        .replace("__LABEL_SEARCH__", _t("label.search", locale))
        .replace("__LABEL_ACTIONS__", _t("label.actions", locale))
    )


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _t(key: str, locale: str) -> str:
    return _h(translate(key, locale))
