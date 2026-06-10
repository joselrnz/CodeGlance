"""Lua — function declarations/definitions (no class container in the grammar)."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Lua(TreeSitterLang):
    """Tree-sitter extraction rules for Lua source files."""

    id = "lua"
    grammar = "lua"
    extensions = (".lua",)
    func = {"function_declaration", "function_definition"}
