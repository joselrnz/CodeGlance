"""Localization foundation tests."""

from codeglance.i18n import (
    list_languages,
    normalize_locale,
    text_direction,
    translate,
    validate_catalog_coverage,
)


def test_list_languages_includes_supported_release_locales():
    assert list_languages() == [
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
    ]


def test_normalize_locale_accepts_common_aliases_and_falls_back_to_english():
    cases = {
        "en": "en",
        "EN_us": "en",
        "es-MX": "es",
        "zh_CN": "zh",
        "zh-Hans-CN": "zh",
        "zh_TW": "zh-TW",
        "zh-Hant-HK": "zh-TW",
        "pt_BR": "pt-BR",
        "pt-PT": "pt-BR",
        "fr_CA.UTF-8": "fr",
        "": "en",
        None: "en",
        "unknown": "en",
    }

    for raw, expected in cases.items():
        assert normalize_locale(raw) == expected


def test_translate_returns_localized_messages_and_formats_values():
    assert translate("app.title") == "Codeglance"
    assert translate("nav.overview", "es") == "Resumen"
    assert translate("label.search_placeholder", "pt_BR", scope="archivos") == "Buscar archivos"
    assert translate("label.search_placeholder", "fr-CA", scope="fichiers") == "Rechercher fichiers"


def test_translate_falls_back_to_english_for_unknown_locale_or_missing_key():
    assert translate("nav.graph", "xx-YY") == "Graph"
    assert translate("missing.key", "es") == "missing.key"


def test_text_direction_marks_rtl_locales_only():
    assert text_direction("en") == "ltr"
    assert text_direction("es-MX") == "ltr"
    assert text_direction("ar") == "rtl"
    assert text_direction("he-IL") == "rtl"


def test_validate_catalog_coverage_reports_no_gaps():
    assert validate_catalog_coverage() == []


def test_validate_catalog_coverage_reports_missing_extra_and_empty_values():
    issues = validate_catalog_coverage(
        {
            "en": {"app.title": "Codeglance", "nav.graph": "Graph"},
            "es": {"app.title": "", "nav.extra": "Extra"},
        }
    )

    assert "es: missing keys nav.graph" in issues
    assert "es: extra keys nav.extra" in issues
    assert "es: empty values app.title" in issues
