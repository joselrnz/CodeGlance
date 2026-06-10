"""PHP — functions/methods, classes/interfaces/traits/enums, consts, and properties."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Php(TreeSitterLang):
    """Tree-sitter extraction rules for PHP source files."""

    id = "php"
    grammar = "php"
    extensions = (".php",)
    func = {"function_definition", "method_declaration"}
    cls = {"class_declaration", "interface_declaration", "trait_declaration", "enum_declaration"}
    method = {"method_declaration"}
    var = {"const_declaration"}
