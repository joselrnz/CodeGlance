"""Python language support — symbol extraction and import resolution via the stdlib ``ast``.

Python is the one language handled without tree-sitter: the standard library's ``ast`` module
yields precise signatures, docstrings, line ranges, module-level variables/constants and class
attributes. The analysis pipeline uses this for every ``.py`` file.
"""

from __future__ import annotations

import ast


class _PyImport:
    __slots__ = ("module", "level", "names")

    def __init__(self, module: str | None, level: int, names: list[str]):
        self.module = module
        self.level = level
        self.names = names


def _py_line_range(node) -> list[int]:
    """Return [startLine, endLine] (1-indexed) for an AST node."""
    return [node.lineno, getattr(node, "end_lineno", None) or node.lineno]


def _py_func_sig(node) -> str:
    """Reconstruct a readable signature for a function/method AST node."""
    try:
        args = ast.unparse(node.args)
    except Exception:
        args = ""
    ret = ""
    try:
        if node.returns is not None:
            ret = " -> " + ast.unparse(node.returns)
    except Exception:
        ret = ""
    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    return f"{prefix}{node.name}({args}){ret}"


def _py_class_sig(node) -> str:
    """Reconstruct a readable `class Name(bases)` signature for a ClassDef node."""
    try:
        bases = ", ".join(ast.unparse(b) for b in node.bases)
    except Exception:
        bases = ""
    return f"class {node.name}({bases})" if bases else f"class {node.name}"


def _py_symbol(node, kind: str) -> dict:
    """Build a rich symbol dict (name/doc/docstring/lineRange/signature) from an AST node."""
    full_doc = (ast.get_docstring(node) or "").strip()
    sig = _py_class_sig(node) if kind == "class" else _py_func_sig(node)
    return {
        "kind": kind,
        "name": node.name,
        "doc": full_doc.split("\n")[0][:200],   # first line → summary
        "docstring": full_doc[:600],            # full docstring → docstring field
        "lineRange": _py_line_range(node),
        "signature": sig,
        "methods": [],
    }


def _py_vars_from(node):
    """Yield (name, kind) for each simple Name target of an Assign/AnnAssign (handles a, b = ...)."""
    targets = []
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            targets.append(node.target)
    else:  # ast.Assign
        for t in node.targets:
            if isinstance(t, ast.Name):
                targets.append(t)
            elif isinstance(t, (ast.Tuple, ast.List)):
                targets.extend(e for e in t.elts if isinstance(e, ast.Name))
    for t in targets:
        nm = t.id
        if nm == "_" or nm.startswith("__"):
            continue
        yield nm, ("constant" if nm.isupper() and len(nm) > 1 else "variable")


def _py_var_symbol(node, name: str, kind: str) -> dict:
    """Build a variable/constant symbol dict from an Assign/AnnAssign node."""
    try:
        sig = ast.unparse(node)
    except Exception:
        sig = name
    return {
        "kind": kind, "name": name, "doc": "", "docstring": "",
        "lineRange": _py_line_range(node),
        "signature": sig.replace("\n", " ")[:120], "methods": [],
    }


def _python_extract(text: str):
    """Return (module_doc_first_line, module_docstring, symbols, imports).

    symbols is a list of rich dicts (functions/classes, classes carry method dicts).
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return "", "", [], []

    module_docstring = (ast.get_docstring(tree) or "").strip()
    module_doc = module_docstring.split("\n")[0][:240]
    symbols: list[dict] = []
    imports: list[_PyImport] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(_py_symbol(node, "function"))
        elif isinstance(node, ast.ClassDef):
            sym = _py_symbol(node, "class")
            sym["methods"] = [
                _py_symbol(b, "function")
                for b in node.body if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            sym["fields"] = [
                _py_var_symbol(b, nm, kind)
                for b in node.body if isinstance(b, (ast.Assign, ast.AnnAssign))
                for nm, kind in _py_vars_from(b)
            ]
            symbols.append(sym)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for nm, kind in _py_vars_from(node):
                symbols.append(_py_var_symbol(node, nm, kind))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(_PyImport(alias.name, 0, []))
        elif isinstance(node, ast.ImportFrom):
            imports.append(_PyImport(node.module, node.level or 0, [a.name for a in node.names]))
    return module_doc, module_docstring, symbols, imports


def _name_of(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


class _ModuleIndex:
    """Maps dotted module names (and suffixes) to Python file node ids."""

    def __init__(self):
        self._map: dict[str, str] = {}

    def add(self, rel_path: str):
        parts = rel_path[:-3].split("/") if rel_path.endswith(".py") else rel_path.split("/")
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        for i in range(len(parts)):
            suffix = ".".join(parts[i:])
            if suffix:
                self._map.setdefault(suffix, rel_path)

    def resolve(self, dotted: str) -> str | None:
        parts = dotted.split(".")
        for j in range(len(parts), 0, -1):
            cand = ".".join(parts[:j])
            if cand in self._map:
                return self._map[cand]
        return None


def _resolve_py_import(imp: _PyImport, cur_rel: str, index: _ModuleIndex) -> list[str]:
    targets: list[str] = []
    if imp.level and imp.level > 0:
        cur_parts = cur_rel[:-3].split("/")
        pkg = cur_parts[:-1]  # package containing this module
        base = pkg[: len(pkg) - (imp.level - 1)] if imp.level > 1 else pkg
        prefix = ".".join(base)
        if imp.module:
            dotted = f"{prefix}.{imp.module}" if prefix else imp.module
            t = index.resolve(dotted)
            if t:
                targets.append(t)
        for name in imp.names:
            dotted = f"{prefix}.{imp.module}.{name}" if imp.module else (f"{prefix}.{name}" if prefix else name)
            t = index.resolve(dotted)
            if t:
                targets.append(t)
    elif imp.module:
        t = index.resolve(imp.module)
        if t:
            targets.append(t)
        for name in imp.names:
            t2 = index.resolve(f"{imp.module}.{name}")
            if t2:
                targets.append(t2)
    return targets
