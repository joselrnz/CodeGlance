"""Scala — functions, classes/objects/traits, and val/var definitions."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Scala(TreeSitterLang):
    """Tree-sitter extraction rules for Scala source files."""

    id = "scala"
    grammar = "scala"
    extensions = (".scala",)
    func = {"function_definition"}
    cls = {"class_definition", "object_definition", "trait_definition"}
    method = {"function_definition"}
    var = {"val_definition", "var_definition"}
