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
    "label.search_placeholder": "Search {scope}",
}

_OVERRIDES: dict[str, dict[str, str]] = {
    "es": {
        "nav.overview": "Resumen",
        "nav.drill": "Profundizar",
        "nav.explore": "Explorar",
        "nav.tour": "Tour",
        "label.search_placeholder": "Buscar {scope}",
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
    "translate",
    "validate_catalog_coverage",
]
