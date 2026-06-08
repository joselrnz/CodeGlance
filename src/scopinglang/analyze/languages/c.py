"""C — functions and struct/union/enum types (struct members captured as fields)."""

from ..base import TreeSitterLang
from ..registry import register


@register
class C(TreeSitterLang):
    id = "c"
    grammar = "c"
    extensions = (".c", ".h")
    func = {"function_definition"}
    cls = {"struct_specifier", "union_specifier", "enum_specifier"}
