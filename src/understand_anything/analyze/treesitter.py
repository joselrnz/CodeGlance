"""Multi-language symbol extraction via tree-sitter (optional `[treesitter]` extra).

Extracts functions / classes / methods for many languages by walking the parse tree and matching
node types. Falls back silently (returns None) when the extra isn't installed. Python is handled
by the stdlib `ast` path in structural.py, so it is intentionally not covered here.
"""

from __future__ import annotations

from functools import lru_cache

# our scan language id -> tree-sitter-language-pack grammar name
_TS_NAME = {
    # Tuned (explicit specs below)
    "javascript": "javascript", "typescript": "typescript", "go": "go", "rust": "rust",
    "java": "java", "ruby": "ruby", "php": "php", "csharp": "csharp", "c": "c", "cpp": "cpp",
    "kotlin": "kotlin", "swift": "swift", "lua": "lua", "scala": "scala",
    # Extra coverage (handled by the generic node-kind classifier)
    "vhdl": "vhdl", "cobol": "cobol", "fortran": "fortran", "ada": "ada", "verilog": "verilog",
    "haskell": "haskell", "ocaml": "ocaml", "erlang": "erlang", "elixir": "elixir",
    "julia": "julia", "dart": "dart", "solidity": "solidity", "objc": "objc", "groovy": "groovy",
    "perl": "perl", "pascal": "pascal", "zig": "zig", "nim": "nim", "crystal": "crystal", "d": "d",
    "clojure": "clojure", "elm": "elm", "r": "r", "matlab": "matlab", "powershell": "powershell",
    "tcl": "tcl", "commonlisp": "commonlisp", "scheme": "scheme", "racket": "racket",
    "gleam": "gleam", "odin": "odin", "glsl": "glsl", "hlsl": "hlsl", "wgsl": "wgsl",
    "shell": "bash",
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
    "name", "scoped_identifier", "property_identifier", "word", "designator", "value_name",
    "class_name", "module_name", "variable", "atom", "program_name", "entity_name",
    "global_variable", "function_name", "type_name", "object_identifier",
}

# Generic classifier (used for languages without an explicit _SPECS entry). Matches node-kind
# names by suffix so it works across arbitrary grammars (VHDL, COBOL, Fortran, Ada, ...).
_GEN_FUNC_SUFFIX = (
    "function_definition", "function_declaration", "function_body", "function_item",
    "function_clause", "method_definition", "method_declaration", "method_signature",
    "method_spec", "subroutine", "subprogram_body", "subprogram_declaration",
    "procedure_declaration", "procedure_body", "procedure_definition", "constructor_definition",
    "constructor_declaration", "func_definition", "fun_declaration", "value_definition",
    "paragraph_header", "macro_definition", "modifier_definition", "function_specification",
    "procedure_specification", "function_signature", "fun_definition",
)
_GEN_CLASS_SUFFIX = (
    "class_definition", "class_declaration", "class_specifier", "struct_item", "struct_specifier",
    "struct_declaration", "struct_definition", "interface_declaration", "trait_item",
    "enum_item", "enum_declaration", "enum_specifier", "module_definition", "module_declaration",
    "record_declaration", "protocol_declaration", "object_declaration", "entity_declaration",
    "architecture_body", "package_declaration", "derived_type_definition", "type_definition",
    "program_definition", "union_item", "union_specifier", "struct_type", "type_declaration",
    "contract_declaration", "library_declaration", "namespace_declaration", "namespace_definition",
    "abstract_definition", "primitive_definition", "data_type", "newtype", "package_body",
)


# Primitive/keyword names that the generic classifier sometimes grabs from type positions.
_GENERIC_NAME_DENY = {
    "int", "integer", "bool", "boolean", "uint", "float", "double", "char", "string", "str",
    "byte", "short", "long", "void", "bit", "word", "real", "number", "unit", "nil", "none",
    "self", "this", "true", "false", "null", "var", "val", "let", "const", "auto", "type",
    "uint256", "uint8", "address", "bytes", "object", "any", "std_logic", "signal",
}


def _ok_generic_name(name: str) -> bool:
    return (
        bool(name)
        and len(name) <= 64
        and " " not in name and "\n" not in name and "\t" not in name
        and name.lower() not in _GENERIC_NAME_DENY
    )


# VHDL interface (port/generic/param) declarations end in "interface_declaration" but are NOT types.
_GEN_DENY_KINDS = {
    "signal_interface_declaration", "constant_interface_declaration",
    "variable_interface_declaration", "file_interface_declaration",
    "procedure_interface_declaration", "function_interface_declaration",
    "package_interface_declaration", "type_interface_declaration",
}


def _generic_classify(kind: str) -> str | None:
    if kind in _GEN_DENY_KINDS:
        return None
    if "call" in kind or "expression" in kind or "invocation" in kind or "reference" in kind:
        return None
    if kind.endswith(_GEN_FUNC_SUFFIX):
        return "func"
    if kind == "module" or kind == "program" or kind == "submodule":  # Fortran-style containers
        return "cls"
    if kind.endswith(_GEN_CLASS_SUFFIX):
        return "cls"
    return None


def supported_languages() -> set[str]:
    # All languages we can parse — explicit specs plus generic-classifier coverage.
    return set(_TS_NAME)


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
        # Last resort for block-structured langs (Fortran, COBOL, VHDL, Ada): the name is nested
        # inside a *_statement / *_header child — pre-order DFS for the first identifier-like leaf.
        hit = _dfs_first_name(node, sb, 3)
        if hit:
            return hit
    except Exception:
        return ""
    return ""


def _dfs_first_name(node, sb: bytes, depth: int) -> str:
    if depth < 0:
        return ""
    for ch in _children(node):
        if _kind(ch) in _NAME_NODE_TYPES:
            return _text(ch, sb)
    for ch in _children(node):
        r = _dfs_first_name(ch, sb, depth - 1)
        if r:
            return r
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
    if grammar is None:
        return None
    try:
        tree = _parser(grammar).parse(text)
        root = _root(tree)
    except Exception:
        return None
    sb = text.encode("utf-8", "ignore")

    spec = _SPECS.get(language)
    if spec is None:
        return _extract_generic(root, sb)

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


def _extract_generic(root, sb: bytes):
    """Paradigm-agnostic flat extraction for languages without an explicit spec.

    Emits class-like and func-like nodes wherever they occur (no method nesting), so container
    languages (Fortran modules, VHDL architectures, Ada packages) keep their inner subprograms.
    """
    symbols: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def visit(node):
        cls = _generic_classify(_kind(node))
        if cls:
            name = _name_of(node, sb)
            if _ok_generic_name(name) and (cls, name) not in seen:
                seen.add((cls, name))
                symbols.append({"kind": "class" if cls == "cls" else "function",
                                "name": name, "methods": [], "doc": ""})
        for ch in _children(node):
            visit(ch)

    try:
        visit(root)
    except Exception:
        pass
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
