"""Rust — functions, structs/enums/traits/unions, and const/static items.

(``impl`` block methods are associated with their type by the engine's Rust path.)
"""

from ..base import TreeSitterLang
from ..registry import register


@register
class Rust(TreeSitterLang):
    id = "rust"
    grammar = "rust"
    extensions = (".rs",)
    func = {"function_item"}
    cls = {"struct_item", "enum_item", "trait_item", "union_item"}
    var = {"const_item", "static_item"}
