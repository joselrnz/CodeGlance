---
name: codebase-map
description: >
  Quickly understand an unfamiliar codebase by generating a compact dependency + summary map
  instead of reading every file. Use at the START of any task that needs repo-wide understanding
  ("how does this project work", "where is X handled", "what depends on Y", onboarding, planning a
  refactor). Runs `codeglance context`, which prints the read-first hub files, a file→file
  dependency list, and a one-line summary + defined symbols + imports/used-by per file.
---

# Codebase map (codeglance context)

When you need to understand a repository fast — before searching or reading source — generate its
map and read that first. It is dependency-first and token-cheap (a small fraction of the repo).

## Run it

```bash
codeglance context <path>          # prints the Markdown map to stdout
codeglance context . -o map.md     # or write it to a file
```

If `codeglance` isn't installed:

```bash
pip install codeglance              # published package
# or, inside this repo:  pip install -e .
```

First run analyzes the project (tree-sitter, no network) and caches a graph under `.codeglance/`;
later runs are instant. Add `--full` to force a fresh analysis.

## How to use the output

The map has three parts — read them in order:

1. **Read first (most-connected files)** — the hubs / likely entry points. Start here.
2. **Dependency map** — `file → depends on …`. Trace how data and control flow.
3. **Files** — per file: a one-line summary, the symbols it `defines`, and `imports` / `used-by`.

From this you know *what each file does* and *how everything wires together* without opening source.
Only open the actual files the task requires (usually the hubs plus the few the map points you to).

## Other codeglance outputs (when a visual / doc is wanted)

- `codeglance <path>` — interactive HTML knowledge graph (open in a browser, offline).
- `codeglance wiki <path>` — a readable docs/wiki HTML page (setup, architecture, reference).
