"""Deterministic structural extraction.

Produces graph nodes/edges with no LLM:
  - one node per file (typed by category)
  - Python: function/class nodes via stdlib `ast`, `contains` edges, resolved `imports` edges
  - JS/TS and other languages: file nodes + best-effort relative-import edges

This is the always-on, offline, free baseline. `--llm` enrichment layers on top of it.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from ..schema import Edge, Node, edge_weight
from ..scan import ScanResult, ScannedFile
from . import treesitter as ts
from . import imports as imp


# ---------------------------------------------------------------------------
# Node typing
# ---------------------------------------------------------------------------

def node_type_for(f: ScannedFile) -> str:
    lang, cat, path = f.language, f.category, f.path.lower()
    if lang == "terraform":
        return "resource"
    if lang in ("graphql", "protobuf"):
        return "schema"
    if lang == "sql":
        return "table"
    if lang == "dockerfile":
        return "service"
    if "/k8s/" in path or "kubernetes" in path or path.endswith("k8s.yaml"):
        return "service"
    if cat == "infra":
        if ".github/workflows/" in path:
            return "pipeline"
        return "service"
    if cat == "config" or lang == "csv":
        return "config"
    if cat == "docs":
        return "document"
    return "file"


def file_node_id(node_type: str, rel_path: str) -> str:
    return f"{node_type}:{rel_path}"


def _complexity(size_lines: int, symbols: int) -> str:
    score = size_lines + symbols * 25
    if score < 120:
        return "simple"
    if score < 500:
        return "moderate"
    return "complex"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _first_doc_comment(text: str, language: str) -> str:
    """Heuristic one-line summary from the head of a file."""
    lines = text.splitlines()[:60]
    line_comment = {
        "python": "#", "shell": "#", "ruby": "#", "yaml": "#", "toml": "#", "powershell": "#",
        "dockerfile": "#", "terraform": "#", "makefile": "#", "ini": ";",
    }.get(language)
    collected: list[str] = []
    for raw in lines:
        s = raw.strip()
        if not s:
            if collected:
                break
            continue
        if s.startswith(("#!", "<!--", "/*", "*/", "*", "//", '"""', "'''", "/**")):
            cleaned = s.lstrip("#!/*<>-\"' ").strip()
            if cleaned and not cleaned.startswith(("import", "from", "package", "use ")):
                collected.append(cleaned)
                if len(collected) >= 1:
                    break
            continue
        if line_comment and s.startswith(line_comment):
            cleaned = s.lstrip(line_comment).strip()
            if cleaned:
                collected.append(cleaned)
                break
        else:
            break
    summary = " ".join(collected).strip()
    return summary[:240]


def _fallback_summary(f: ScannedFile) -> str:
    label = {
        "code": "source file", "config": "configuration file", "docs": "documentation",
        "infra": "infrastructure definition", "script": "script", "data": "data file",
        "markup": "markup/schema file",
    }.get(f.category, "file")
    return f"{f.language.capitalize()} {label} ({f.sizeLines} lines)."


# ---------------------------------------------------------------------------
# Python extraction
# ---------------------------------------------------------------------------

class _PyImport:
    __slots__ = ("module", "level", "names")

    def __init__(self, module: str | None, level: int, names: list[str]):
        self.module = module
        self.level = level
        self.names = names


def _python_extract(text: str):
    """Return (module_doc, symbols, imports). symbols: list of dicts; imports: list[_PyImport]."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return "", [], []

    module_doc = (ast.get_docstring(tree) or "").strip().split("\n")[0][:240]
    symbols: list[dict] = []
    imports: list[_PyImport] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            symbols.append({
                "kind": "function", "name": node.name,
                "doc": (ast.get_docstring(node) or "").strip().split("\n")[0][:200],
                "methods": [],
            })
        elif isinstance(node, ast.ClassDef):
            methods = [
                b.name for b in node.body
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            symbols.append({
                "kind": "class", "name": node.name,
                "doc": (ast.get_docstring(node) or "").strip().split("\n")[0][:200],
                "methods": methods,
                "bases": [_name_of(b) for b in node.bases if _name_of(b)],
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(_PyImport(alias.name, 0, []))
        elif isinstance(node, ast.ImportFrom):
            imports.append(_PyImport(node.module, node.level or 0, [a.name for a in node.names]))
    return module_doc, symbols, imports


def _name_of(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


# ---------------------------------------------------------------------------
# Import resolution
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------

def build_structural(scan_result: ScanResult) -> tuple[list[Node], list[Edge]]:
    root = scan_result.root
    nodes: list[Node] = []
    edges: list[Edge] = []
    edge_keys: set[tuple] = set()

    def add_edge(source: str, target: str, etype: str):
        if source == target:
            return
        key = (source, target, etype)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append(Edge(source, target, etype, "directed", edge_weight(etype)))

    py_index = _ModuleIndex()
    for f in scan_result.files:
        if f.language == "python":
            py_index.add(f.path)

    # Precompute every file's node id up front so imports resolve to ids in a single pass.
    file_id_by_path: dict[str, str] = {
        f.path: file_node_id(node_type_for(f), f.path) for f in scan_result.files
    }
    import_index = imp.build_index(scan_result.files, root)
    seen_sym_ids: set[str] = set()

    def add_symbol(kind: str, name: str, parent_id: str, file_path: str, language: str,
                   doc: str = "", method: bool = False) -> str:
        base = f"{kind}:{file_path}:{name}"
        sid, k = base, 2
        while sid in seen_sym_ids:  # disambiguate overloads / repeated names
            sid = f"{base}#{k}"
            k += 1
        seen_sym_ids.add(sid)
        nodes.append(Node(
            id=sid, type=kind, name=name, filePath=file_path,
            summary=doc or f"{'Method' if method else kind.capitalize()} {name} in {file_path}",
            tags=[kind, language] + (["method"] if method else []), complexity="simple",
        ))
        add_edge(parent_id, sid, "contains")
        return sid

    def add_symbols(symbols, parent_id: str, file_path: str, language: str) -> int:
        for sym in symbols:
            kind = sym["kind"]
            cid = add_symbol(kind, sym["name"], parent_id, file_path, language, sym.get("doc", ""))
            if kind == "class":
                for meth in sym.get("methods", []):
                    add_symbol("function", f"{sym['name']}.{meth}", cid, file_path, language,
                               f"Method of {sym['name']}", method=True)
        return len(symbols)

    ts_supported = ts.supported_languages()

    def link_imports(src_id: str, targets) -> None:
        for tgt_rel in targets:
            tgt_id = file_id_by_path.get(tgt_rel)
            if tgt_id:
                add_edge(src_id, tgt_id, "imports")

    for f in scan_result.files:
        ntype = node_type_for(f)
        nid = file_id_by_path[f.path]
        abs_path = root / f.path
        text = _read_text(abs_path) if f.sizeLines and f.sizeLines < 20_000 else ""

        summary = ""
        symbol_count = 0
        top_dir = f.path.split("/")[0] if "/" in f.path else ""
        tags = [t for t in (f.language, f.category, top_dir) if t]

        if f.language == "python" and text:
            module_doc, symbols, py_imports = _python_extract(text)
            summary = module_doc
            symbol_count = add_symbols(symbols, nid, f.path, f.language)
            targets = []
            for pi in py_imports:
                targets.extend(_resolve_py_import(pi, f.path, py_index))
            link_imports(nid, targets)
        else:
            if text and f.language in ts_supported:
                ts_syms = ts.extract_symbols(f.language, f.path, text)
                if ts_syms:
                    symbol_count = add_symbols(ts_syms, nid, f.path, f.language)
            if text:
                link_imports(nid, imp.resolve(f.language, f.path, text, import_index))

        if not summary:
            summary = _first_doc_comment(text, f.language) if text else ""
        if not summary:
            summary = _fallback_summary(f)

        nodes.append(Node(
            id=nid, type=ntype, name=f.path.split("/")[-1], filePath=f.path,
            summary=summary, tags=tags, complexity=_complexity(f.sizeLines, symbol_count),
        ))

    return nodes, edges
