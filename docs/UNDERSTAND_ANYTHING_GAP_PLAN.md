# Understand Anything Gap Plan

This document tracks what Codeglance is still missing compared with Understand Anything and how to add the useful parts without changing the core product shape.

Codeglance should stay:

- Python-first and pip-installable.
- Static-output friendly: `glance.html`, `wiki.html`, Markdown, JSON, TOON, and schema files should remain openable without a backend.
- Easy to serve locally with Python: `codeglance serve .codeglance/outputs --host 0.0.0.0`.
- Useful for both humans and agents from one analysis pass.
- Deterministic by default, with optional AI enrichment only when configured.

## Reference Baseline

Understand Anything currently emphasizes:

- interactive graph exploration with hierarchical drill-down
- business-domain mapping, flows, and process steps
- knowledge-base graphs for docs and wiki content
- fuzzy and semantic search
- guided tours and onboarding
- diff impact analysis
- persona-adaptive UI
- language concept explanations
- natural-language Q&A
- localized summaries and UI labels
- auto-update hooks and incremental refresh
- multi-platform agent/plugin installation

Codeglance already covers the core offline graph, generated wiki, agent context, TOON, schema, impact/onboarding docs, mobile-friendly Glance UI, local serving, editor links, and broad language extraction. The gaps below focus on product polish and agent workflow depth.

## Capability Matrix

| Capability | Codeglance Today | Gap | Priority |
| --- | --- | --- | --- |
| Static interactive HTML | Self-contained `glance.html` with structural/domain/knowledge modes | Keep improving layout and validation | Done / ongoing |
| Local output browser | `codeglance serve` hosts generated files | Add watch mode and browser refresh | High |
| Folder drill-down | Layer cards, folders, files, breadcrumbs, up navigation | Continue validating on large repos | Medium |
| Fuzzy search | Present | Improve ranking and scoped search | Medium |
| Semantic search | Offline keyword-style semantic mode | Optional LLM/embedding-backed mode later | Medium |
| Dependency path finder | Present | Add path explanations for non-experts | Medium |
| Diff impact | Markdown impact report and changed-file overlay | Add generated graph validation/review report | High |
| Guided tours | Deterministic tour steps | Add persona-specific tour copy | Medium |
| Business domains | Domain mode exists | Add explicit flow/process-step extraction | High |
| Knowledge graph | Markdown links and docs graph | Add entity/claim extraction as optional AI lane | Medium |
| Natural-language Q&A | Offline terminal supports graph queries | Add `codeglance ask` using generated context | High |
| Persona modes | Not present | Add Overview/Developer/Reviewer/PM modes | Medium |
| Language concepts | Parser extracts classes/functions/resources | Add concept cards and concept filters | Medium |
| Localization | English only | Add UI string table, then optional localized summaries | Low / Medium |
| Auto-update | Fingerprints avoid unnecessary re-analysis | Add `serve --watch` and `init --hook` | High |
| Plugin distribution | Local `.agents` and `.claude` skill assets | Add broader generated skill/plugin templates | Medium |
| Team sharing | Generated folder is commit-friendly | Document what to commit and when to use Git LFS | Low |

## Product Direction

The right direction is not to copy every Understand Anything surface. Codeglance should become the clean, Python-native version:

1. Generate durable static artifacts.
2. Serve them locally when needed.
3. Give agents a small, structured memory first.
4. Let humans inspect the same facts visually.
5. Add optional AI only where deterministic analysis cannot infer intent.

The HTML should remain the primary visual output. Any new features should compile into the generated bundle rather than requiring a long-running web app.

## Phase 1: Live Static Workflow

### Goal

Make the local HTML workflow feel live without turning Codeglance into a server product.

### Features

- `codeglance serve --watch`
  - Watches source files and `.codeglance/config.json`.
  - Regenerates the configured output profile after changes.
  - Keeps the same local URL alive.
  - Prints desktop and LAN URLs.
- Browser auto-refresh
  - `glance.html` can optionally poll `meta.json`.
  - If the analysis timestamp or graph hash changes, show a small "Refresh available" button.
  - Avoid forced refresh while the user is inspecting code.
- `codeglance init --hook`
  - Installs an optional post-commit hook.
  - Regenerates `agent.md`, `llms.txt`, `knowledge-graph.toon`, and `meta.json`.
  - Does not force users to commit generated HTML unless they choose to.

### Static HTML Constraint

`glance.html` must still work from `file://`. Auto-refresh should be best-effort and only active when served over HTTP.

### Suggested Files

- `src/codeglance/serve.py`
- `src/codeglance/commands/serve.py`
- `src/codeglance/commands/init.py`
- `src/codeglance/render/template_parts/script.py`
- `tests/test_smoke.py`

### Validation

- Generate a bundle.
- Run `codeglance serve .codeglance/outputs --host 0.0.0.0 --watch`.
- Edit a source file.
- Confirm `meta.json` changes.
- Confirm the browser shows a refresh notice.
- Confirm `file:///.../glance.html` still opens without errors.

## Phase 2: Agent Q&A Without Bloat

### Goal

Let users ask codebase questions while preserving the low-token context process.

### Feature

`codeglance ask "How does auth work?"`

The command should read generated artifacts in this order:

1. `llms.txt`
2. `agent.md`
3. `knowledge-graph.toon`
4. selected excerpts from `context.md`
5. selected source snippets only when necessary

### Design

- Default mode should be retrieval-only and explain what files to read.
- Optional LLM mode can call a configured provider.
- Output should cite node IDs and file paths.
- The command should never paste the entire repo into a prompt.

### Static HTML Constraint

The HTML terminal can expose the same graph-query commands offline. Natural-language Q&A should live in CLI first, then maybe become an optional served endpoint later.

### Suggested Files

- `src/codeglance/commands/ask.py`
- `src/codeglance/cli/parser.py`
- `src/codeglance/output/llm.py`
- `src/codeglance/services/`
- `tests/test_smoke.py`

### Validation

- Ask a file-location question.
- Ask an architecture question.
- Ask a changed-file impact question.
- Confirm answers cite generated artifacts and source paths.
- Confirm no answer requires reading the whole repo.

## Phase 3: Business Flow Extraction

### Goal

Make Domain mode tell a story: domains, workflows, steps, and implementation files.

### Features

- `codeglance domain .`
- Domain cards:
  - name
  - purpose
  - main files
  - entry points
  - outgoing dependencies
  - risks or review notes
- Flow cards:
  - trigger
  - steps
  - implementation nodes
  - data objects involved
  - test files when detected

### Deterministic First Pass

Infer domains from:

- folder names
- route/controller naming
- service names
- Terraform resource groups
- package/module boundaries
- dependency direction
- docs headings

Optional AI can rename domains and summarize intent, but the underlying graph should be usable without AI.

### Static HTML Constraint

Domain and flow data should be embedded in `glance.html` and exported to `knowledge-graph.json`. Domain mode should not call a backend.

### Suggested Files

- `src/codeglance/analyze/domain.py`
- `src/codeglance/schema.py`
- `src/codeglance/render/__init__.py`
- `src/codeglance/render/template_parts/script.py`
- `src/codeglance/render/wiki.py`
- `tests/test_smoke.py`

### Validation

- Test against `examples/microservices`.
- Test against `examples/java-service`.
- Test against Terraform examples.
- Confirm domains are useful even with no LLM key.

## Phase 4: Persona Modes

### Goal

Make Glance easier for normal users while preserving depth for engineers.

### Modes

| Mode | Default Detail | Best For |
| --- | --- | --- |
| Overview | Layers, folders, top files | Non-technical walkthrough |
| Developer | Files, classes, dependencies, paths | Implementation work |
| Reviewer | Changed files, risk, impact, tests | PR review |
| PM | Domains, flows, user-facing capabilities | Product understanding |
| Agent | Compact IDs, paths, edge labels, context hints | AI/code agent navigation |

### UI Changes

- Add an audience selector in the left tools panel.
- Keep the top toolbar small.
- Store the mode in local storage.
- Each mode changes defaults only; users can still override filters.

### Static HTML Constraint

Persona modes should be pure client-side state in `glance.html`.

### Suggested Files

- `src/codeglance/render/template_parts/markup.py`
- `src/codeglance/render/template_parts/css.py`
- `src/codeglance/render/template_parts/script.py`
- `docs/GLANCE_WALKTHROUGH.md`
- `tests/test_smoke.py`

### Validation

- Screenshots at desktop, tablet, and phone widths.
- Confirm no toolbar overlap.
- Confirm sidebars remain usable.
- Confirm terminal remains reachable on mobile.

## Phase 5: Language Concepts

### Goal

Teach the codebase, not just show nodes.

### Concepts To Detect

- Python: decorators, dataclasses, generators, async functions, context managers, protocols
- JavaScript/TypeScript: hooks, components, async functions, interfaces, generics
- Java: controllers, services, repositories, annotations, records
- Rust: traits, impl blocks, enums, macros
- Go: interfaces, goroutines, handlers, structs
- Terraform: modules, variables, outputs, resources, providers
- SQL: tables, views, migrations, indexes
- Zig/C/C++: structs, enums, allocators, build files, exported APIs

### Output

- Concept cards in Glance.
- `concepts.md` in full/human/agent profiles.
- Concept filters in the tools panel.
- Concept summaries in `agent.md` when high-signal.

### Static HTML Constraint

Concepts should be computed during analysis and embedded in the bundle.

### Suggested Files

- `src/codeglance/analyze/languages/*`
- `src/codeglance/schema.py`
- `src/codeglance/output/profiles.py`
- `src/codeglance/render/template_parts/script.py`
- `tests/fixtures/`
- `tests/test_smoke.py`

### Validation

- Add fixtures per language concept.
- Confirm concepts appear in `knowledge-graph.json`.
- Confirm concepts are filterable in Glance.

## Phase 6: Graph Review Report

### Goal

Make generated output trustworthy before users push or share it.

### Feature

`codeglance review . -o .codeglance/review.md`

Checks:

- orphan-heavy layers
- missing summaries
- huge folders that need drill grouping
- unsupported or unknown languages
- broken edges
- duplicate node IDs
- missing source snippets
- stale fingerprints
- generated output not matching current commit

### Static HTML Constraint

The review report should be Markdown plus optional summary cards in `index.html`. No server required.

### Suggested Files

- `src/codeglance/commands/review.py`
- `src/codeglance/services/review.py`
- `src/codeglance/output/generate.py`
- `src/codeglance/output/index.py`
- `tests/test_smoke.py`

### Validation

- Run against this repo.
- Run against Ghostty output.
- Force a broken graph in a test fixture and confirm the report catches it.

## Phase 7: Localization

### Goal

Support localized UI labels first, then optional localized summaries later.

### Step 1: UI Strings

- Add a small string table:
  - `en`
  - `es`
  - `zh`
  - `ja`
  - `ko`
  - `ru`
- Apply to buttons, tooltips, panel headings, terminal help, and empty states.

### Step 2: Generated Text

- Optional `--language`.
- Store chosen language in `.codeglance/config.json`.
- Deterministic fallback remains English.
- LLM-generated summaries can be localized only when AI enrichment is enabled.

### Static HTML Constraint

All strings must be embedded in `glance.html`; no remote translation calls.

### Suggested Files

- `src/codeglance/config.py`
- `src/codeglance/render/template_parts/script.py`
- `src/codeglance/render/template_parts/markup.py`
- `src/codeglance/commands/init.py`
- `tests/test_smoke.py`

### Validation

- Generate with `--language es`.
- Confirm UI labels change.
- Confirm graph data still validates.
- Confirm no missing string keys.

## Phase 8: Multi-Agent And Plugin Assets

### Goal

Make Codeglance easy for agents to use across tools without making the core package depend on any one agent.

### Features

- `codeglance init --agents`
- `codeglance init --agents codex`
- `codeglance init --agents claude,cursor,copilot,gemini`
- Generated command/skill assets:
  - read `llms.txt`
  - refresh `agent.md`
  - generate full bundle
  - explain one file
  - run impact before commit

### Static HTML Constraint

Plugins should call the Python CLI and generated files. They should not require a Node service or hosted API.

### Suggested Files

- `src/codeglance/commands/init.py`
- `src/codeglance/templates/agents/`
- `docs/AGENT_CONTEXT.md`
- `tests/test_smoke.py`

### Validation

- Init a temp repo.
- Confirm generated skill files contain correct commands.
- Confirm paths are relative and portable.

## Phase 9: Team Sharing

### Goal

Make it clear what teams should commit and what should stay local.

### Recommended Policy

Commit for team onboarding:

- `.codeglance/outputs/llms.txt`
- `.codeglance/outputs/agent.md`
- `.codeglance/outputs/knowledge-graph.toon`
- `.codeglance/outputs/llm-context.schema.json`
- `.codeglance/outputs/meta.json`
- optionally `.codeglance/outputs/wiki.html`

Usually do not commit:

- screenshots
- temporary browser validation artifacts
- stale demo outputs
- very large `knowledge-graph.json` unless the team agrees

Use Git LFS when:

- generated JSON or HTML crosses repository size limits
- teams want to commit full visual bundles for large monorepos

### Suggested Files

- `README.md`
- `docs/AGENT_CONTEXT.md`
- `.gitignore`
- `.codeglance/.codeglanceignore`

## Implementation Order

The strongest next sequence is:

1. `serve --watch` plus refresh notice.
2. `review.md` graph/output validator.
3. `ask` command that consumes existing generated context.
4. Business flow extraction.
5. Persona modes in Glance.
6. Language concept cards.
7. Localization.
8. Broader plugin templates.
9. Team sharing polish.

This order improves the current workflow first. It also reduces risk because every later feature can reuse the watch, validation, and generated-context foundation.

## Validation Standard

Every phase should pass:

```bash
python -m pytest
python -m codeglance generate . --out .codeglance/outputs --profile all --full
python -m codeglance serve .codeglance/outputs --host 0.0.0.0
```

For UI changes, also validate:

- desktop screenshot
- tablet-width screenshot
- phone-width screenshot
- no toolbar overlap
- both sidebars reachable
- terminal reachable
- breadcrumb/up navigation works
- `file://` open still works
- no browser console errors

## Guardrails

- Do not require Node, npm, a database, or a hosted service.
- Do not make AI calls mandatory.
- Do not let the top toolbar grow again; use side panels and progressive disclosure.
- Do not make generated output depend on a live server.
- Do not replace TOON/agent.md with raw full-repo dumps.
- Do not hide file paths from agents; humans can get friendlier labels, agents need stable IDs.

## Success Criteria

Codeglance is competitive when a user can:

1. Run `pip install codeglance`.
2. Run `codeglance init --generate`.
3. Run `codeglance serve .codeglance/outputs --host 0.0.0.0 --watch`.
4. Open `glance.html` on desktop or phone.
5. See overview, drill folders, inspect source, and follow breadcrumbs.
6. Ask an agent to read `llms.txt` first.
7. Refresh generated memory after edits.
8. Run an impact/review report before committing.
9. Share a compact, explainable artifact bundle with the team.

