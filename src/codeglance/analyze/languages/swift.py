"""Swift — functions, classes/protocols/structs, and properties."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Swift(TreeSitterLang):
    id = "swift"
    grammar = "swift"
    extensions = (".swift",)
    func = {"function_declaration"}
    cls = {"class_declaration", "protocol_declaration", "struct_declaration"}
    method = {"function_declaration"}
    var = {"property_declaration"}
