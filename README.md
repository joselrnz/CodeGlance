# ScopingLang

A **pure-Python**, `pip`-installable port of [Understand-Anything](https://github.com/Lum1104/Understand-Anything).

Point it at a codebase, and it produces an interactive **knowledge graph** of files, functions,
classes and their relationships — rendered to a **single self-contained HTML file** you just
double-click to open. No Node, no npm, no Vite, no server, no hosting.

```bash
pip install scopinglang

# Analyze a project -> writes .scopinglang/knowledge-graph.json -> opens an HTML graph
scopinglang /path/to/project

# Re-render an existing graph to HTML
scopinglang render /path/to/project/.scopinglang/knowledge-graph.json -o graph.html

# Zero-JavaScript static image instead (inline SVG, no interactivity)
scopinglang render knowledge-graph.json --static -o graph.svg.html
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
  tags, complexity, typed connections, and the **syntax-highlighted source code with line numbers**
  (the node's own line range highlighted). Plus pan/zoom, search, layer + node-type legends, a
  minimap, **directional curved edges with type labels**, **animated _marching-ants_ flow edges**
  (dashes glide from source → target; toggle with the **≈ Flow** button or `a`), a **path finder**
  (shortest path between any two nodes), **export to PNG / SVG / JSON**, **persona tabs**
  (Deep Dive / Overview / Learn), **zoom controls**, a guided tour, and keyboard shortcuts
  (`/ f p e a d t ?`). Like the original, it
  opens on an **overview of layer cards** (name, description, complexity, file count) and you
  **click a layer to drill into its files**, with a breadcrumb back to the overview. The header
  mirrors the original: **persona tabs**, a **Files/+Classes/`fn`** detail toggle, **category
  filter buttons** (Code/Config/Docs/Infra/Data/Domain/Knowledge), a **Domain / Structural** view
  toggle, and **inline layer chips**;
  the sidebar has **Info / Files tabs** — a collapsible file explorer with **VS Code-style
  file-type icons** ([vscode-icons](https://github.com/vscode-icons/vscode-icons), MIT, inlined)
  plus the **guided-tour steps**. A **theme picker** (**Dark Ocean** by default, plus Dark Gold /
  Forest / Rose / Light Minimal, 8 accent colors, Serif/Sans/Mono heading font) recolors
  everything — all base colors are CSS variables, so you can also just open the `.html` and tweak
  them. Fully offline.
- **`--static`:** a zero-JavaScript inline-SVG rendering (cards + containers + arrows). A picture,
  but truly no JS.

### Domain view

Toggle **Domain** in the header (or press `d`) for a higher-level **domain map**: each top-level
package / service directory becomes a **domain card** (its classes/types listed as **entities**),
and the imports/calls between domains become **animated flow edges**. It's inferred deterministically
from the project structure — no LLM required — so a microservices repo shows each service and how
they depend on one another. Try `scopinglang examples/microservices` then click **Domain**.

## Knowledge graph schema

`{ version, project, nodes[], edges[], layers[], tour[] }` — byte-for-byte compatible with the
original, so graphs produced by either tool render in the other.

## Language coverage

Deep symbol extraction (functions, classes, methods, **variables & constants** → `contains` edges)
— **all ~50 work out of the box from a single `pip install`** (tree-sitter ships as a normal pip
wheel; no Node, no build):

- **Python** — stdlib `ast`: functions, classes, methods, **module-level variables/constants, and
  class attributes** (`UPPER_CASE` → constant, otherwise variable).
- **~50 more** via bundled tree-sitter grammars:
  - *Tuned* (precise method/impl handling): JavaScript, TypeScript/TSX, Go, Rust, Java, Ruby,
    PHP, C#, C, C++, Kotlin, Swift, Scala, Lua. Top-level **`var` / `const` / `let` / `static`
    declarations** are captured as variable/constant nodes for Python, Go, JS/TS and Rust
    (function-local variables are intentionally skipped to keep the graph readable).
  - *Terraform/HCL* — resource / module / variable / output blocks, **plus `depends_on` edges**
    between blocks that reference each other (resource → security group → module → variable).
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

Re-running `scopinglang .` is cheap: per-file content fingerprints (`.scopinglang/fingerprints.json`)
detect what changed. Unchanged files keep their existing summaries (so prior `--llm` enrichment is
preserved for free), and `--llm` only re-summarizes changed/added files. Pass `--full` to force a
complete rebuild.
