"""Declarative language definitions for the analyzer registry.

Each *tuned* language is a tiny subclass of :class:`TreeSitterLang` living in
``languages/<id>.py`` — it declares only the tree-sitter node-kinds to extract.
The shared extraction engine reads these specs through the registry, so adding or
reading a language means one small file instead of editing a monolith.
"""

from __future__ import annotations


class TreeSitterLang:
    """A tuned tree-sitter language: just the node-kinds the engine should extract."""

    id: str = ""                       # scan language id (e.g. "go")
    grammar: str = ""                  # tree-sitter-language-pack grammar name
    extensions: tuple = ()             # file extensions (".go",) — for reference/derivation
    func: set = frozenset()            # standalone callables
    cls: set = frozenset()             # type-like containers (class/struct/enum/trait/...)
    method: set = frozenset()          # callables defined inside a class body
    var: set = frozenset()             # top-level variable / constant declarations
