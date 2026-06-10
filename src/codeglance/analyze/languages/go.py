"""Go — functions/methods, type specs (structs/interfaces), and top-level var/const."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Go(TreeSitterLang):
    """Tree-sitter extraction rules for Go source files."""

    id = "go"
    grammar = "go"
    extensions = (".go",)
    func = {"function_declaration", "method_declaration"}
    cls = {"type_spec"}
    var = {"var_declaration", "const_declaration"}
