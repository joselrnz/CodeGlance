"""Kotlin — functions, classes/objects/interfaces, and top-level/class properties."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Kotlin(TreeSitterLang):
    id = "kotlin"
    grammar = "kotlin"
    extensions = (".kt", ".kts")
    func = {"function_declaration"}
    cls = {"class_declaration", "object_declaration", "interface_declaration"}
    method = {"function_declaration"}
    var = {"property_declaration"}
