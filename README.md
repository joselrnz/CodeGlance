<p align="center">
  <img src="brand/codeglance-banner.svg" alt="codeglance" width="760">
</p>
<p align="center">
  <a href="https://pypi.org/project/codeglance/"><img alt="PyPI package v0.0.1" src="https://img.shields.io/badge/pypi-v0.0.1-0ea5e9"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-0ea5e9">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-22d3ee">
  <img alt="Python based" src="https://img.shields.io/badge/runtime-Python--based-1f6feb">
  <img alt="Offline HTML" src="https://img.shields.io/badge/output-offline%20HTML-155e75">
</p>

`codeglance` turns a codebase into files you can actually inspect:

- an interactive HTML graph for humans
- a readable wiki page for humans
- a compact Markdown map for AI agents
- a low-token agent handoff that can be refreshed after edits
- a local output browser so you can view generated HTMLs from your laptop or phone

No Node. No npm. No hosted service. Install it with pip, point it at a folder, open the output.

```bash
pip install codeglance
codeglance /path/to/project
```

## Quick Start

Generate the main graph:

```bash
codeglance init
codeglance .
```

That writes:

```text
.codeglance/knowledge-graph.json
.codeglance/knowledge-graph.html
.codeglance/meta.json
```

Generate the wiki:

```bash
codeglance wiki . -o .codeglance/wiki.html
```

Generate AI context:

```bash
codeglance context . --mode full -o .codeglance/context.md
codeglance context . --mode agent -o AGENTS.md
```

Explain one file or symbol:

```bash
codeglance explain src/app.py
codeglance explain UserService -o .codeglance/explain.md
```

Generate review workflow docs:

```bash
codeglance onboard . -o .codeglance/onboarding.md
codeglance impact . -o .codeglance/impact.md
```

Browse every generated output locally:

```bash
codeglance init
codeglance generate . --out .codeglance/outputs
codeglance generate . --out .codeglance/outputs --profile all
codeglance serve . --host 0.0.0.0
codeglance serve . --host 0.0.0.0 --watch
```

Then open the printed URL on your desktop or phone on the same Wi-Fi.

`codeglance init` creates:

- `.codeglance/config.json`: default output/profile commands
- `.codeglance/.codeglanceignore`: extra scan ignores
- `AGENTS.md`: low-token agent reading protocol
- `.agents/skills/codeglance/SKILL.md`: local agent skill
- `.claude/skills/codeglance/SKILL.md`: Claude-compatible skill
- `.claude/commands/codeglance.md`: local `/codeglance` command prompt

Use `--no-agents` for config only, or `--force` to overwrite existing files.
Use `codeglance init --generate` when you want setup and the first output bundle in one command.

## Project Structure

CodeGlance is a Python package with a thin CLI over reusable SDK services.

```text
codeglance/
├── brand/                  # banner, logo, badge, favicon, social-card SVGs
├── demo/                   # generated demo HTML/Markdown outputs
├── docs/                   # structure, agent-context, and project notes
├── examples/               # sample repos used for validation and demos
├── src/codeglance/
│   ├── analyze/            # scanners, language registry, symbol extraction, layers, tours
│   ├── cli/                # console entrypoint and argparse parser
│   ├── commands/           # CLI command handlers
│   ├── models/             # public model facade: KnowledgeGraph, Node, Edge, Layer
│   ├── output/             # generated output bundles, llms.txt, TOON, schema, index
│   ├── render/             # interactive HTML, static HTML, wiki, and agent context renderers
│   ├── services/           # reusable workflows used by API and CLI
│   ├── api.py              # public Python SDK surface
│   ├── graph.py            # analysis orchestration
│   ├── schema.py           # canonical graph dataclasses and JSON schema behavior
│   ├── scan.py             # file discovery, language/framework detection
│   └── serve.py            # local output browser
├── tests/                  # smoke tests and fixture repos
├── pyproject.toml
└── README.md
```

Public Python usage:

```python
from codeglance.api import analyze_project, generate_bundle, render_html
from codeglance.models import KnowledgeGraph

graph: KnowledgeGraph = analyze_project(".")
html = render_html(graph, ".")
generate_bundle(".", ".codeglance/outputs")
```

The older `codeglance.schema` imports still work, but new integrations should prefer
`codeglance.models` and `codeglance.api`.

## Outputs

### Interactive Graph

The default HTML graph is a self-contained canvas app. It shows files, functions, classes,
dependencies, layers, domains, documentation links, and changed files from the last analysis.

Useful controls are built in:

- overview cards for architecture layers
- structural, domain, and knowledge views
- search, filters, focus mode, path finding, and guided tour
- file tree with source snippets and highlighted symbols
- export to PNG, SVG, or JSON
- themes and keyboard shortcuts
- mobile-friendly bottom-sheet panels, safe-area layout, one-finger pan/tap, and two-finger pinch zoom

Open it directly as a file, or serve it through `codeglance serve`.

### Wiki

The wiki output is a readable HTML document:

- getting started
- project overview
- architecture layers
- inferred domains
- per-file reference
- suggested reading order

Use it when you want a cleaner document instead of a graph.

### Agent Context

Agents should not need to read the whole repo before every task. `codeglance context` gives them
a smaller entry point.

Full mode:

```bash
codeglance context . --mode full
```

Includes the read-first files, file-to-file dependencies, summaries, symbols, imports, and used-by
relationships.

Agent mode:

```bash
codeglance context . --mode agent -o AGENTS.md
```

Keeps the handoff small: snapshot, read-first files, layers, dependency hotspots, changed files,
context budget, reading protocol, and refresh rules.

### Local Output Browser

`generate` writes a compact output folder from one analysis pass:

```bash
codeglance generate . --out .codeglance/outputs
```

The default `minimal` profile contains:

| File | Audience | Purpose |
| --- | --- | --- |
| `index.html` | human | Clickable output-folder landing page. |
| `llms.txt` | agent | Small read-first entrypoint with artifact order and usage rules. |
| `glance.html` | human | Interactive visual codebase map. |
| `agent.md` | agent | Compact, low-token repo handoff. |
| `llm-context.schema.json` | agent/tool | Machine-readable contract for all generated artifacts. |
| `knowledge-graph.toon` | agent | Compact graph context for prompts. |
| `knowledge-graph.json` | tool | Canonical structured graph for parsing and re-rendering. |
| `meta.json` | human/tool | Analysis metadata: version, commit, analyzed file count. |

Use profiles when you want a different bundle:

```bash
codeglance generate . --profile minimal  # LLM entrypoint + Glance visual + compact agent context + JSON metadata
codeglance generate . --profile human    # Glance visual + wiki + onboarding/impact docs + JSON metadata
codeglance generate . --profile agent    # compact agent context + onboarding/impact docs + graph data
codeglance generate . --profile all      # every generated artifact
```

The `all` profile adds:

- `graph.static.html`
- `wiki.html`
- `context.md`
- `onboarding.md`
- `impact.md`

LLM-specific generated files:

- `llms.txt`: tiny entrypoint with read order and artifact pointers
- `onboarding.md`: first-day walkthrough with read-first files, layers, tour order, and agent workflow
- `impact.md`: changed-file impact report with likely ripple areas and review checklist
- `llm-context.schema.json`: structured contract for agents and tools, including artifact tiers,
  graph fields, node types, edge types, and output profiles
- `knowledge-graph.toon`: compact structured graph for LLM prompt context, with repeated JSON
  field names collapsed into TOON-style tables
- `knowledge-graph.json`: canonical graph for parsers, tooling, re-rendering, and compatibility

`serve` hosts an output folder and generates a simple index page for artifacts:

```bash
codeglance serve .
codeglance serve . --dir .codeglance
codeglance serve .codeglance/outputs --host 0.0.0.0
codeglance serve . --host 0.0.0.0 --watch --profile all
codeglance serve demo --host 0.0.0.0
```

It lists HTML, Markdown, JSON, TXT, and SVG files. This is the easiest way to check all generated
views from a phone without pushing or deploying anything.

Use `--watch` when you want a live local workflow. Codeglance regenerates the selected output
profile when project files change, and `glance.html` shows a refresh notice when served output is
newer than the page you are viewing. The same HTML still opens directly from disk without a server.

For a guided walkthrough of `glance.html`, the generated files, mobile behavior, screenshots, and the
human-in-the-loop review flow, see [`docs/GLANCE_WALKTHROUGH.md`](docs/GLANCE_WALKTHROUGH.md).

## How It Stays Fast

Codeglance stores fingerprints in `.codeglance/fingerprints.json`. Re-running analysis compares
file hashes, keeps prior summaries for unchanged files, and only marks changed files for the diff
overlay.

```bash
codeglance .
codeglance wiki .
codeglance context . --mode agent -o AGENTS.md
```

Use `--full` when you want to rebuild from scratch.

## Analysis

The default path is deterministic and offline:

- Python uses the standard library `ast` module.
- Other languages use bundled tree-sitter grammars.
- Imports become dependency edges where local resolution is supported.
- Layers are inferred from the graph structure.
- Tours and summaries have deterministic fallbacks.

Optional LLM enrichment is available:

```bash
ANTHROPIC_API_KEY=... codeglance . --llm
```

The package still works without an API key.

## Language Coverage

Python is first-class. Tree-sitter coverage adds broad symbol extraction across common and older
languages:

- JavaScript, TypeScript/TSX, Go, Rust, Java, Ruby, PHP, C#, C, C++, Kotlin, Swift, Scala, Lua
- Terraform/HCL resources, modules, variables, outputs, and dependency references
- VHDL, Verilog, COBOL, Fortran, Ada, Haskell, OCaml, Erlang, Elixir, Clojure, Julia, Dart,
  Solidity, PowerShell, Tcl, Common Lisp, Scheme, Racket, Gleam, shell, and more

Unsupported text files still appear as file-level nodes with summaries.

## Example Projects

The `examples/` folder has small repos you can use to test the different views:

```bash
codeglance examples/taskman
codeglance examples/microservices
codeglance examples/canvas-cli
codeglance examples/terraform-aws
codeglance examples/terraform-azure
codeglance examples/rust-cli
codeglance examples/java-service
codeglance examples/wiki
```

They cover Python apps, CLIs, microservices, AWS and Azure Terraform modules, Rust modules,
Java packages, and Markdown knowledge graphs.

## Schema

The graph is plain JSON:

```json
{
  "version": "1.0.0",
  "project": {},
  "nodes": [],
  "edges": [],
  "layers": [],
  "tour": []
}
```

You can diff it, inspect it, or render it again:

```bash
codeglance render .codeglance/knowledge-graph.json -o graph.html
codeglance render .codeglance/knowledge-graph.json --static -o graph.static.html
```

## Documentation Map

- `docs/STRUCTURE.md`: package layout, module responsibilities, and SDK/CLI boundaries
- `docs/AGENT_CONTEXT.md`: agent reading protocol and generated context strategy
- `docs/UNDERSTAND_ANYTHING_GAP_PLAN.md`: roadmap for missing Understand Anything-style capabilities while preserving static HTML and Python serving
- `docs/README.md`: documentation index and screenshot guidance
- `REFACTOR_PLAN.md`: longer-term cleanup and enhancement plan

## Current Version

Package version is static for now: `0.0.1`.

When the package version changes, update:

- `pyproject.toml`
- `src/codeglance/__init__.py`
- this README badge
- brand badge text

## Next Build Plan

The current package structure is now split into SDK, services, CLI, commands, models, output,
renderers, and analysis. The next useful pieces are:

- `codeglance review` to validate graph/output quality before sharing or pushing
- `codeglance ask` to answer repo questions from `llms.txt`, `agent.md`, TOON, and selected context
- persona modes in Glance for Overview, Developer, Reviewer, PM, and Agent audiences
- business-flow extraction for domain/process views
- richer output-folder landing pages with screenshots and project stats
- optional strict Pydantic models behind a `pydantic` extra
- JSON context mode for tools that prefer smaller structured ingestion
- changed-only context mode for fast review after edits
