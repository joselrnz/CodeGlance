<p align="center">
  <img src="brand/codeglance-banner.svg" alt="codeglance" width="920">
</p>
<p align="center">
  <a href="https://pypi.org/project/codeglance/"><img alt="PyPI package v0.0.1" src="https://img.shields.io/badge/pypi-v0.0.1-0ea5e9"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-0ea5e9">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-22d3ee">
  <img alt="Python based" src="https://img.shields.io/badge/runtime-Python--based-1f6feb">
  <img alt="Offline HTML" src="https://img.shields.io/badge/output-offline%20HTML-155e75">
</p>

<p align="center">
  <img src="brand/codeglance-local-adapters.svg" alt="Codeglance scans once, builds an evidence map, and writes local adapter files for AI coding tools" width="860">
</p>

`codeglance` turns a repository into a visual map, a readable wiki, and compact AI context files.
It runs locally, writes deterministic artifacts, and gives humans and coding agents the same
evidence before anyone starts editing source.

**Map first. Source last.**

```bash
pip install codeglance
codeglance init
codeglance generate . --out .codeglance/outputs --profile all
codeglance serve . --dir .codeglance/outputs --watch
```

No Node. No npm. No hosted service. Pure Python in, static files out.

## Why

New repo, old repo, inherited repo, huge repo: the failure mode is usually the same. You open files
too early, miss the dependency shape, and hand an AI agent a pile of source with no reading order.

Codeglance gives you a repo memory layer:

| Need | Codeglance output |
| --- | --- |
| See the system shape | Interactive `glance.html` graph with layers, domains, dependencies, search, focus, paths, and export. |
| Read the project like docs | Generated `wiki.html` with overview, architecture, domains, file reference, and reading order. |
| Give agents compact context | `llms.txt`, `agent.md`, and `knowledge-graph.toon` for low-token handoffs. |
| Plan a change | `impact.md`, `review.md`, changed-file overlays, and dependency hotspots. |
| Browse locally | `codeglance serve` opens every generated artifact from your laptop or phone. |
| Bring tools along | Local guidance files for agent/editor workflows. No network install or hosted runtime required. |

## How It Works

<p align="center">
  <img src="brand/codeglance-workflow.svg" alt="Codeglance workflow from repository scan to evidence map and generated outputs" width="860">
</p>

## Hippocampus Context

<p align="center">
  <img src="brand/codeglance-hippocampus.svg" alt="Codeglance hippocampus context memory system with short-term memory, long-term memory, indexing, and recycle lanes" width="860">
</p>

`codeglance hippocampus` turns the graph into a memory budget for long agent sessions. It keeps
changed files and task facts in short-term memory, promotes reusable architecture into long-term
memory, and moves low-signal files into a recycle lane until the graph pulls them back.

| Lane | What it saves |
| --- | --- |
| Short-term | The few files and facts that must stay in the prompt right now. |
| Working set | One-hop dependencies that explain the task without reading the whole repo. |
| Long-term | Stable architecture facts that can be reused across sessions. |
| Recycle lane | Low-signal context kept out of the prompt until evidence cites it again. |

## Quick Start

Generate the default graph:

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

Generate the complete output bundle:

```bash
codeglance generate . --out .codeglance/outputs --profile all
codeglance serve . --dir .codeglance/outputs --host 0.0.0.0 --watch
```

Open the printed URL on your desktop or phone on the same Wi-Fi. `--watch` regenerates outputs when
files change and quietly marks the `glance.html` Refresh button when newer output is available.

## Command Map

| Command | Use it when you want to |
| --- | --- |
| `codeglance .` | Analyze a project and write the primary interactive graph. |
| `codeglance wiki . -o .codeglance/wiki.html` | Generate a readable architecture/wiki document. |
| `codeglance context . --mode agent -o AGENTS.md` | Create a small agent handoff file. |
| `codeglance context . --mode full -o .codeglance/context.md` | Create fuller repo context with dependencies and symbols. |
| `codeglance explain src/app.py` | Explain one file or symbol. |
| `codeglance ask "Where should I start?" .` | Ask a repo question and get cited graph evidence. |
| `codeglance processes .` | Generate a domain/process map from the analyzed graph. |
| `codeglance hippocampus .` | Generate a context memory budget with short-term, working, long-term, and recycle lanes. |
| `codeglance onboard .` | Generate a first-day walkthrough. |
| `codeglance impact .` | Build a changed-file impact report. |
| `codeglance review .` | Check graph/output quality before sharing. |
| `codeglance generate . --profile all` | Produce the full local output folder from one analysis pass. |
| `codeglance serve . --watch` | Browse outputs locally and refresh as files change. |

## Output Profiles

| Profile | Best for | Includes |
| --- | --- | --- |
| `minimal` | Fast default handoff | `index.html`, `llms.txt`, `glance.html`, `agent.md`, schema, TOON, graph JSON, metadata. |
| `human` | People reviewing a repo | Visual graph, wiki, hippocampus context, onboarding, impact docs, review docs, metadata. |
| `agent` | Coding-agent context | Compact agent context, hippocampus memory budget, onboarding, impact docs, review docs, graph data. |
| `all` | Full local bundle | Every generated artifact. |

Default minimal outputs:

| File | Audience | Purpose |
| --- | --- | --- |
| `index.html` | human | Clickable output-folder landing page. |
| `glance.html` | human | Interactive visual codebase map. |
| `wiki.html` | human | Readable project wiki when using `human` or `all`. |
| `llms.txt` | agent | Small read-first entrypoint with artifact order and usage rules. |
| `agent.md` | agent | Compact, low-token repo handoff. |
| `knowledge-graph.toon` | agent | Compact graph context for prompts. |
| `knowledge-graph.json` | tool | Canonical structured graph for parsing and re-rendering. |
| `llm-context.schema.json` | agent/tool | Machine-readable contract for generated artifacts. |
| `meta.json` | human/tool | Version, commit, analyzed file count, and analysis metadata. |

The `all` profile also writes `graph.static.html`, `context.md`, `hippocampus.md`, `onboarding.md`,
`impact.md`, and `review.md`.

## Interactive Graph

The default HTML graph is a self-contained canvas app. It opens directly from disk or through
`codeglance serve`.

| Area | Built in |
| --- | --- |
| Navigation | Zoom, pan, focus mode, path finding, guided tour, search, filters. |
| Views | Structural graph, domain/process view, knowledge view, file tree. |
| Inspector | Source snippets, highlighted symbols, dependencies, used-by links, editor links. |
| Output | Export PNG, SVG, or JSON. |
| Devices | Desktop layout plus mobile bottom sheets, safe-area handling, tap/pan/pinch gestures. |
| Local workflow | Watch mode marks refresh quietly; no forced reloads or pop-up banners. |

## Agent And Editor Adapters

Codeglance writes repo-local guidance files that point tools to the same generated artifacts. It
does not install official plugins, publish marketplace packages, call tool APIs, or imply affiliation.

| Target | Generated guidance |
| --- | --- |
| Codex | `AGENTS.md`, `.agents/skills/codeglance/SKILL.md` |
| Claude Code | `.claude/skills/codeglance/SKILL.md`, `.claude/commands/codeglance.md` |
| Cursor | `.cursor/rules/codeglance.mdc` |
| Windsurf | `.windsurf/rules/codeglance.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` |
| Cline | `.clinerules/codeglance.md` |
| Roo Code | `.roo/rules/codeglance.md` |
| Aider | `.aider/codeglance.md` |
| Continue | `.continue/rules/codeglance.md` |
| Augment Code | `.augment-guidelines` |
| Zed | `.rules` |

```bash
codeglance init --agents default
codeglance init --agents all --dry-run
codeglance init --agents codex,cursor,copilot --marketplace-manifests
codeglance init --list-agents

codeglance agents list
codeglance agents plan . --platform codex,cursor --marketplace-manifests
codeglance agents install . --platform cursor --dry-run
codeglance agents validate . --platform codex,cursor
```

Optional marketplace manifests are local JSON descriptors under `.codeglance/marketplace/`; they are
not published or uploaded. No affiliation, endorsement, or partnership is implied with any named
third-party tool.

## Analysis

The default path is deterministic and offline:

| Capability | How |
| --- | --- |
| Python symbols/imports | Standard-library `ast`. |
| Other languages | Bundled tree-sitter grammars through `tree-sitter-language-pack`. |
| Dependencies | Import/reference resolution where local resolution is available. |
| Layers/domains | Inferred from graph structure and path conventions. |
| Summaries/tours | Deterministic fallbacks, with optional LLM enrichment. |
| Incremental runs | `.codeglance/fingerprints.json` keeps unchanged file summaries and marks changed files. |

Optional LLM enrichment:

```bash
ANTHROPIC_API_KEY=... codeglance . --llm
```

The package works without an API key.

## Language Coverage

Python is first-class. Tree-sitter coverage adds broad symbol extraction across common, systems, and
older languages:

| Family | Examples |
| --- | --- |
| Web/app | JavaScript, TypeScript/TSX, PHP, Ruby, Dart |
| Backend/systems | Go, Rust, Java, C#, C, C++, Kotlin, Swift, Scala |
| Infrastructure | Terraform/HCL resources, modules, variables, outputs, dependency references |
| Data/ops | PowerShell, shell, Lua, Julia |
| Legacy/specialized | VHDL, Verilog, COBOL, Fortran, Ada, Haskell, OCaml, Erlang, Elixir, Clojure, Common Lisp, Scheme, Racket, Gleam |

Unsupported text files still appear as file-level nodes with summaries.

## Python API

```python
from codeglance.api import analyze_project, generate_bundle, render_html
from codeglance.models import KnowledgeGraph

graph: KnowledgeGraph = analyze_project(".")
html = render_html(graph, ".")
generate_bundle(".", ".codeglance/outputs")
```

The older `codeglance.schema` imports still work, but new integrations should prefer
`codeglance.models` and `codeglance.api`.

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

## Project Structure

```text
codeglance/
├── brand/                  # banner, logo, favicon, README visuals, social-card SVGs
├── docs/                   # structure, agent-context, integrations, release notes
├── src/codeglance/
│   ├── ask/                # graph-evidence retrieval for repo questions
│   ├── analyze/            # scanners, language registry, symbol extraction, layers, tours
│   ├── cli/                # console entrypoint and argparse parser
│   ├── commands/           # CLI command handlers
│   ├── integrations/       # repo-local agent/editor guidance files
│   ├── models/             # public model facade: KnowledgeGraph, Node, Edge, Layer
│   ├── output/             # generated bundles, llms.txt, TOON, schema, index
│   ├── processes/          # domain/process map extraction
│   ├── render/             # interactive HTML, static HTML, wiki, and agent context renderers
│   ├── services/           # reusable workflows used by API and CLI
│   ├── api.py              # public Python SDK surface
│   ├── graph.py            # analysis orchestration
│   ├── schema.py           # canonical graph dataclasses and JSON schema behavior
│   ├── scan.py             # file discovery, language/framework detection
│   └── serve.py            # local output browser
├── tests/
├── pyproject.toml
└── README.md
```

## Documentation Map

| File | Purpose |
| --- | --- |
| [`docs/STRUCTURE.md`](docs/STRUCTURE.md) | Package layout, module responsibilities, SDK imports, generated output layout. |
| [`docs/AGENT_CONTEXT.md`](docs/AGENT_CONTEXT.md) | Agent reading protocol and generated context strategy. |
| [`docs/GLANCE_WALKTHROUGH.md`](docs/GLANCE_WALKTHROUGH.md) | Walkthrough for `glance.html`, generated files, mobile behavior, screenshots, and review flow. |
| [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md) | Agent/editor matrix, safety rules, generated files, validation behavior. |
| [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) | Pre-push and pre-publish validation checklist. |

## Status

Current package version: `0.0.1`.

Before publishing a new release, update the version in `pyproject.toml`,
`src/codeglance/__init__.py`, this README badge, and the brand badge text. Use
[`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) for the full validation pass.
