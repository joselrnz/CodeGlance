# Codeglance Mega Plan

This is the working plan for making Codeglance competitive with visual codebase understanding tools
while keeping the product shape simple:

- Python-first and pip-installable.
- Static-output friendly: HTML, Markdown, JSON, TOON, and schema files still open without a backend.
- Local-first serving through `codeglance serve`.
- Useful to humans and agents from the same analysis pass.
- Deterministic by default, with optional AI enrichment only when configured.
- No Node, database, hosted service, or mandatory API key.

## Product North Star

Codeglance should answer two questions quickly:

1. For humans: "What is this repo and where should I look first?"
2. For agents: "What compact context should I read before touching code?"

The main output remains `glance.html`. The agent entrypoint remains `llms.txt` plus compact generated
context. Any future feature should compile into the generated bundle instead of requiring a live app.

## Current Baseline

Already implemented:

- `glance.html`: self-contained interactive canvas graph.
- Overview, Drill, Explore, Tour personas in the top bar and Tools sidebar.
- Structural, Domain, and Knowledge modes.
- Folder drill-down, breadcrumbs, full-path labels, and up navigation.
- Left Tools sidebar and right Inspector sidebar.
- Source snippets with expand, VS Code link, and Cursor link.
- Mobile-friendly Tools rail, Inspector pill, terminal dock, and bottom-center zoom controls.
- Quiet watch-mode refresh: `serve --watch` detects newer output and marks the toolbar Refresh button.
- `codeglance serve`: local output browser with desktop and LAN URLs.
- `codeglance generate`: profile-based output bundles.
- `codeglance review`: graph/output quality report.
- `codeglance ask`: deterministic graph-backed Q&A with cited evidence and JSON/Markdown output.
- `codeglance processes`: explicit business domain and process-flow sidecar output.
- `codeglance agents`: safe agent/editor guidance install planning.
- First-class `knowledge-graph.json` fields for `domains`, `flows`, `processes`, process evidence,
  and process confidence.
- `knowledge-graph.toon` domain, flow, and process-step tables for compact agent context.
- Domain inspector process-flow evidence and terminal commands: `flows`, `flow <query>`,
  `processes`, and `process <query>`.
- Domain flow cards show steps, files, confidence, entry/exit hints, clickable timeline steps, and
  open-first-step actions.
- `impact.md`, `onboarding.md`, `agent.md`, `llms.txt`, `knowledge-graph.toon`,
  `knowledge-graph.json`, `llm-context.schema.json`, and `meta.json`.
- `codeglance init`: project config, agent instructions, and command assets.
- Localization foundation: locale normalization, string catalog fallback, and coverage validation.
- Static HTML localization shell: `VizConfig(ui_language=...)` and
  `codeglance generate --language/--ui-language` set `<html lang dir>` and localize toolbar,
  Tools, overview, inspector, terminal/help, filter/theme menus, path modal, and empty-state labels
  without changing graph IDs or schema keys.
- `codeglance init --language/--ui-language/--content-language` writes project localization defaults.
- Broad language extraction through Python AST and tree-sitter language pack.
- Static package version policy: package version is `0.0.1` until intentionally changed.

## Capability Matrix

| Capability | Status | Next Improvement |
| --- | --- | --- |
| Static interactive HTML | Shipped | Continue UI validation on large repos. |
| Local output browser | Shipped | Improve landing page cards and artifact grouping. |
| Watch mode | Shipped | Keep refresh quiet; never show pop-up banners. |
| Folder drill-down | Shipped | Add smarter nested layout for very wide folders. |
| Breadcrumb/up navigation | Shipped | Add keyboard shortcut and terminal command aliases. |
| Inspector source view | Shipped | Add better code expansion and copy/open affordances. |
| Editor links | Shipped | Keep VS Code/Cursor links, add graceful fallback copy action. |
| Graph review report | Shipped | Add `doctor` for release/readiness checks. |
| Impact report | Shipped | Add changed-only context mode. |
| Agent context | Shipped | Add richer `ask` intents and generated answer artifacts. |
| Domain mode | Flow cards shipped | Add deeper Process subview and broader flow polish. |
| Knowledge mode | Partial | Add concept/entity extraction from docs. |
| Persona modes | Partial | Expand from current view presets into audience presets. |
| Language concepts | Partial | Add concept cards and filters. |
| Localization | UI/runtime gate shipped | Generated prose localization remains opt-in/future. |
| Agent installers | Foundation | Add marketplace manifests and platform-specific validation. |
| Team sharing | Partial docs | Add release/share checklist and commit policy. |

## Immediate Push Readiness

Before pushing to GitHub, run this sequence:

```bash
python -m pytest
python -m build
python -m codeglance generate . --out .codeglance/outputs --profile all --full
python -m codeglance review . -o .codeglance/outputs/review.md
python -m codeglance ask "What should I read first?" . --format json
python -m codeglance processes . --format json
python -m codeglance agents plan . --platform codex
```

Then manually verify:

- `glance.html` opens through `codeglance serve`.
- Overview, Drill, Explore, and Tour all render.
- Tools sidebar, Inspector sidebar, terminal, and zoom controls do not overlap.
- Folder drill-down breadcrumbs can go back up.
- The toolbar Refresh button is quiet and does not display a pop-up banner.
- `index.html` lists expected artifacts.
- `review.md` reports no issues before release.

## Phase 1: Release Hardening

Goal: make the package safe to push and publish as `0.0.1`.

Features:

- Add a release checklist.
- Build the wheel and source distribution.
- Install the wheel in a temporary virtual environment.
- Smoke-test CLI commands from the installed package:
  - `codeglance --help`
  - `codeglance init`
  - `codeglance generate`
  - `codeglance serve`
  - `codeglance review`
- Confirm `.gitignore` does not accidentally commit bulky local generated output.

Suggested files:

- `README.md`
- `docs/README.md`
- `docs/RELEASE_CHECKLIST.md`
- `.gitignore`
- `tests/test_smoke.py`

Validation:

```bash
python -m pytest
python -m build
python -m pip install --force-reinstall dist/codeglance-0.0.1-py3-none-any.whl
codeglance --help
```

## Phase 2: `codeglance doctor`

Goal: turn repeated manual checks into one command.

Command:

```bash
codeglance doctor .
```

Checks:

- package version consistency
- required dependencies import correctly
- output folder exists or can be generated
- `meta.json` matches the current graph
- `glance.html` includes required runtime markers
- `review.md` is clean
- generated profile has expected files
- local server command can bind to a requested port or report the conflict clearly

Output:

- concise terminal summary
- optional Markdown report with `-o`
- non-zero exit code only for real blockers

Suggested files:

- `src/codeglance/commands/doctor.py`
- `src/codeglance/cli/parser.py`
- `src/codeglance/render/workflows.py`
- `src/codeglance/services/projects.py`
- `tests/test_smoke.py`

## Phase 3: `codeglance ask` Foundation

Status: foundation shipped. The command works offline, returns Markdown or JSON, and cites graph
evidence.

Goal: let users and agents ask repo questions without stuffing the whole repo into a prompt.

Command:

```bash
codeglance ask "How does auth work?"
```

Default mode should be retrieval-only:

1. Read `llms.txt`.
2. Read `agent.md`.
3. Use `knowledge-graph.toon` for compact graph context.
4. Pull focused sections from `context.md`.
5. Cite exact file paths and node IDs.
6. Tell the user which files to open next.

Optional LLM mode can call a configured provider, but the command must still work without an API key.

Suggested files:

- `src/codeglance/commands/ask.py`
- `src/codeglance/cli/parser.py`
- `src/codeglance/output/llm.py`
- `src/codeglance/services/`
- `tests/test_smoke.py`

## Phase 4: Business Flow Extraction

Goal: make Domain mode tell a clearer story for non-experts.

Detect:

- entry points
- routes/controllers/handlers
- services and repositories
- Terraform modules/resources
- data objects
- test files
- cross-domain dependencies

Output:

- flow cards in `glance.html`
- flow section in `wiki.html`
- compact flow summary in `agent.md`
- optional `flows.md` in full/human profiles

Static constraint:

- flow data is computed during analysis and embedded in generated files
- no backend calls from `glance.html`

## Phase 5: Persona Presets

Goal: make the UI friendlier without removing power-user depth.

Current top-level views already behave like personas:

- Overview: normal user / architecture map
- Drill: files and classes without function noise
- Explore: full engineer graph
- Tour: guided walkthrough

Next iteration:

| Persona | Default View | Adds |
| --- | --- | --- |
| Human | Overview | simple language, fewer controls |
| Developer | Drill | imports, paths, code snippets |
| Reviewer | Drill + Diff | impact, risks, changed nodes |
| PM | Domain | business flows and capabilities |
| Agent | Explore | stable IDs, paths, context hints |

Implementation notes:

- Keep the top bar small.
- Put advanced controls in the Tools sidebar.
- Persist choices in local storage.
- Do not bring back a crowded top-right More menu.

## Phase 6: Language Concept Cards

Goal: teach what the repo uses, not only where files live.

Concepts to detect:

- Python: decorators, dataclasses, generators, async functions, protocols
- JavaScript/TypeScript: components, hooks, interfaces, async functions
- Java: controllers, services, repositories, records, annotations
- Rust: traits, impl blocks, enums, macros
- Go: interfaces, goroutines, handlers, structs
- Terraform: providers, modules, variables, outputs, resources
- SQL: tables, views, indexes, migrations
- Zig/C/C++: structs, enums, allocators, build files, exported APIs

Outputs:

- concept filters in Tools
- concept cards in Glance
- `concepts.md`
- high-signal concept summary in `agent.md`

## Phase 7: Knowledge And Docs Graph

Goal: make docs and wiki pages navigable like code.

Improve:

- heading-to-heading links
- docs that reference files/classes/functions
- TODO/risk/decision extraction
- agent read-order recommendations
- stale-doc detection when docs mention missing files

Optional AI lane:

- entity/claim extraction
- plain-English summaries
- localized summaries

Deterministic output must stay useful without AI.

## Phase 8: Localization

Goal: localize UI labels first, generated summaries later.

Step 1:

- add a UI string table
- support `en` first, then `es`
- apply labels to buttons, panels, terminal help, empty states

Step 2:

- optional `--language`
- store language in `.codeglance/config.json`
- localize LLM summaries only when AI enrichment is enabled

All strings must be embedded in the static HTML.

## Phase 9: Team Sharing Policy

Goal: make it obvious what to commit.

Usually commit:

- `llms.txt`
- `agent.md`
- `knowledge-graph.toon`
- `llm-context.schema.json`
- `meta.json`
- optionally `wiki.html`
- optionally `review.md`

Usually keep local:

- screenshots
- temporary validation artifacts
- very large full visual bundles
- stale demo outputs

Commit `glance.html` only when the team wants visual artifacts in Git. Otherwise regenerate locally.

## Implementation Order

Current project decision: do not push until Codeglance is materially stronger than Understand
Anything in Q&A, business flows, localization, and platform installers. The implementation contract
for those four gates lives in [`COMPETITIVE_SUPERSET_PLAN.md`](COMPETITIVE_SUPERSET_PLAN.md).

Recommended next sequence:

1. Harden multi-agent/platform installer docs and validation.
2. Release hardening and wheel install smoke.
3. `codeglance doctor`.
4. Deeper Process subview and broader flow polish.
5. Persona preset cleanup.
6. Language concept cards.
7. Knowledge/docs graph improvements.

The first four items are the competitive gate. The later items reduce push/publish risk and improve
product depth without changing the static/Python-first architecture.

## Validation Standard

Every phase should pass:

```bash
python -m pytest
python -m codeglance generate . --out .codeglance/outputs --profile all --full
python -m codeglance review . -o .codeglance/outputs/review.md
python -m codeglance serve . --dir .codeglance/outputs --host 0.0.0.0 --watch --profile all
```

For UI changes, also validate:

- desktop screenshot
- tablet-width screenshot
- phone-width screenshot
- no toolbar overlap
- both sidebars reachable
- terminal reachable
- breadcrumb/up navigation works
- toolbar Refresh button is quiet
- `file://` open still works
- no browser console errors

## Guardrails

- Do not require Node, npm, a database, or a hosted service.
- Do not make AI calls mandatory.
- Do not let the top toolbar grow again.
- Do not use pop-up refresh banners.
- Do not make generated output depend on a live server.
- Do not replace TOON/agent.md with raw full-repo dumps.
- Do not hide file paths from agents; humans can get friendlier labels, agents need stable IDs.

## Success Criteria

Codeglance is ready when a user can:

1. Run `pip install codeglance`.
2. Run `codeglance init --generate`.
3. Run `codeglance serve . --dir .codeglance/outputs --host 0.0.0.0 --watch --profile all`.
4. Open `glance.html` on desktop or phone.
5. See Overview, Drill, Inspector, source snippets, breadcrumbs, and terminal.
6. Give an agent `llms.txt` as the first read.
7. Refresh generated memory after edits without pop-up spam.
8. Run `codeglance impact` and `codeglance review` before committing.
9. Share a compact, explainable artifact bundle with the team.
