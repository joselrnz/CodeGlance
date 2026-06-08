"""Multi-language symbol extraction via tree-sitter (optional `[treesitter]` extra).

Extracts functions / classes / methods for many languages by walking the parse tree and matching
node types. Falls back silently (returns None) when the extra isn't installed. Python is handled
by the stdlib `ast` path in structural.py, so it is intentionally not covered here.
"""

from __future__ import annotations

import re
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
    "shell": "bash", "terraform": "terraform", "hcl": "hcl",
}

# Per-language node types. func = standalone callable; cls = type-like container;
# method = callable defined directly inside a class body.
_F = "func"
_C = "cls"
_M = "method"
_V = "var"   # top-level variable / constant declaration
_SPECS: dict[str, dict[str, set[str]]] = {
    "javascript": {
        _F: {"function_declaration", "generator_function_declaration", "method_definition"},
        _C: {"class_declaration"},
        _M: {"method_definition"},
        _V: {"lexical_declaration", "variable_declaration"},
    },
    "typescript": {
        _F: {"function_declaration", "generator_function_declaration", "method_definition",
             "function_signature", "method_signature"},
        _C: {"class_declaration", "interface_declaration", "abstract_class_declaration",
             "enum_declaration"},
        _M: {"method_definition", "method_signature"},
        _V: {"lexical_declaration", "variable_declaration"},
    },
    "go": {
        _F: {"function_declaration", "method_declaration"},
        _C: {"type_spec"},
        _M: set(),
        _V: {"var_declaration", "const_declaration"},
    },
    "rust": {
        _F: {"function_item"},
        _C: {"struct_item", "enum_item", "trait_item", "union_item"},
        _M: set(),
        _V: {"const_item", "static_item"},
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
        _V: {"const_declaration"},
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
        _V: {"property_declaration"},
    },
    "swift": {
        _F: {"function_declaration"},
        _C: {"class_declaration", "protocol_declaration", "struct_declaration"},
        _M: {"function_declaration"},
        _V: {"property_declaration"},
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
        _V: {"val_definition", "var_definition"},
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
# Standalone variable/constant declaration kinds (generic classifier — VHDL signals, Fortran/Ada
# variables, etc.). Interface/port/param declarations are excluded via _GEN_DENY_KINDS.
_GEN_VAR_SUFFIX = (
    "variable_declaration", "constant_declaration", "const_declaration", "var_declaration",
    "let_declaration", "global_variable_declaration", "signal_declaration", "global_declaration",
    "val_definition", "var_definition", "constant_definition", "variable_definition",
)
# Class/struct member declarations (captured as fields of their enclosing type, across tuned langs).
_FIELD_KINDS = {
    "field_declaration", "property_declaration", "property_signature", "public_field_definition",
    "field_definition", "constant_declaration", "const_declaration", "val_definition",
    "var_definition", "property_definition",
}


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
    if kind.endswith(_GEN_VAR_SUFFIX):
        return "var"
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


def _point_row(p) -> int:
    """Row (0-indexed) from a tree-sitter point, tolerating tuple or object form."""
    try:
        return p[0] if isinstance(p, (tuple, list)) else getattr(p, "row", 0)
    except Exception:
        return 0


def _line_range(node) -> list[int] | None:
    """Return [startLine, endLine] (1-indexed) for a node, or None if unavailable."""
    try:
        return [_point_row(_call(node.start_position)) + 1, _point_row(_call(node.end_position)) + 1]
    except Exception:
        return None


def _sig_line(node, sb: bytes) -> str:
    """First source line of a node — a decent stand-in for the declaration signature."""
    return _text(node, sb).split("\n", 1)[0].strip()[:200]


def _clean_comment(text: str) -> str:
    """Strip comment markers (// /* */ # -- ; <!-- --> ''') and collapse to one doc string."""
    text = text.strip()
    for tok in ("/**", "*/", "<!--", "-->", '"""', "'''"):
        text = text.replace(tok, "")
    out = []
    for ln in text.splitlines():
        ln = ln.strip().lstrip("/#*-;").strip()
        if ln:
            out.append(ln)
    return " ".join(out)[:400]


def _symbol(node, kind: str, sb: bytes, lead_text: str = "") -> dict:
    """Build a rich symbol dict (name/doc/docstring/lineRange/signature) for a node."""
    doc_full = _clean_comment(lead_text) if lead_text else ""
    return {
        "kind": kind,
        "name": _name_of(node, sb),
        "doc": doc_full.split(". ")[0][:200] if doc_full else "",  # first sentence → summary
        "docstring": doc_full,
        "lineRange": _line_range(node),
        "signature": _sig_line(node, sb),
        "methods": [],
    }


def _is_named(node) -> bool:
    """True for meaningful named nodes (not punctuation/keyword tokens like 'export' or '{')."""
    try:
        return bool(_call(node.is_named))
    except Exception:
        return True


def _iter_with_comments(node):
    """Yield (child, leading_comment_node_or_None), pairing each doc-comment with what follows."""
    pending = None
    for ch in _children(node):
        if "comment" in _kind(ch):
            pending = ch
            continue
        yield ch, pending
        pending = None


_VAR_SPEC_KINDS = {"var_spec", "const_spec", "variable_declarator", "short_var_declaration"}
# Identifier node kinds that actually name a declared variable (not types or literals).
_STRICT_NAME_KINDS = {
    "identifier", "simple_identifier", "field_identifier", "property_identifier",
    "variable_name", "name", "word", "global_variable", "instance_variable",
}
# Declaration keywords that must never be mistaken for a variable's name.
_DECL_KW = {
    "const", "var", "val", "let", "auto", "type", "constant", "signal", "variable", "field",
    "property", "static", "global", "local", "public", "private", "protected", "final",
    "readonly", "dim", "mut", "pub",
}


def _looks_const(node, sb: bytes) -> bool:
    """True if the declaration text reads like an immutable constant."""
    head = _text(node, sb)[:48].lower()
    return any(w in head for w in (" const", "const ", "constant", "final ", "readonly", "#define"))


def _var_name1(node, sb: bytes) -> str:
    """Best-effort single declared name for a declarator/spec node (skips keywords & types)."""
    nn = node.child_by_field_name("name")
    if nn is not None:
        t = _text(nn, sb).strip()
        if t and t.lower() not in _DECL_KW:
            return t
    for ch in _children(node):
        if _kind(ch) in _STRICT_NAME_KINDS:
            t = _text(ch, sb).strip()
            if t and t.lower() not in _DECL_KW:
                return t
    return ""


# Subtrees that hold values/types/bodies, not declared names — never descend into these.
_VAL_PRUNE = ("expression", "initializer", "literal", "call", "argument", "block", "body")


def _collect_var_names(node, sb, depth=0):
    """DFS for declared names, pruning value/type subtrees so initializers aren't mistaken for names."""
    out = []
    for ch in _children(node):
        k = _kind(ch)
        if k in ("var_spec", "const_spec"):            # Go/VHDL: names come before the type/value
            for g in _children(ch):
                gk = _kind(g)
                if gk in ("=", ":", ":=", "assignment_expression") or "type" in gk:
                    break
                if gk in _STRICT_NAME_KINDS:
                    t = _text(g, sb).strip()
                    if t and t.lower() not in _DECL_KW:
                        out.append(t)
        elif "declarator" in k or k.endswith("_element"):   # JS/Java/PHP declarators carry one name
            nm = _var_name1(ch, sb)
            if nm:
                out.append(nm)
        elif k == "identifier_list":                   # VHDL/Ada `signal a, b : t`
            for g in _children(ch):
                if _kind(g) in _STRICT_NAME_KINDS:
                    out.append(_text(g, sb))
        elif k in _STRICT_NAME_KINDS:
            t = _text(ch, sb).strip()
            if t and t.lower() not in _DECL_KW:
                out.append(t)
        elif depth < 4 and not any(p in k for p in _VAL_PRUNE):
            out.extend(_collect_var_names(ch, sb, depth + 1))
    return out


def _var_names(node, sb, base_kind: str):
    """Collect (name, kind) for a variable/const declaration (handles multi-name & block langs)."""
    found = _collect_var_names(node, sb)
    if not found:
        nm = _var_name1(node, sb)
        if nm:
            found = [nm]
    is_const = base_kind == "constant" or _looks_const(node, sb)
    out, seen = [], set()
    for nm in found:
        if nm in seen or nm.lower() in _DECL_KW or not _ok_generic_name(nm):
            continue
        seen.add(nm)
        kind = "constant" if (is_const or (nm.isupper() and len(nm) > 1)) else "variable"
        out.append((nm, kind))
    return out


def extract_symbols(language: str, path: str, text: str):
    """Return list of rich symbol dicts (name/doc/docstring/lineRange/signature/methods), or None."""
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

    if language in ("terraform", "hcl"):
        return _extract_terraform(root, sb)

    spec = _SPECS.get(language)
    if spec is None:
        return _extract_generic(root, sb)

    func_types, cls_types, method_types = spec[_F], spec[_C], spec[_M]
    callable_types = func_types | method_types
    var_types = spec.get(_V, set())
    symbols: list[dict] = []
    impl_methods: dict[str, list[dict]] = {}  # Rust: type name -> method dicts from impl blocks

    def lead_text(comment_node) -> str:
        return _text(comment_node, sb) if comment_node is not None else ""

    def visit(node, inside_class: bool, lead=None, depth=0):
        k = _kind(node)
        # Rust: methods live in `impl Type { fn ... }`, separate from the struct/enum definition.
        if language == "rust" and k == "impl_item":
            tname = _impl_type_name(node, sb)
            body = _body_of(node)
            if tname and body is not None:
                for ch, c in _iter_with_comments(body):
                    if _kind(ch) in func_types and _name_of(ch, sb):
                        impl_methods.setdefault(tname, []).append(_symbol(ch, "function", sb, lead_text(c)))
            return  # don't emit impl functions as free functions
        if depth == 1 and var_types and k in var_types and not inside_class:
            base = "constant" if ("const" in k or "static" in k) else "variable"
            for nm, kk in _var_names(node, sb, base):
                s = _symbol(node, kk, sb, lead_text(lead)); s["name"] = nm
                symbols.append(s)
            return
        if k in cls_types:
            cname = _name_of(node, sb)
            if cname:
                sym = _symbol(node, "class", sb, lead_text(lead))
                sym["name"] = cname
                body = _body_of(node)
                if body is not None:
                    for ch, c in _iter_with_comments(body):
                        ck = _kind(ch)
                        if ck in callable_types and _name_of(ch, sb):
                            sym["methods"].append(_symbol(ch, "function", sb, lead_text(c)))
                        elif ck in _FIELD_KINDS:
                            base = "constant" if "const" in ck else "variable"
                            for nm, kk in _var_names(ch, sb, base):
                                fs = _symbol(ch, kk, sb, lead_text(c)); fs["name"] = nm
                                sym.setdefault("fields", []).append(fs)
                symbols.append(sym)
            return  # don't descend (methods already captured; avoids double-counting)
        if k in func_types and not inside_class:
            if _name_of(node, sb):
                symbols.append(_symbol(node, "function", sb, lead_text(lead)))
        # This node emitted nothing — propagate any leading comment to the first NAMED child
        # (e.g. a JSDoc before `export function ...` belongs to the wrapped function, skipping
        # the 'export' keyword token).
        used = False
        for ch, c in _iter_with_comments(node):
            take = c
            if take is None and not used and _is_named(ch):
                take = lead
            if _is_named(ch):
                used = True
            visit(ch, inside_class, take, depth + 1)

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
                target = {"kind": "class", "name": tname, "methods": [], "doc": "",
                          "docstring": "", "lineRange": None, "signature": ""}
                symbols.append(target)
                by_name[tname] = target
            existing = {m["name"] for m in target["methods"] if isinstance(m, dict)}
            for m in meths:
                if m["name"] not in existing:
                    target["methods"].append(m)
    return symbols


# Dotted HCL references like aws_instance.web, module.net, var.region (each segment alpha-led).
_TF_REF = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*(?:\.[A-Za-z_][A-Za-z0-9_-]*)+)")
_TF_BUILTIN = {"each", "count", "self", "path", "terraform", "local"}


def _tf_refkey(btype: str, labels: list[str]) -> str:
    """The token other blocks use to reference this block (e.g. resource -> 'type.name')."""
    if btype == "resource" and len(labels) >= 2:
        return f"{labels[0]}.{labels[1]}"
    if btype == "data" and len(labels) >= 2:
        return f"data.{labels[0]}.{labels[1]}"
    if btype == "module" and labels:
        return f"module.{labels[0]}"
    if btype == "variable" and labels:
        return f"var.{labels[0]}"
    return ""


def _tf_refs(text: str, self_key: str) -> list[str]:
    """Find references to other blocks inside a block body, normalised to refkeys."""
    out: set[str] = set()
    for m in _TF_REF.finditer(text):
        segs = m.group(1).split(".")
        head = segs[0]
        if head in _TF_BUILTIN:
            continue
        if head == "var" and len(segs) >= 2:
            out.add(f"var.{segs[1]}")
        elif head == "module" and len(segs) >= 2:
            out.add(f"module.{segs[1]}")
        elif head == "data" and len(segs) >= 3:
            out.add(f"data.{segs[1]}.{segs[2]}")
        elif head not in ("var", "module", "data") and len(segs) >= 2:
            out.add(f"{segs[0]}.{segs[1]}")   # resource reference type.name
    out.discard(self_key)
    return sorted(out)


def _extract_terraform(root, sb: bytes):
    """Extract top-level HCL/Terraform blocks as symbols, with reference info for dependency edges."""
    body = root
    for ch in _children(root):
        if _kind(ch).endswith("body"):
            body = ch
            break
    symbols: list[dict] = []
    seen: set[str] = set()
    for node in _children(body):
        if _kind(node) != "block":
            continue
        btype, labels = "", []
        for ch in _children(node):
            k = _kind(ch)
            if k == "identifier" and not btype:
                btype = _text(ch, sb)
            elif "string" in k:
                labels.append(_text(ch, sb).strip('"').strip("'"))
        if not btype:
            continue
        name = btype + (" " + ".".join(labels) if labels else "")
        if name in seen:
            continue
        seen.add(name)
        refkey = _tf_refkey(btype, labels)
        refs = _tf_refs(_text(node, sb), refkey)
        symbols.append({"kind": "class", "name": name, "doc": "", "docstring": "",
                        "lineRange": _line_range(node), "signature": _sig_line(node, sb),
                        "methods": [], "refkey": refkey, "refs": refs})
    return symbols


def _extract_generic(root, sb: bytes):
    """Paradigm-agnostic flat extraction for languages without an explicit spec.

    Emits class-like and func-like nodes wherever they occur (no method nesting), so container
    languages (Fortran modules, VHDL architectures, Ada packages) keep their inner subprograms.
    """
    symbols: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def visit(node, lead=None):
        cls = _generic_classify(_kind(node))
        emitted = False
        if cls == "var":
            base = "constant" if "const" in _kind(node) else "variable"
            for nm, kk in _var_names(node, sb, base):
                if (kk, nm) in seen:
                    continue
                seen.add((kk, nm))
                s = _symbol(node, kk, sb, _text(lead, sb) if lead is not None else "")
                s["name"] = nm
                symbols.append(s)
                emitted = True
        elif cls:
            name = _name_of(node, sb)
            if _ok_generic_name(name) and (cls, name) not in seen:
                seen.add((cls, name))
                sym = _symbol(node, "class" if cls == "cls" else "function", sb,
                              _text(lead, sb) if lead is not None else "")
                sym["name"] = name
                symbols.append(sym)
                emitted = True
        used = False
        for ch, c in _iter_with_comments(node):
            take = c
            if take is None and not used and not emitted and _is_named(ch):
                take = lead
            if _is_named(ch):
                used = True
            visit(ch, take)

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
