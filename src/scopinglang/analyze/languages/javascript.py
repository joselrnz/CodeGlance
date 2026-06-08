"""JavaScript — functions, classes, methods, and top-level var/let/const."""

from ..base import TreeSitterLang
from ..registry import register


@register
class JavaScript(TreeSitterLang):
    id = "javascript"
    grammar = "javascript"
    extensions = (".js", ".jsx", ".mjs", ".cjs")
    func = {"function_declaration", "generator_function_declaration", "method_definition"}
    cls = {"class_declaration"}
    method = {"method_definition"}
    var = {"lexical_declaration", "variable_declaration"}
