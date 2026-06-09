"""C++ — functions/methods, classes/structs/unions/enums, and fields."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Cpp(TreeSitterLang):
    id = "cpp"
    grammar = "cpp"
    extensions = (".cc", ".cpp", ".cxx", ".hh", ".hpp")
    func = {"function_definition"}
    cls = {"class_specifier", "struct_specifier", "union_specifier", "enum_specifier"}
    method = {"function_definition"}
