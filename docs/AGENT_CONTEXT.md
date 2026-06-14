# Agent Context

CodeGlance serves two audiences from one analysis pass:

- Humans get a self-contained HTML graph and wiki they can inspect visually.
- Agents get Markdown that is small enough to read often, but rich enough to choose the next files to open.

## Current Behavior

An agent can refresh a compact project memory after each change, read that memory first, then open only the files relevant to the requested task. The same underlying graph powers the HTML, wiki, full context map, and compact agent handoff, so human and agent views stay aligned.

## Constraints

- Keep the default install simple: `pip install codeglance`.
- Do not require a server, database, vector store, or external API for deterministic analysis.
- Do not include source code in the agent handoff by default; point to the files instead.
- Preserve a full Markdown mode for deeper work.
- Always respect ignore rules and generated-output ignores.
- Regenerate via incremental fingerprints so repeated runs are cheap.

## Current Interfaces

- `codeglance .` writes `.codeglance/knowledge-graph.json` and `.codeglance/knowledge-graph.html`.
- `codeglance wiki .` writes a human-readable docs page from the same graph.
- `codeglance context . --mode full` emits the complete dependency-first Markdown map.
- `codeglance context . --mode agent -o AGENTS.md` emits the low-token agent handoff.
- `codeglance generate . --out .codeglance/outputs` emits the default LLM-ready bundle:
  `llms.txt`, `agent.md`, `llm-context.schema.json`, `knowledge-graph.toon`, `glance.html`,
  `knowledge-graph.json`, `meta.json`, and `index.html`.
- `codeglance serve . --host 0.0.0.0` hosts generated outputs for desktop and phone review.

## Agent Workflow

1. Read `llms.txt` first for the current artifact list and read order.
2. Read `agent.md` next. Treat it as Tier 1 context: project shape, read order, changed files, and rules.
3. Read `llm-context.schema.json` when a tool or agent needs field meanings, artifact tiers, node types, or edge types.
4. Use `knowledge-graph.toon` when an LLM needs compact structured graph context in the prompt.
5. Use `knowledge-graph.json` when a parser, renderer, or tool needs canonical machine-readable data.
6. If the task is still unclear, read `context.md` or generate `codeglance context . --mode full`. Treat that as Tier 2 context.
7. Open source only for files named by Read First, Changed Since Last Run, or Dependency Hotspots.
8. Follow dependency edges one hop at a time instead of scanning the entire tree.
9. Make the change.
10. Run tests or targeted validation.
11. Refresh the output bundle when the code shape changed.
12. Use `codeglance serve .codeglance/outputs --host 0.0.0.0` when a human needs to inspect the generated outputs locally.

## Design Notes

- OpenAI prompt guidance recommends clear Markdown/XML boundaries, retrieved context, and explicit workflow guidance. Codeglance keeps the agent handoff structured and small instead of stuffing the whole repo into a prompt.
- Claude Code memory guidance uses persistent Markdown project memory. Codeglance's `agent.md` is a generated project memory that can be refreshed after code changes.
- Aider's repo map keeps a compact symbol/file map under a token budget and expands when needed. Codeglance follows the same principle with `agent.md` first, `context.md` second, and source files last.
- Repository-level coding research shows that multi-file changes need repository context and dependency analysis instead of isolated local prompts.
- Graph-RAG/codebase graph research supports deterministic structural graphs over naive vector/text retrieval for multi-hop architecture questions.
- TOON-style structured context is useful for LLM prompts because it keeps tabular graph data while reducing repeated JSON field names. JSON stays canonical for tools and parsing.

## External Patterns

- Aider repo maps: compact symbol/file maps sent with change requests instead of entire repos.
- Repomix-style packing: optional full-repo export in Markdown, XML, JSON, or plain text when a model really needs a bundle.
- `llms.txt`: a small, stable entrypoint that tells agents where the current docs and context live.
