"""Language registry — the dispatcher that assembles every language's extraction
spec from the per-language modules in ``languages/``.

The tree-sitter engine pulls ``specs()`` (tuned node-kinds) and ``grammars()``
(grammar name for every supported language) from here instead of hardcoding them.
"""

from __future__ import annotations

_TUNED: dict = {}        # language id -> TreeSitterLang subclass
_GENERIC: dict = {}      # language id -> tree-sitter grammar name (generic-classifier langs)
_loaded = False


def register(cls):
    """Class decorator: register a tuned :class:`TreeSitterLang` definition."""
    _TUNED[cls.id] = cls
    return cls


def register_generic(language: str, grammar: str) -> None:
    """Register a language handled by the generic node-kind classifier."""
    _GENERIC[language] = grammar


def _ensure_loaded() -> None:
    """Import the languages package once so every module self-registers."""
    global _loaded
    if not _loaded:
        _loaded = True
        from . import languages  # noqa: F401  (import triggers registration)


def specs() -> dict:
    """``{language: {func, cls, method, var}}`` for the tuned languages."""
    _ensure_loaded()
    return {c.id: {"func": set(c.func), "cls": set(c.cls),
                   "method": set(c.method), "var": set(c.var)}
            for c in _TUNED.values()}


def grammars() -> dict:
    """``{language: grammar}`` for ALL supported languages (tuned + generic)."""
    _ensure_loaded()
    out = {c.id: c.grammar for c in _TUNED.values()}
    for lang, gram in _GENERIC.items():
        out.setdefault(lang, gram)
    return out


def extensions() -> dict:
    """``{extension: language}`` derived from the registered tuned languages."""
    _ensure_loaded()
    out: dict = {}
    for c in _TUNED.values():
        for ext in c.extensions:
            out.setdefault(ext, c.id)
    return out
