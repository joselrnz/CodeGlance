"""Small localization catalog for Codeglance UI and CLI labels."""

from __future__ import annotations

from collections.abc import Mapping

SUPPORTED_LOCALES: tuple[str, ...] = (
    "en",
    "es",
    "zh",
    "zh-TW",
    "ja",
    "ko",
    "ru",
    "pt-BR",
    "fr",
    "de",
    "it",
    "tr",
    "pl",
    "uk",
    "id",
    "vi",
    "hi",
    "ar",
    "he",
    "nl",
    "sv",
)

_BASE: dict[str, str] = {
    "app.title": "Codeglance",
    "nav.overview": "Overview",
    "nav.drill": "Drill",
    "nav.explore": "Explore",
    "nav.tour": "Tour",
    "nav.graph": "Graph",
    "map.structural": "Structural",
    "map.domain": "Domain",
    "map.knowledge": "Knowledge",
    "panel.info": "Info",
    "panel.files": "Files",
    "action.fit": "Fit",
    "action.path": "Path",
    "action.filter": "Filter",
    "action.export": "Export",
    "action.flow": "Flow",
    "action.theme": "Theme",
    "action.term": "Terminal",
    "action.refresh": "Refresh",
    "action.help": "Help",
    "action.diff": "Diff",
    "action.functions": "Functions",
    "action.facets": "Facets",
    "detail.files": "Files",
    "detail.classes": "+Classes",
    "search.fuzzy": "Fuzzy",
    "search.semantic": "Semantic",
    "label.tools": "Tools",
    "label.analysis": "Analysis",
    "label.detail": "Detail",
    "label.search": "Search",
    "label.actions": "Actions",
    "label.search_placeholder": "Search {scope}",
    "label.search_nodes": "Search nodes...",
    "overview.nodes": "Nodes",
    "overview.edges": "Edges",
    "overview.layers": "Layers",
    "overview.types": "Types",
    "overview.languages": "Languages",
    "overview.frameworks": "Frameworks",
    "overview.node_types": "Node types",
    "overview.most_connected": "Most connected",
    "overview.project_tour": "Project Tour",
    "overview.start_tour": "Start Tour",
    "domain.blurb": "Business domains inferred from the project structure, linked by cross-domain flows. Click a domain for details.",
    "domain.entities": "ENTITIES",
    "knowledge.blurb": "Markdown docs as articles, linked by wikilinks and citations. Click an article for details.",
    "panel.documentation": "Documentation",
    "panel.language_notes": "Language notes",
    "panel.layer": "Layer",
    "panel.connections": "Connections",
    "panel.source": "Source",
    "panel.expand": "Expand",
    "panel.process_flows": "Process flows",
    "empty.files": "No files.",
    "empty.domains": "No domains detected.",
    "empty.docs": "No linked docs found.",
    "empty.knowledge": "No markdown docs to link.",
    "filter.node_types": "Node types",
    "filter.complexity": "Complexity",
    "filter.reset": "Reset filters",
    "theme.title": "Theme",
    "theme.accent": "Accent color",
    "theme.heading_font": "Heading font",
    "terminal.title": "terminal",
    "terminal.subtitle": "graph queries + JS · 100% offline · type help",
    "terminal.help_intro": "Explore & test this codebase — all offline, against the embedded graph:",
    "terminal.none": "(none)",
    "terminal.no_domains": "no domains detected",
    "terminal.no_steps": "no steps",
    "terminal.unknown": "unknown command",
    "terminal.try_help": "try help",
    "modal.path_title": "Dependency Path Finder",
    "modal.find_path": "Find path",
    "modal.clear": "Clear",
    "help.title": "Keyboard Shortcuts",
    "help.subtitle": "Drive the whole graph from the keyboard — no mouse required.",
    "help.general": "General",
    "help.navigation": "Navigation",
    "help.view_modes": "View modes",
    "help.guided_tour": "Guided tour",
    "help.focus_search": "Focus search",
    "help.filter_panel": "Filter panel",
    "help.export_menu": "Export menu",
    "help.theme_menu": "Theme menu",
    "help.terminal": "Terminal (queries + JS)",
    "help.toggle_help": "Toggle this help",
    "help.close_panel": "Close panel / menu",
    "help.fit_graph": "Fit graph to view",
    "help.reset_fit": "Reset & fit",
    "help.zoom": "Zoom in / out",
    "help.pan": "Pan the canvas",
    "help.path_finder": "Path finder",
    "help.focus_node": "Focus node + neighbors",
    "help.domain_toggle": "Domain <-> Structural",
    "help.knowledge_toggle": "Knowledge <-> Structural",
    "help.diff_overlay": "Diff overlay",
    "help.edge_flow": "Edge-flow animation",
    "help.collapse_clusters": "Collapse / expand all clusters",
    "help.tour_prev_next": "Previous / next step",
    "help.tour_exit": "Exit the tour",
    "help.close_hint": "Press Esc or click outside to close",
}

_OVERRIDES: dict[str, dict[str, str]] = {
    "es": {
        "nav.overview": "Resumen",
        "nav.drill": "Profundizar",
        "nav.explore": "Explorar",
        "nav.tour": "Tour",
        "map.structural": "Estructura",
        "map.domain": "Dominio",
        "map.knowledge": "Conocimiento",
        "action.filter": "Filtro",
        "action.export": "Exportar",
        "action.refresh": "Actualizar",
        "action.help": "Ayuda",
        "label.tools": "Herramientas",
        "label.analysis": "Analisis",
        "label.detail": "Detalle",
        "label.search": "Buscar",
        "label.actions": "Acciones",
        "label.search_placeholder": "Buscar {scope}",
        "label.search_nodes": "Buscar nodos...",
        "overview.nodes": "Nodos",
        "overview.edges": "Enlaces",
        "overview.layers": "Capas",
        "overview.types": "Tipos",
        "overview.languages": "Lenguajes",
        "overview.frameworks": "Frameworks",
        "overview.node_types": "Tipos de nodo",
        "overview.most_connected": "Mas conectados",
        "overview.project_tour": "Tour del proyecto",
        "overview.start_tour": "Iniciar tour",
        "domain.blurb": "Dominios de negocio inferidos desde la estructura del proyecto, enlazados por flujos entre dominios.",
        "domain.entities": "ENTIDADES",
        "knowledge.blurb": "Documentos Markdown como articulos, enlazados por wikilinks y citas.",
        "panel.documentation": "Documentacion",
        "panel.language_notes": "Notas del lenguaje",
        "panel.layer": "Capa",
        "panel.connections": "Conexiones",
        "panel.source": "Fuente",
        "panel.expand": "Expandir",
        "panel.process_flows": "Flujos de proceso",
        "empty.files": "No hay archivos.",
        "empty.domains": "No se detectaron dominios.",
        "empty.docs": "No se encontraron documentos enlazados.",
        "empty.knowledge": "No hay documentos Markdown para enlazar.",
        "filter.node_types": "Tipos de nodo",
        "filter.complexity": "Complejidad",
        "filter.reset": "Restablecer filtros",
        "theme.title": "Tema",
        "theme.accent": "Color principal",
        "theme.heading_font": "Fuente de titulos",
        "terminal.title": "terminal",
        "terminal.subtitle": "consultas del grafo + JS · 100% offline · escribe help",
        "terminal.help_intro": "Explora y prueba este codigo: todo offline, contra el grafo embebido:",
        "terminal.none": "(ninguno)",
        "terminal.no_domains": "no se detectaron dominios",
        "terminal.no_steps": "sin pasos",
        "terminal.unknown": "comando desconocido",
        "terminal.try_help": "prueba help",
        "modal.path_title": "Buscador de rutas de dependencia",
        "modal.find_path": "Buscar ruta",
        "modal.clear": "Limpiar",
        "help.title": "Atajos de teclado",
        "help.subtitle": "Controla todo el grafo desde el teclado, sin mouse.",
        "help.general": "General",
        "help.navigation": "Navegacion",
        "help.view_modes": "Vistas",
        "help.guided_tour": "Tour guiado",
    },
    "fr": {
        "nav.overview": "Apercu",
        "nav.drill": "Explorer",
        "nav.explore": "Parcourir",
        "nav.tour": "Visite",
        "label.search_placeholder": "Rechercher {scope}",
    },
    "pt-BR": {
        "nav.overview": "Visao geral",
        "nav.drill": "Detalhar",
        "nav.explore": "Explorar",
        "nav.tour": "Tour",
        "label.search_placeholder": "Buscar {scope}",
    },
    "de": {"nav.overview": "Ubersicht", "nav.explore": "Erkunden"},
    "it": {"nav.overview": "Panoramica", "nav.explore": "Esplora"},
    "nl": {"nav.overview": "Overzicht", "nav.explore": "Verkennen"},
    "sv": {"nav.overview": "Oversikt", "nav.explore": "Utforska"},
    "tr": {"nav.overview": "Genel Bakis", "nav.explore": "Kesfet"},
    "pl": {"nav.overview": "Przeglad", "nav.explore": "Eksploruj"},
    "uk": {"nav.overview": "Ohliad", "nav.explore": "Doslidyty"},
    "id": {"nav.overview": "Ringkasan", "nav.explore": "Jelajah"},
    "vi": {"nav.overview": "Tong quan", "nav.explore": "Kham pha"},
    "zh": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "zh-TW": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "ja": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "ko": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "ru": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "hi": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "ar": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "he": {"nav.overview": "Overview", "nav.explore": "Explore"},
}

_RTL_LOCALES = {"ar", "he"}


def list_languages() -> list[str]:
    """Return supported locale IDs in release order."""

    return list(SUPPORTED_LOCALES)


def normalize_locale(locale: str | None) -> str:
    """Normalize user/browser locale strings to a supported Codeglance locale."""

    if not locale:
        return "en"

    cleaned = locale.split(".", 1)[0].replace("_", "-").strip()
    if not cleaned:
        return "en"

    parts = [part for part in cleaned.split("-") if part]
    if not parts:
        return "en"
    language = parts[0].lower()
    region = parts[-1].upper() if len(parts) > 1 else ""

    if language == "zh":
        if region in {"TW", "HK", "MO"} or any(part.lower() == "hant" for part in parts[1:]):
            return "zh-TW"
        return "zh"
    if language == "pt":
        return "pt-BR"
    if language == "en":
        return "en"

    if language in SUPPORTED_LOCALES:
        return language
    return "en"


def translate(key: str, locale: str | None = "en", **values: object) -> str:
    """Translate a catalog key, falling back to English and then the key name."""

    catalog = _catalog_for(normalize_locale(locale))
    template = catalog.get(key) or _BASE.get(key) or key
    if values:
        try:
            return template.format(**values)
        except (KeyError, ValueError):
            return template
    return template


def ui_catalog(locale: str | None = "en") -> dict[str, str]:
    """Return the merged UI catalog for embedding in generated static HTML."""

    return _catalog_for(normalize_locale(locale))


def text_direction(locale: str | None = "en") -> str:
    """Return the document direction for a locale."""

    return "rtl" if normalize_locale(locale) in _RTL_LOCALES else "ltr"


def validate_catalog_coverage(catalogs: Mapping[str, Mapping[str, str]] | None = None) -> list[str]:
    """Return missing-key coverage issues for every supported locale catalog."""

    source = catalogs or _all_catalogs()
    expected = set(source.get("en", _BASE))
    issues: list[str] = []
    locales = [locale for locale in source if locale != "en"] if catalogs is not None else list(SUPPORTED_LOCALES)
    for locale in locales:
        catalog = source.get(locale, {})
        keys = set(catalog)
        missing = sorted(expected - keys)
        extra = sorted(keys - expected)
        empty = sorted(key for key, value in catalog.items() if key in expected and not value)
        if missing:
            issues.append(f"{locale}: missing keys {', '.join(missing)}")
        if extra:
            issues.append(f"{locale}: extra keys {', '.join(extra)}")
        if empty:
            issues.append(f"{locale}: empty values {', '.join(empty)}")
    return issues


def _catalog_for(locale: str) -> dict[str, str]:
    catalog = dict(_BASE)
    catalog.update(_OVERRIDES.get(locale, {}))
    return catalog


def _all_catalogs() -> dict[str, dict[str, str]]:
    return {locale: _catalog_for(locale) for locale in SUPPORTED_LOCALES}


__all__ = [
    "SUPPORTED_LOCALES",
    "list_languages",
    "normalize_locale",
    "text_direction",
    "translate",
    "ui_catalog",
    "validate_catalog_coverage",
]
