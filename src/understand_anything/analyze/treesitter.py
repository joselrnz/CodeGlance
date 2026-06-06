"""Multi-language symbol extraction via tree-sitter (optional `[treesitter]` extra).

Extracts functions / classes / methods for many languages by walking the parse tree and matching
node types. Falls back silently (returns None) when the extra isn't installed. Python is handled
by the stdlib `ast` path in structural.py, so it is intentionally not covered here.
"""

from __future__ import annotations

from functools import lru_cache

# our scan language id -> tree-sitter-language-pack grammar name
_TS_NAME = {
    "javascript": "javascript", "typescript": "typescript", "go": "go", "rust": "rust",
    "java": "java", "ruby": "ruby", "php": "php", "csharp": "csharp", "c": "c", "cpp": "cpp",
    "kotlin": "kotlin", "swift": "swift", "lua": "lua", "scala": "scala",
}

# Per-language node types. func = standalone callable; cls = type-like container;
# method = callable defined directly inside a class body.
_F = "func"
_C = "cls"
_M = "method"
_SPECS: dict[str, dict[str, set[str]]] = {
    "javascript": {
        _F: {"function_declaration", "generator_function_declaration", "method_definition"},
        _C: {"class_declaration"},
        _M: {"method_definition"},
    },
    "typescript": {
        _F: {"function_declaration", "generator_function_declaration", "method_definition",
             "function_signature", "method_signature"},
        _C: {"class_declaration", "interface_declaration", "abstract_class_declaration",
             "enum_declaration"},
        _M: {"method_definition", "method_signature"},
    },
    "go": {
        _F: {"function_declaration", "method_declaration"},
        _C: {"type_spec"},
        _M: set(),
    },
    "rust": {
        _F: {"function_item"},
        _C: {"struct_item", "enum_item", "trait_item", "union_item"},
        _M: set(),
    },
    "java": {
        _F: {"method_declaration", "constructor_declaration"},
        _C: {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"},
        _M: {"method_declaration", "constructor_declaration"},
    },
    "ruby": {
        _F: {"method", "singleton_method"},
        _C: {"class", "module"},
        _M: {"method", "singleton_method"},
    },
    "php": {
        _F: {"function_definition", "method_declaration"},
        _C: {"class_declaration", "interface_declaration", "trait_declaration", "enum_declaration"},
        _M: {"method_declaration"},
    },
    "csharp": {
        _F: {"method_declaration", "constructor_declaration", "local_function_statement"},
        _C: {"class_declaration", "interface_declaration", "struct_declaration",
             "enum_declaration", "record_declaration"},
        _M: {"method_declaration", "constructor_declaration"},
    },
    "c": {
        _F: {"function_definition"},
        _C: {"struct_specifier", "union_specifier", "enum_specifier"},
        _M: set(),
    },
    "cpp": {
        _F: {"function_definition"},
        _C: {"class_specifier", "struct_specifier", "union_specifier", "enum_specifier"},
        _M: {"function_definition"},
    },
    "kotlin": {
        _F: {"function_declaration"},
        _C: {"class_declaration", "object_declaration", "interface_declaration"},
        _M: {"function_declaration"},
    },
    "swift": {
        _F: {"function_declaration"},
        _C: {"class_declaration", "protocol_declaration", "struct_declaration"},
        _M: {"function_declaration"},
    },
    "lua": {
        _F: {"function_declaration", "function_definition"},
        _C: set(),
        _M: set(),
    },
    "scala": {
        _F: {"function_definition"},
        _C: {"class_definition", "object_definition", "trait_definition"},
        _M: {"function_definition"},
    },
}

# Node types whose text is a usable identifier (fallback when no 'name' field).
_NAME_NODE_TYPES = {
    "identifier", "type_identifier", "field_identifier", "simple_identifier", "constant",
    "name", "scoped_identifier", "property_identifier", "word",
}


def supported_languages() -> set[str]:
    return set(_SPECS)


@lru_cache(maxsize=1)
def is_available() -> bool:
    try:
        import tree_sitter_language_pack  # noqa: F401
        return True
    except Exception:
        return False


@lru_cache(maxsize=64)
def _parser(grammar: str):
    from tree_sitter_language_pack import get_parser
    return get_parser(grammar)


def _grammar_for(language: str, path: str) -> str | None:
    if language == "typescript" and path.endswith(".tsx"):
        return "tsx"
    return _TS_NAME.get(language)


# The tree-sitter-language-pack binding exposes node accessors as methods (e.g. node.kind(),
# node.child_count()) rather than properties, and has no .text — text comes from byte offsets.
# These helpers tolerate either form so we survive minor binding differences.

def _call(attr):
    return attr() if callable(attr) else attr


def _kind(node) -> str:
    return _call(node.kind)


def _children(node) -> list:
    return [node.child(i) for i in range(_call(node.child_count))]


def _text(node, src_bytes: bytes) -> str:
    return src_bytes[_call(node.start_byte):_call(node.end_byte)].decode("utf-8", "ignore")


def _root(tree):
    return _call(tree.root_node)


def _name_of(node, sb: bytes) -> str:
    try:
        nn = node.child_by_field_name("name")
        if nn is not None:
            return _text(nn, sb)
        for ch in _children(node):
            if _kind(ch) in _NAME_NODE_TYPES:
                return _text(ch, sb)
        decl = node.child_by_field_name("declarator")
        if decl is not None:
            return _name_of(decl, sb)
    except Exception:
        return ""
    return ""


def _body_of(node):
    body = node.child_by_field_name("body")
    if body is not None:
        return body
    for ch in _children(node):
        if _kind(ch).endswith(("body", "declaration_list", "block", "field_declaration_list")):
            return ch
    return None


def extract_symbols(language: str, path: str, text: str):
    """Return list of {kind, name, methods, doc} or None if extraction is unavailable."""
    if not is_available():
        return None
    grammar = _grammar_for(language, path)
    spec = _SPECS.get(language)
    if grammar is None or spec is None:
        return None
    try:
        tree = _parser(grammar).parse(text)
        root = _root(tree)
    except Exception:
        return None

    sb = text.encode("utf-8", "ignore")
    func_types, cls_types, method_types = spec[_F], spec[_C], spec[_M]
    callable_types = func_types | method_types
    symbols: list[dict] = []
    impl_methods: dict[str, list[str]] = {}  # Rust: type name -> methods from impl blocks

    def visit(node, inside_class: bool):
        k = _kind(node)
        # Rust: methods live in `impl Type { fn ... }`, separate from the struct/enum definition.
        if language == "rust" and k == "impl_item":
            tname = _impl_type_name(node, sb)
            body = _body_of(node)
            if tname and body is not None:
                for ch in _children(body):
                    if _kind(ch) in func_types:
                        mn = _name_of(ch, sb)
                        if mn:
                            impl_methods.setdefault(tname, []).append(mn)
            return  # don't emit impl functions as free functions
        if k in cls_types:
            cname = _name_of(node, sb)
            if cname:
                methods = []
                body = _body_of(node)
                if body is not None:
                    for ch in _children(body):
                        if _kind(ch) in callable_types:
                            mn = _name_of(ch, sb)
                            if mn:
                                methods.append(mn)
                symbols.append({"kind": "class", "name": cname, "methods": methods, "doc": ""})
            return  # don't descend (methods already captured; avoids double-counting)
        if k in func_types and not inside_class:
            fn = _name_of(node, sb)
            if fn:
                symbols.append({"kind": "function", "name": fn, "methods": [], "doc": ""})
        for ch in _children(node):
            visit(ch, inside_class)

    try:
        visit(root, False)
    except Exception:
        pass

    # Merge Rust impl methods into their type's class (or synthesize one if defined elsewhere).
    if impl_methods:
        by_name = {s["name"]: s for s in symbols if s["kind"] == "class"}
        for tname, meths in impl_methods.items():
            target = by_name.get(tname)
            if target is None:
                target = {"kind": "class", "name": tname, "methods": [], "doc": ""}
                symbols.append(target)
                by_name[tname] = target
            for m in meths:
                if m not in target["methods"]:
                    target["methods"].append(m)
    return symbols


def _impl_type_name(node, sb: bytes) -> str:
    tn = node.child_by_field_name("type")
    if tn is None:
        for ch in _children(node):
            if _kind(ch) in ("type_identifier", "generic_type", "scoped_type_identifier"):
                tn = ch
                break
    if tn is None:
        return ""
    txt = _text(tn, sb)
    return txt.split("<")[0].split("::")[-1].strip()
