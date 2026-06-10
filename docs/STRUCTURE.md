# CodeGlance package structure

CodeGlance is organized as a Python SDK with a thin CLI on top.

## Current layout

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

## Reference pattern

IBM watsonx Orchestrate ADK uses a Python package plus CLI model, with clear
resource areas such as `agents/`, `tools/`, `knowledge/`, and `flows/`, plus
command families for environment, agent, tool, and settings workflows.

CodeGlance follows the same shape at package scale:

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

A future `pydantic` extra can add strict validation models without changing the
current public imports.
