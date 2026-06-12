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
    "flow.steps": "steps",
    "flow.files": "files",
    "flow.confidence": "confidence",
    "flow.entry": "entry",
    "flow.exit": "exit",
    "flow.open_first_step": "Open first step",
    "flow.more_steps": "more step(s)",
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
        "flow.steps": "pasos",
        "flow.files": "archivos",
        "flow.confidence": "confianza",
        "flow.entry": "entrada",
        "flow.exit": "salida",
        "flow.open_first_step": "Abrir primer paso",
        "flow.more_steps": "paso(s) mas",
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
    "ja": {
        "nav.overview": "概要",
        "nav.drill": "ドリル",
        "nav.explore": "探索",
        "nav.tour": "ツアー",
        "nav.graph": "グラフ",
        "map.structural": "構造",
        "map.domain": "ドメイン",
        "map.knowledge": "ナレッジ",
        "panel.info": "情報",
        "panel.files": "ファイル",
        "action.fit": "全体表示",
        "action.path": "経路",
        "action.filter": "フィルター",
        "action.export": "エクスポート",
        "action.flow": "フロー",
        "action.theme": "テーマ",
        "action.term": "ターミナル",
        "action.refresh": "更新",
        "action.help": "ヘルプ",
        "action.diff": "差分",
        "action.functions": "関数",
        "action.facets": "分類",
        "detail.files": "ファイル",
        "detail.classes": "+クラス",
        "search.fuzzy": "あいまい",
        "search.semantic": "意味検索",
        "label.tools": "ツール",
        "label.analysis": "分析",
        "label.detail": "詳細",
        "label.search": "検索",
        "label.actions": "操作",
        "label.search_placeholder": "{scope}を検索",
        "label.search_nodes": "ノードを検索...",
        "overview.nodes": "ノード",
        "overview.edges": "エッジ",
        "overview.layers": "レイヤー",
        "overview.types": "種類",
        "overview.languages": "言語",
        "overview.frameworks": "フレームワーク",
        "overview.node_types": "ノード種別",
        "overview.most_connected": "接続が多い項目",
        "overview.project_tour": "プロジェクトツアー",
        "overview.start_tour": "ツアー開始",
        "domain.blurb": "プロジェクト構造から推定した業務ドメインと、ドメイン間フローです。",
        "domain.entities": "エンティティ",
        "knowledge.blurb": "Markdownドキュメントを記事として扱い、リンクや引用で関連付けます。",
        "panel.documentation": "ドキュメント",
        "panel.language_notes": "言語メモ",
        "panel.layer": "レイヤー",
        "panel.connections": "接続",
        "panel.source": "ソース",
        "panel.expand": "拡大",
        "panel.process_flows": "プロセスフロー",
        "flow.steps": "ステップ",
        "flow.files": "ファイル",
        "flow.confidence": "信頼度",
        "flow.entry": "開始",
        "flow.exit": "終了",
        "flow.open_first_step": "最初のステップを開く",
        "flow.more_steps": "件の追加ステップ",
        "empty.files": "ファイルがありません。",
        "empty.domains": "ドメインが検出されませんでした。",
        "empty.docs": "リンクされたドキュメントはありません。",
        "empty.knowledge": "リンクできるMarkdownドキュメントはありません。",
        "filter.node_types": "ノード種別",
        "filter.complexity": "複雑度",
        "filter.reset": "フィルターをリセット",
        "theme.title": "テーマ",
        "theme.accent": "アクセント色",
        "theme.heading_font": "見出しフォント",
        "terminal.title": "ターミナル",
        "terminal.subtitle": "グラフクエリ + JS · 100%オフライン · help と入力",
        "terminal.help_intro": "埋め込みグラフを使って、このコードベースをオフラインで調査します:",
        "terminal.none": "(なし)",
        "terminal.no_domains": "ドメインが検出されませんでした",
        "terminal.no_steps": "ステップなし",
        "terminal.unknown": "不明なコマンド",
        "terminal.try_help": "helpを試してください",
        "modal.path_title": "依存経路ファインダー",
        "modal.find_path": "経路を検索",
        "modal.clear": "クリア",
        "help.title": "キーボードショートカット",
        "help.subtitle": "マウスなしでグラフ全体を操作できます。",
        "help.general": "一般",
        "help.navigation": "ナビゲーション",
        "help.view_modes": "表示モード",
        "help.guided_tour": "ガイドツアー",
    },
    "ar": {
        "nav.overview": "نظرة عامة",
        "nav.drill": "تفصيل",
        "nav.explore": "استكشاف",
        "nav.tour": "جولة",
        "nav.graph": "الرسم",
        "map.structural": "هيكلي",
        "map.domain": "المجال",
        "map.knowledge": "المعرفة",
        "panel.info": "معلومات",
        "panel.files": "الملفات",
        "action.fit": "ملاءمة",
        "action.path": "المسار",
        "action.filter": "تصفية",
        "action.export": "تصدير",
        "action.flow": "التدفق",
        "action.theme": "السمة",
        "action.term": "الطرفية",
        "action.refresh": "تحديث",
        "action.help": "مساعدة",
        "action.diff": "الفروقات",
        "action.functions": "الدوال",
        "action.facets": "الأوجه",
        "detail.files": "الملفات",
        "detail.classes": "+الفئات",
        "search.fuzzy": "تقريبي",
        "search.semantic": "دلالي",
        "label.tools": "الأدوات",
        "label.analysis": "التحليل",
        "label.detail": "التفاصيل",
        "label.search": "بحث",
        "label.actions": "الإجراءات",
        "label.search_placeholder": "بحث {scope}",
        "label.search_nodes": "ابحث في العقد...",
        "overview.nodes": "العقد",
        "overview.edges": "الروابط",
        "overview.layers": "الطبقات",
        "overview.types": "الأنواع",
        "overview.languages": "اللغات",
        "overview.frameworks": "الأطر",
        "overview.node_types": "أنواع العقد",
        "overview.most_connected": "الأكثر اتصالا",
        "overview.project_tour": "جولة المشروع",
        "overview.start_tour": "ابدأ الجولة",
        "domain.blurb": "مجالات العمل المستنتجة من بنية المشروع مع التدفقات بينها.",
        "domain.entities": "الكيانات",
        "knowledge.blurb": "مستندات Markdown كمواد معرفية مرتبطة بالروابط والاستشهادات.",
        "panel.documentation": "التوثيق",
        "panel.language_notes": "ملاحظات اللغة",
        "panel.layer": "الطبقة",
        "panel.connections": "الاتصالات",
        "panel.source": "المصدر",
        "panel.expand": "توسيع",
        "panel.process_flows": "تدفقات العملية",
        "flow.steps": "خطوات",
        "flow.files": "ملفات",
        "flow.confidence": "الثقة",
        "flow.entry": "البداية",
        "flow.exit": "النهاية",
        "flow.open_first_step": "افتح الخطوة الأولى",
        "flow.more_steps": "خطوات إضافية",
        "empty.files": "لا توجد ملفات.",
        "empty.domains": "لم يتم اكتشاف مجالات.",
        "empty.docs": "لا توجد مستندات مرتبطة.",
        "empty.knowledge": "لا توجد مستندات Markdown للربط.",
        "filter.node_types": "أنواع العقد",
        "filter.complexity": "التعقيد",
        "filter.reset": "إعادة ضبط المرشحات",
        "theme.title": "السمة",
        "theme.accent": "لون التمييز",
        "theme.heading_font": "خط العناوين",
        "terminal.title": "الطرفية",
        "terminal.subtitle": "استعلامات الرسم + JS · دون اتصال · اكتب help",
        "terminal.help_intro": "استكشف هذا المشروع دون اتصال عبر الرسم المضمن:",
        "terminal.none": "(لا شيء)",
        "terminal.no_domains": "لم يتم اكتشاف مجالات",
        "terminal.no_steps": "لا توجد خطوات",
        "terminal.unknown": "أمر غير معروف",
        "terminal.try_help": "جرّب help",
        "modal.path_title": "مكتشف مسار الاعتماد",
        "modal.find_path": "ابحث عن المسار",
        "modal.clear": "مسح",
        "help.title": "اختصارات لوحة المفاتيح",
        "help.subtitle": "تحكم في الرسم بالكامل من لوحة المفاتيح.",
        "help.general": "عام",
        "help.navigation": "التنقل",
        "help.view_modes": "أوضاع العرض",
        "help.guided_tour": "جولة موجهة",
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
    "ko": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "ru": {"nav.overview": "Overview", "nav.explore": "Explore"},
    "hi": {"nav.overview": "Overview", "nav.explore": "Explore"},
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
