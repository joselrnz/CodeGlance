"""Ruby — methods (incl. singleton) and class/module containers."""

from ..base import TreeSitterLang
from ..registry import register


@register
class Ruby(TreeSitterLang):
    """Tree-sitter extraction rules for Ruby source files."""

    id = "ruby"
    grammar = "ruby"
    extensions = (".rb",)
    func = {"method", "singleton_method"}
    cls = {"class", "module"}
    method = {"method", "singleton_method"}
