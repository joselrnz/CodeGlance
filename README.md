# understand-anything-py

A **pure-Python**, `pip`-installable port of [Understand-Anything](https://github.com/Lum1104/Understand-Anything).

Point it at a codebase, and it produces an interactive **knowledge graph** of files, functions,
classes and their relationships — rendered to a **single self-contained HTML file** you just
double-click to open. No Node, no npm, no Vite, no server, no hosting.

```bash
pip install understand-anything-py

# Analyze a project -> writes .understand-anything/knowledge-graph.json -> opens an HTML graph
understand /path/to/project

# Re-render an existing graph to HTML
understand render /path/to/project/.understand-anything/knowledge-graph.json -o graph.html

# Zero-JavaScript static image instead (inline SVG, no interactivity)
understand render knowledge-graph.json --static -o graph.svg.html
```

## How it differs from the original

| | Original (Understand-Anything) | This port |
|---|---|---|
| Runtime | TypeScript / Node / pnpm / Vite | Python only |
| Viewer | React dashboard served by a Vite **dev server** (token-gated) | A **single HTML file** you open directly |
| Intelligence | Claude subagents (needs a Claude Code session) | Deterministic by default; optional `--llm` enrichment |
| Data format | `knowledge-graph.json` | **Identical** `knowledge-graph.json` schema |

## Analysis modes (hybrid)

- **Default (deterministic, offline, free):** tree-sitter / Python `ast` structural extraction —
  files, functions, classes, imports, Louvain-detected layers, a heuristic tour.
- **`--llm` (optional):** enrich node summaries, layer names and the guided tour via an LLM API
  (set `ANTHROPIC_API_KEY`). Everything still works without it.

## Visual modes

- **Interactive (default):** a self-contained HTML canvas app modeled on the original dashboard —
  **labeled node cards** colored **by type** (with a type badge), **layer container boxes**,
  **directional edge arrows**, a **project-overview** panel, and a rich **node panel** when you
  click a card: the **signature**, the **docstring / leading doc-comment** pulled from the code,
  tags, complexity, typed connections, and the **source code with line numbers** (the node's own
  line range highlighted). Plus pan/zoom, search, layer + node-type legends, a minimap, and a
  guided tour. Fully offline.
- **`--static`:** a zero-JavaScript inline-SVG rendering (cards + containers + arrows). A picture,
  but truly no JS.

## Knowledge graph schema

`{ version, project, nodes[], edges[], layers[], tour[] }` — byte-for-byte compatible with the
original, so graphs produced by either tool render in the other.

## Language coverage

Deep symbol extraction (functions, classes, methods → `contains` edges):

- **Python** — always on (stdlib `ast`, no extra needed).
- **~50 more via the `treesitter` extra** (`pip install understand-anything-py[treesitter]`):
  - *Tuned* (precise method/impl handling): JavaScript, TypeScript/TSX, Go, Rust, Java, Ruby,
    PHP, C#, C, C++, Kotlin, Swift, Scala, Lua.
  - *Generic node-kind classifier* (works across any grammar): VHDL, Verilog, COBOL, Fortran,
    Ada, Pascal, Haskell, OCaml, Erlang, Elixir, Clojure, Elm, Julia, R, Perl, Groovy, Dart,
    Zig, Nim, Crystal, D, Solidity, Objective-C, MATLAB, PowerShell, Tcl, Common Lisp, Scheme,
    Racket, Gleam, Odin, GLSL/HLSL/WGSL, shell — and more.
- **Any other text file** — file-level node with a heuristic summary; import edges where supported.

Yes, including VHDL and COBOL. The generic classifier matches function/type node kinds by name
across arbitrary tree-sitter grammars, so adding a language is usually just a file-extension entry.
Without the extra, non-Python files still appear as file nodes — you just don't get per-symbol
detail.

**Import-graph edges** resolve intra-project dependencies for: Python (`ast`), JS/TS (relative),
Go (go.mod module + packages), Rust (`mod` / `use crate::`), Java (dotted path), C/C++
(`#include "..."`), Ruby (`require_relative`), and PHP (`require`/`include`).

## Incremental updates

Re-running `understand .` is cheap: per-file content fingerprints (`.understand-anything/fingerprints.json`)
detect what changed. Unchanged files keep their existing summaries (so prior `--llm` enrichment is
preserved for free), and `--llm` only re-summarizes changed/added files. Pass `--full` to force a
complete rebuild.
