"""Per-file content fingerprints for incremental re-analysis.

Stored at `.understand-anything/fingerprints.json` as {relPath: sha1}. On re-run we diff against
the previous fingerprints to decide which files changed, so unchanged files keep their (possibly
LLM-enriched) summaries and `--llm` only spends tokens on what actually changed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FP_FILE = "fingerprints.json"


def compute(files, root: str | Path) -> dict[str, str]:
    root = Path(root)
    out: dict[str, str] = {}
    for f in files:
        try:
            out[f.path] = hashlib.sha1((root / f.path).read_bytes()).hexdigest()
        except OSError:
            out[f.path] = ""
    return out


def load(root: str | Path) -> dict[str, str]:
    p = Path(root) / ".understand-anything" / FP_FILE
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save(root: str | Path, fingerprints: dict[str, str]) -> None:
    p = Path(root) / ".understand-anything" / FP_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(fingerprints, ensure_ascii=False), encoding="utf-8")


def diff(old: dict[str, str], new: dict[str, str]) -> tuple[set[str], set[str], set[str]]:
    """Return (changed, added, removed) relative paths."""
    old_keys, new_keys = set(old), set(new)
    added = new_keys - old_keys
    removed = old_keys - new_keys
    changed = {k for k in (old_keys & new_keys) if old.get(k) != new.get(k)}
    return changed, added, removed
