"""Lua — function declarations/definitions (no class container in the grammar)."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Lua(TreeSitterLang):
    id = "lua"
    grammar = "lua"
    extensions = (".lua",)
    func = {"function_declaration", "function_definition"}
