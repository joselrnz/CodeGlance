# CodeGlance package structure

CodeGlance is organized as a Python SDK with a thin CLI on top.

## Root Tree

```text
codeglance/
├── .agents/                # local CodeGlance skill for repo mapping
├── .claude/                # Claude-compatible skill metadata
├── brand/                  # SVG brand assets
├── docs/                   # package and agent documentation
├── src/codeglance/         # installable Python package
├── tests/                  # pytest smoke tests and fixtures
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

Generated and local-only folders such as `.codeglance/`, `dist/`, `.pytest_cache/`, `.ruff_cache/`,
and `__pycache__/` are intentionally ignored.

## Package Tree

```text
src/codeglance/
├── analyze/
│   ├── languages/          # per-language tree-sitter extraction specs
│   ├── base.py             # declarative language definition helpers
│   ├── imports.py          # local dependency resolution
│   ├── layers.py           # architecture layer detection
│   ├── llm.py              # optional LLM enrichment
│   ├── pipeline.py         # structural extraction pipeline
│   ├── registry.py         # language registry
│   ├── tour.py             # guided-tour generation
│   └── ts_core.py          # tree-sitter adapter
├── ask/
│   ├── models.py           # cited answer/result dataclasses
│   ├── render.py           # Markdown/JSON answer rendering
│   └── retrieval.py        # graph-evidence retrieval for repo questions
├── cli/
│   ├── __init__.py         # exports main/build_parser for package entrypoint
│   ├── main.py             # process entrypoint and default command dispatch
│   └── parser.py           # argparse command/flag definitions
├── commands/
│   ├── analyze.py          # analyze/render/dashboard/wiki/context commands
│   ├── agents.py           # agent/editor integration commands
│   ├── ask.py              # graph-evidence question answering command
│   ├── common.py           # shared CLI helpers
│   ├── generate.py         # output-bundle command
│   ├── init.py             # config and local integration bootstrap
│   ├── processes.py        # domain/process map command
│   ├── serve.py            # local server command
│   └── workflows.py        # explain, hippocampus, impact, review, onboard commands
├── integrations/
│   ├── install.py          # repo-local guidance file writer
│   ├── models.py           # integration target/file models
│   ├── registry.py         # supported agent/editor target registry
│   └── templates.py        # generated guidance text
├── models/
│   ├── __init__.py         # stable public model imports
│   ├── constants.py        # schema constants and vocabulary
│   └── graph.py            # model facade over schema dataclasses
├── output/
│   ├── generate.py         # output bundle orchestration
│   ├── index.py            # output-folder HTML index
│   ├── llm.py              # llms.txt and LLM context schema
│   ├── profiles.py         # minimal/human/agent/all profiles
│   └── toon.py             # compact TOON graph renderer
├── render/
│   ├── context.py          # Markdown context for agents
│   ├── icons.py            # vendored file-type icon data
│   ├── static.py           # zero-JS static HTML renderer
│   ├── template_parts/     # CSS/JS/HTML chunks for the interactive graph
│   ├── template.py         # interactive HTML renderer template
│   ├── wiki.py             # generated wiki renderer
│   └── workflows.py        # Markdown workflow reports
├── services/
│   └── projects.py         # reusable analyze/render/generate workflows
├── api.py                  # public SDK surface
├── config.py               # typed visualization config
├── enums.py                # schema/render enum vocabulary
├── fingerprint.py          # incremental analysis fingerprints
├── graph.py                # analysis orchestration
├── ignore.py               # lightweight ignore matching
├── layout.py               # graph layout engine
├── processes/              # domain/process map extraction
├── scan.py                 # project scanner and language detection
├── schema.py               # canonical JSON/dataclass schema
└── serve.py                # local artifact browser
```

## Responsibility Table

| Area | Path | Purpose |
| --- | --- | --- |
| Public SDK | `src/codeglance/api.py` | Python-callable workflows: analyze, render, generate, load, save. |
| Services | `src/codeglance/services/` | Reusable workflow implementation used by SDK and CLI. |
| Public models | `src/codeglance/models/` | Stable model facade over the internal schema dataclasses. |
| CLI parser | `src/codeglance/cli/` | Entrypoint and argument parser only. |
| CLI commands | `src/codeglance/commands/` | Command implementations split by workflow. |
| Analysis | `src/codeglance/analyze/` | Language registry, structural extraction, layers, tours, LLM enrichment. |
| Output bundles | `src/codeglance/output/` | Generated bundle profiles, LLM context, TOON, index, orchestration. |
| Renderers | `src/codeglance/render/` | Interactive HTML, static HTML, wiki, and agent context renderers. |
| Local server | `src/codeglance/serve.py` | Hosts generated HTML/Markdown/JSON folders locally. |

## Package Boundaries

- `api.py` is the SDK entrypoint.
- `services/` owns reusable workflows.
- `cli/` is only parser/dispatch.
- `commands/` owns workflow-specific CLI handlers.
- `models/` is the stable import target for graph data structures.
- `output/` owns generated artifacts for humans and agents.

## Pydantic-style boundary

The package currently keeps dataclasses instead of adding Pydantic as a runtime
dependency. That preserves the lightweight install while still giving users a
typed, structured model facade:

```python
from codeglance.api import analyze_project, render_html
from codeglance.models import KnowledgeGraph

graph: KnowledgeGraph = analyze_project(".")
html = render_html(graph, ".")
```

## Generated Output Layout

The default generated bundle lives under `.codeglance/outputs/`:

```text
.codeglance/outputs/
├── index.html
├── llms.txt
├── glance.html
├── wiki.html
├── processes.md
├── processes.json
├── agent.md
├── context.md
├── hippocampus.md
├── onboarding.md
├── impact.md
├── review.md
├── graph.static.html
├── llm-context.schema.json
├── knowledge-graph.toon
├── knowledge-graph.json
└── meta.json
```

The `minimal` profile writes the compact subset. Use `--profile all` for the complete folder shown
above.

## Import Guidance

Use these imports in new code:

```python
from codeglance.api import analyze_project, generate_bundle, render_html
from codeglance.models import KnowledgeGraph, Node, Edge
```

The old `codeglance.schema` module remains the canonical implementation and compatibility layer,
but `codeglance.models` is the cleaner SDK-facing namespace.
