"""Lightweight, dependency-free ignore matching (gitignore-ish).

Combines a built-in default set with patterns read from the project's `.gitignore` and
`.understand-anything/.understandignore`. Good enough for excluding the usual noise; not a full
gitignore implementation (no negation-precedence edge cases), but covers the common patterns.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

# Directory names excluded wherever they appear in the tree.
DEFAULT_IGNORE_DIRS = {
    "node_modules", ".git", ".hg", ".svn", "vendor", "venv", ".venv", "env",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
    "out", "coverage", ".next", ".nuxt", ".cache", ".turbo", "target", "obj", "bin",
    ".idea", ".vscode", ".gradle", ".terraform", ".understand-anything", "site-packages",
    ".tox", ".eggs", "__snapshots__",
}

# Filename glob patterns excluded wherever they appear.
DEFAULT_IGNORE_GLOBS = {
    "*.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "*.min.js", "*.min.css", "*.map", "*.generated.*", "*.log",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico", "*.webp", "*.bmp",
    "*.woff", "*.woff2", "*.ttf", "*.eot", "*.otf",
    "*.mp3", "*.mp4", "*.mov", "*.avi", "*.wav", "*.pdf",
    "*.zip", "*.tar", "*.gz", "*.tgz", "*.rar", "*.7z", "*.jar", "*.war",
    "*.pyc", "*.pyo", "*.class", "*.o", "*.so", "*.dll", "*.dylib", "*.exe",
    "*.wasm", "*.bin", "*.dat", "*.db", "*.sqlite", "*.sqlite3",
}


class IgnoreMatcher:
    def __init__(self, dirs: set[str], globs: set[str], path_patterns: list[str]):
        self._dirs = dirs
        self._globs = globs
        self._path_patterns = path_patterns

    def is_ignored_dir(self, name: str) -> bool:
        return name in self._dirs

    def is_ignored(self, rel_path: str) -> bool:
        rel_path = rel_path.replace("\\", "/")
        parts = rel_path.split("/")
        name = parts[-1]
        if any(p in self._dirs for p in parts[:-1]):
            return True
        if any(fnmatch.fnmatch(name, g) for g in self._globs):
            return True
        for pat in self._path_patterns:
            if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(name, pat):
                return True
            # Directory-style pattern "foo/" or "foo" matching a path segment.
            seg = pat.rstrip("/")
            if seg and seg in parts:
                return True
        return False


def _read_patterns(path: Path) -> list[str]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        out.append(line.lstrip("/"))
    return out


def build_matcher(root: Path) -> IgnoreMatcher:
    patterns: list[str] = []
    patterns += _read_patterns(root / ".gitignore")
    patterns += _read_patterns(root / ".understand-anything" / ".understandignore")
    return IgnoreMatcher(set(DEFAULT_IGNORE_DIRS), set(DEFAULT_IGNORE_GLOBS), patterns)
