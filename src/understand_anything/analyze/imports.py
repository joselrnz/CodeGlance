"""Cross-language import / dependency edge resolution.

Best-effort resolution of intra-project imports to concrete files, per language:
  - Python   : handled separately in structural.py via the stdlib `ast` module index
  - JS/TS     : relative specifiers (./foo, ../bar)
  - Go        : go.mod module path + package directories
  - Rust      : `mod name;` siblings and `use crate::a::b` paths
  - Java      : dotted import resolved by path suffix (com/example/Foo.java)
  - C / C++   : #include "relative/header.h"
  - Ruby      : require_relative './x'
  - PHP       : require/include 'relative/path.php'

External / third-party imports are intentionally skipped (only project-internal edges).
"""

from __future__ import annotations

import re
from pathlib import Path

_JS_EXTS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte")
_C_EXTS = (".h", ".hpp", ".hh", ".hxx", ".c", ".cc", ".cpp", ".cxx")

_RE = {
    "js": re.compile(
        r"""import\s[^'"]*?from\s*['"]([^'"]+)['"]"""
        r"""|require\(\s*['"]([^'"]+)['"]\s*\)"""
        r"""|import\(\s*['"]([^'"]+)['"]\s*\)""",
    ),
    "go_single": re.compile(r'import\s+(?:[\w.]+\s+)?"([^"]+)"'),
    "go_block": re.compile(r"import\s*\((.*?)\)", re.DOTALL),
    "go_line": re.compile(r'(?:[\w.]+\s+)?"([^"]+)"'),
    "rust_mod": re.compile(r"\bmod\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;"),
    "rust_use": re.compile(r"\buse\s+crate::([a-zA-Z0-9_:]+)"),
    "java": re.compile(r"import\s+(?:static\s+)?([\w.]+)\s*;"),
    "c_inc": re.compile(r'#\s*include\s+"([^"]+)"'),
    "ruby": re.compile(r"""require_relative\s+['"]([^'"]+)['"]"""),
    "php": re.compile(r"""(?:require|include)(?:_once)?\s*\(?\s*['"]([^'"]+)['"]"""),
}


class ImportIndex:
    def __init__(self, all_files: set[str]):
        self.all_files = all_files
        self.go_module: str = ""
        self.go_dirs: dict[str, list[str]] = {}        # import path -> .go files
        self.rust_crate_roots: list[str] = []          # dirs containing lib.rs/main.rs
        self.java_by_suffix: dict[str, str] = {}       # "a/b/C.java" -> rel path


def build_index(files, root: Path) -> ImportIndex:
    all_files = {f.path for f in files}
    idx = ImportIndex(all_files)

    # Go module path from go.mod
    gomod = root / "go.mod"
    if gomod.is_file():
        m = re.search(r"^\s*module\s+(\S+)", gomod.read_text(encoding="utf-8", errors="ignore"), re.M)
        if m:
            idx.go_module = m.group(1).strip()
    # Go package directories -> files
    if idx.go_module:
        for f in files:
            if f.language == "go":
                d = str(Path(f.path).parent.as_posix())
                pkg = idx.go_module if d == "." else f"{idx.go_module}/{d}"
                idx.go_dirs.setdefault(pkg, []).append(f.path)

    # Rust crate roots
    for f in files:
        if f.language == "rust" and Path(f.path).name in ("lib.rs", "main.rs"):
            idx.rust_crate_roots.append(str(Path(f.path).parent.as_posix()))

    # Java suffix index
    for f in files:
        if f.language == "java":
            idx.java_by_suffix[f.path] = f.path  # match by endswith later

    return idx


def resolve(language: str, rel_path: str, text: str, idx: ImportIndex) -> list[str]:
    """Return a list of project-internal target file rel-paths imported by this file."""
    if language in ("javascript", "typescript", "vue", "svelte"):
        return _resolve_js(text, rel_path, idx.all_files)
    if language == "go":
        return _resolve_go(text, idx)
    if language == "rust":
        return _resolve_rust(text, rel_path, idx)
    if language == "java":
        return _resolve_java(text, idx)
    if language in ("c", "cpp"):
        return _resolve_relative(_findall(_RE["c_inc"], text), rel_path, idx.all_files, _C_EXTS,
                                 require_dot=False)
    if language == "ruby":
        return _resolve_relative(_findall(_RE["ruby"], text), rel_path, idx.all_files, (".rb",),
                                 require_dot=False)
    if language == "php":
        return _resolve_relative(_findall(_RE["php"], text), rel_path, idx.all_files, (".php",),
                                 require_dot=False)
    return []


def _findall(rx: re.Pattern, text: str) -> list[str]:
    return [m if isinstance(m, str) else next((g for g in m if g), "") for m in rx.findall(text)]


def _resolve_js(text: str, rel_path: str, all_files: set[str]) -> list[str]:
    specs = []
    for m in _RE["js"].finditer(text):
        spec = m.group(1) or m.group(2) or m.group(3)
        if spec:
            specs.append(spec)
    return _resolve_relative(specs, rel_path, all_files, _JS_EXTS, require_dot=True)


def _resolve_go(text: str, idx: ImportIndex) -> list[str]:
    if not idx.go_module:
        return []
    specs: list[str] = []
    for block in _RE["go_block"].findall(text):
        specs += _RE["go_line"].findall(block)
    specs += _RE["go_single"].findall(text)
    out: list[str] = []
    for spec in specs:
        out.extend(idx.go_dirs.get(spec, []))
    return out


def _resolve_rust(text: str, rel_path: str, idx: ImportIndex) -> list[str]:
    out: list[str] = []
    base = Path(rel_path).parent
    # `mod name;` -> sibling name.rs or name/mod.rs
    for name in _RE["rust_mod"].findall(text):
        for cand in (f"{base/name}.rs", f"{base/name}/mod.rs"):
            cand = _norm(cand)
            if cand in idx.all_files:
                out.append(cand)
                break
    # `use crate::a::b::c` -> root/a/b/c.rs or root/a/b.rs (drop trailing item)
    roots = idx.rust_crate_roots or [str(base.as_posix())]
    for path in _RE["rust_use"].findall(text):
        segs = [s for s in path.split("::") if s]
        for root in roots:
            found = False
            for cut in range(len(segs), 0, -1):
                sub = "/".join(segs[:cut])
                for cand in (f"{root}/{sub}.rs", f"{root}/{sub}/mod.rs"):
                    cand = _norm(cand)
                    if cand in idx.all_files:
                        out.append(cand)
                        found = True
                        break
                if found:
                    break
            if found:
                break
    return out


def _resolve_java(text: str, idx: ImportIndex) -> list[str]:
    out: list[str] = []
    for dotted in _RE["java"].findall(text):
        suffix = dotted.replace(".", "/") + ".java"
        for path in idx.all_files:
            if path.endswith(suffix):
                out.append(path)
                break
    return out


def _resolve_relative(specs, rel_path: str, all_files: set[str], exts, require_dot: bool = True) -> list[str]:
    out: list[str] = []
    base = Path(rel_path).parent
    for spec in specs:
        if require_dot and not spec.startswith("."):
            continue  # bare specifier = external library (npm, etc.)
        target = _norm((base / spec).as_posix())
        candidates = [target] + [target + e for e in exts] + [f"{target}/index{e}" for e in exts]
        hit = next((c for c in candidates if c in all_files), None)
        if hit is None and not require_dot:
            # C/C++/Ruby/PHP includes may be written relative to a root, not the file's dir —
            # fall back to a project-wide path-suffix match (e.g. include "net/http.h").
            spec_norm = _norm(spec)
            extra = [spec_norm] + [spec_norm + e for e in exts]
            hit = next((c for c in extra if c in all_files), None)
            if hit is None:
                hit = next((p for p in all_files if p.endswith("/" + spec_norm) or p == spec_norm), None)
        if hit:
            out.append(hit)
    return out


def _norm(p: str) -> str:
    parts: list[str] = []
    for seg in p.replace("\\", "/").split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
        else:
            parts.append(seg)
    return "/".join(parts)
