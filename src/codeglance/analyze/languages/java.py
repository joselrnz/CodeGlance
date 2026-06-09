"""Java — methods/constructors, classes/interfaces/enums/records, and fields."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Java(TreeSitterLang):
    id = "java"
    grammar = "java"
    extensions = (".java",)
    func = {"method_declaration", "constructor_declaration"}
    cls = {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"}
    method = {"method_declaration", "constructor_declaration"}
