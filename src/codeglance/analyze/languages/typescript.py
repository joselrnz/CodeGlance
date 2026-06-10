"""TypeScript / TSX — functions, classes, interfaces, enums, methods, variables.

(.tsx files parse with the ``tsx`` grammar — handled by the engine's grammar lookup.)
"""

from ..base import TreeSitterLang
from ..registry import register


@register
class TypeScript(TreeSitterLang):
    """Tree-sitter extraction rules for TypeScript and TSX files."""

    id = "typescript"
    grammar = "typescript"
    extensions = (".ts", ".tsx")
    func = {"function_declaration", "generator_function_declaration", "method_definition",
            "function_signature", "method_signature"}
    cls = {"class_declaration", "interface_declaration", "abstract_class_declaration",
           "enum_declaration"}
    method = {"method_definition", "method_signature"}
    var = {"lexical_declaration", "variable_declaration"}
