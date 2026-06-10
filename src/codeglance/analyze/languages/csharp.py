"""C# — methods/constructors, classes/interfaces/structs/enums/records, and fields."""

from ..base import TreeSitterLang
from ..registry import register


@register
class CSharp(TreeSitterLang):
    """Tree-sitter extraction rules for C# source files."""

    id = "csharp"
    grammar = "csharp"
    extensions = (".cs",)
    func = {"method_declaration", "constructor_declaration", "local_function_statement"}
    cls = {"class_declaration", "interface_declaration", "struct_declaration",
           "enum_declaration", "record_declaration"}
    method = {"method_declaration", "constructor_declaration"}
