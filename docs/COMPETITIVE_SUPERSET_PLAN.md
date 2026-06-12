# Competitive Superset Plan

This plan replaces the earlier "push soon" path. Codeglance will not be pushed as `0.0.1` until it
is materially stronger than Understand Anything in the four areas where that project is visibly
ahead:

1. natural-language Q&A
2. explicit business process steps and flows
3. localization
4. broad agent/platform installers

The target is not feature parity. The target is a better Python-first implementation:

- deterministic and useful without an API key
- static artifacts first
- evidence and citations instead of opaque answers
- generated files that work for humans and agents
- no Node, database, hosted service, or agent-platform runtime dependency

## Implementation Status

Foundation shipped on 2026-06-12:

- `codeglance ask`: deterministic, no-API-key graph Q&A with cited node IDs and file paths.
- `codeglance processes`: explicit business domain/process map in Markdown or JSON.
- `codeglance agents`: registry, dry-run planning, and safe installation for common agent/editor guidance files.
- Agent/editor adapters now validate required Codeglance artifact references and optional marketplace
  manifest structure.
- `src/codeglance/i18n.py`: offline locale normalization and UI/CLI string catalog foundation.
- Generated bundles include `processes.md` and `processes.json` for `human`, `agent`, and `all` profiles.
- Public SDK exports include `answer_question(...)` and `render_process_report(...)`.
- `knowledge-graph.json` now persists domains, flows, process aliases, process evidence, and
  confidence.
- `knowledge-graph.toon` now includes compact domain, flow, and process-step tables.
- `glance.html` supports static UI localization via `VizConfig(ui_language=...)` and
  `codeglance generate --language/--ui-language`, including document `lang`, `dir`, embedded
  runtime UI labels, inspector labels, terminal/help labels, filter/theme menus, and path modal
  labels.
- Domain inspector now shows persisted process flows with clickable step evidence, and the offline
  terminal supports `flows`, `flow <query>`, `processes`, and `process <query>`.
- Domain inspector flow cards now show step count, file count, confidence, entry/exit hints, a
  compact clickable step timeline, and an open-first-step action.

Still to finish before claiming full competitive advantage:

- richer `ask` intents such as reverse dependencies, changed-file risk, and read-first recommendations
- deeper Process subview and broader flow-focused polish beyond the Domain inspector cards
- generated prose localization policy and optional LLM-backed content localization
- release wheel smoke and `doctor`

## Capability 1: `codeglance ask`

**Capability**

Users and agents can ask questions about a repo and get deterministic, cited answers from the graph
without sending the whole repo to a model. Optional LLM mode only synthesizes over retrieved
evidence.

**Why this beats a chat box**

- Every answer cites graph node IDs and file paths.
- Default mode works offline.
- Retrieval uses the generated graph, summaries, symbols, layers, tour, and source snippets.
- Low-token by construction: map first, source last.

**Implementation contract**

Add modules:

- `src/codeglance/ask/models.py`
- `src/codeglance/ask/index.py`
- `src/codeglance/ask/retrieve.py`
- `src/codeglance/ask/render.py`
- `src/codeglance/ask/llm.py`
- `src/codeglance/commands/ask.py`

Update:

- `src/codeglance/cli/parser.py`
- `src/codeglance/commands/__init__.py`
- `src/codeglance/services/projects.py`
- `src/codeglance/api.py`
- `src/codeglance/output/llm.py`
- `tests/test_ask.py` or `tests/test_smoke.py`

CLI:

```bash
codeglance ask "How does checkout work?"
codeglance ask "Where is OrderService used?" --format json
codeglance ask "What imports routes.py?" --depth 2
codeglance ask "What should I read first?" --limit 8
codeglance ask "How does checkout work?" --llm
```

Retrieval steps:

1. Load or analyze `KnowledgeGraph`.
2. Build an in-memory `AskIndex`.
3. Detect query intent:
   - where
   - how
   - dependencies
   - reverse dependencies
   - read-first
   - changed/risk
4. Rank evidence by lexical score, graph proximity, type/path boosts, layer/tour boosts, and
   deduplication by file path.
5. Render Markdown or JSON with:
   - answer
   - evidence
   - related files
   - next reads
   - limits/uncertainty

Tests:

- CLI registers `ask`.
- JSON output is parseable.
- Questions find known symbols in example projects.
- Reverse-dependency questions return valid evidence.
- No API key path always succeeds.
- `--llm` unavailable path falls back cleanly.
- Evidence paths exist and snippets stay capped.

## Capability 2: Persisted Business Domains, Flows, And Process Steps

**Status**

Core persistence is shipped. The graph schema, TOON output, process sidecar commands, SDK facade,
and generated LLM context schema now carry domains, flows, processes, and process steps. The HTML
inspector and terminal can read those flows. Domain inspector cards now expose the main process
story for non-experts; remaining work is a deeper Process subview and broader flow-focused polish.

**Capability**

Domain mode becomes first-class graph data, not just renderer-derived cards. Codeglance should
serialize domains, flows, processes, and process steps into JSON/TOON/Markdown so humans and agents
can inspect the same business map.

**Why this beats a visual-only domain view**

- Every flow and step has evidence: file path, node ID, line range, signature.
- Business claims are diffable and reviewable.
- Agents can read compact business context without opening the HTML.
- Deterministic extraction ships first; LLM naming can come later.

**Implementation contract**

Schema additions:

- `Domain`
- `BusinessFlow`
- `BusinessProcess`
- `ProcessStep`

Add graph fields:

- `domains`
- `flows`
- `processes`
- `processSteps`

Add module:

- `src/codeglance/analyze/domains.py`

Update:

- `src/codeglance/schema.py`
- `src/codeglance/models.py` or model facade exports
- `src/codeglance/graph.py`
- `src/codeglance/render/__init__.py`
- `src/codeglance/render/template_parts/script.py`
- `src/codeglance/render/wiki.py`
- `src/codeglance/render/context.py`
- `src/codeglance/output/toon.py`
- `src/codeglance/output/llm.py`
- `tests/test_smoke.py`

Extraction heuristics:

- service/app/module boundaries
- route/controller/handler names and decorators
- Java service/repository/model packages
- Terraform modules/resources/outputs/variables
- call-chain verbs such as `validate`, `charge`, `save`, `ship`, `notify`, `provision`
- imports and dependency edges grouped by domain

UI:

- Domain cards show kind, summary, entities, entrypoints, confidence, inbound/outbound flows.
- Inspector shows flow evidence and open-source-node actions. **First pass done.**
- Add a deeper Process subview beyond the Domain inspector cards.
- Terminal commands:
  - `domains`
  - `flows`
  - `flow <domain>`
  - `processes`
  - `process <name>`

Generated outputs:

- `wiki.html`: Business Flows and Processes sections.
- `agent.md`: compact business domains, key flows, process steps.
- `knowledge-graph.toon`: compact domain/flow/process tables.
- `llm-context.schema.json`: document new fields.
- Optional later: `flows.md`.

Tests:

- schema round trip with domains/flows/processes.
- microservices checkout process steps.
- Java service flow from service to repository/model.
- Terraform root module to network/app modules/resources.
- negative shared/utility fixture to avoid noisy fake domains.

## Capability 3: Localization

**Status**

Static HTML localization is now usable offline. `VizConfig(ui_language=...)` normalizes locale IDs,
sets document `lang` and RTL/LTR direction, and localizes toolbar/Tools chrome, overview labels,
inspector labels, terminal/help labels, filter/theme menus, path modal labels, and empty states.
`codeglance generate --language/--ui-language` writes localized bundles. `codeglance init
--language/--ui-language/--content-language` records project defaults in `.codeglance/config.json`.
Remaining work is generated prose localization policy and optional LLM-backed content localization.

**Capability**

Codeglance supports deterministic UI localization for more languages than Understand Anything,
without translating graph IDs or agent-critical structured data. Generated prose localization is
opt-in.

**Why this beats basic `--language`**

- UI localization works offline.
- Graph schema remains stable for tools.
- Agent artifacts remain English by default for reliability.
- Generated prose localization is explicit, not accidental.
- Fallback is deterministic and testable.

**Implementation contract**

Add:

- `src/codeglance/i18n.py`
- optional `src/codeglance/config_project.py` or similar typed config loader

Catalogs:

- `en`
- `es`
- `zh`
- `zh-TW`
- `ja`
- `ko`
- `ru`
- `pt-BR`
- `fr`
- `de`
- `it`
- `tr`
- `pl`
- `uk`
- `id`
- `vi`
- `hi`
- `ar`
- `he`
- `nl`
- `sv`

CLI/config:

```bash
codeglance generate . --language es
codeglance generate . --ui-language ja --content-language en
codeglance generate . --language es --localize-generated-text --llm
codeglance init --language es
codeglance --list-languages
```

Config fields:

```json
{
  "language": "en",
  "uiLanguage": "en",
  "contentLanguage": "en",
  "localizeGeneratedText": false
}
```

HTML:

- set `<html lang="...">`
- set `dir="rtl"` for `ar` and `he`
- embed selected catalog plus English fallback
- localize toolbar labels, titles, placeholders, terminal help, export menu, path finder, empty
  states, inspector labels, and cards. **Done for English, Spanish, Japanese, and Arabic runtime
  coverage; other locales safely fall back per key.**

Policy:

- Never translate JSON keys, node IDs, edge types, file paths, TOON field names, or schema terms.
- UI strings localize offline.
- Agent artifacts stay English unless explicitly configured.
- If generated-text localization is requested without an API key, fall back to English and record
  actual language in metadata.

Tests:

- locale fallback chain: `es-MX -> es -> en`
- required core keys exist for every locale
- HTML embeds selected locale and direction
- missing translations fall back to English
- agent outputs stay English by default
- `init --language` writes config. **Done.**
- RTL smoke for `ar`

## Capability 4: Multi-Agent And Platform Installers

**Capability**

Codeglance generates high-quality adapters for many coding agents without depending on any of
them. The package remains a universal context generator, not an agent runtime.

**Why this beats plugin sprawl**

- One pip package generates files for many tools.
- No platform SDK dependency.
- Every adapter points to the same canonical artifacts.
- Safe install behavior: dry-run, skip, merge, force.

**Implementation contract**

Add package:

```text
src/codeglance/integrations/
├── __init__.py
├── registry.py
├── install.py
├── templates.py
├── validation.py
└── platforms/
    ├── codex.py
    ├── claude.py
    ├── cursor.py
    ├── windsurf.py
    ├── copilot.py
    ├── gemini.py
    ├── cline.py
    ├── roo.py
    ├── aider.py
    └── generic.py
```

Tier 1 targets:

- Codex/generic: `AGENTS.md`, `.agents/skills/codeglance/SKILL.md`
- Claude Code: `.claude/skills/codeglance/SKILL.md`, `.claude/commands/codeglance.md`
- Cursor: `.cursor/rules/codeglance.mdc`
- Windsurf: `.windsurf/rules/codeglance.md`
- GitHub Copilot: `.github/copilot-instructions.md`
- Gemini CLI: `GEMINI.md`
- Cline/Roo: `.clinerules/codeglance.md`, `.roo/rules/codeglance.md`
- Aider: `CONVENTIONS.md` or comment-safe `.aider.conf.yml` guidance
- Continue: `.continue/rules/codeglance.md`

CLI:

```bash
codeglance init --agents default
codeglance init --agents all
codeglance init --agents claude,codex,cursor,copilot
codeglance init --list-agents
codeglance init --dry-run
codeglance init --marketplace-manifests

codeglance agents list
codeglance agents install --platform all
codeglance agents install --platform cursor --dry-run
codeglance agents validate
```

Safety:

- never overwrite by default
- `codeglance init` skips existing files by default
- `codeglance agents install` reports conflicts by default
- `--force`/`--overwrite` replaces selected integration files when explicitly requested
- `--dry-run` writes nothing
- no API keys, network calls, post-commit hooks, or shell auto-execution in templates
- all paths repo-relative and Windows/POSIX safe

Current implementation note:

- Tier 1 registry paths, selector parsing, dry-run, validation, and optional local marketplace
  manifests are implemented.
- The integration package is split into `models.py`, `templates.py`, `registry.py`, and `install.py`;
  `__init__.py` remains a compatibility facade for public imports.
- Validation checks missing files, modified files, missing required artifact references, unreadable
  files, and invalid marketplace manifest contracts.
- Platform matrix and safety behavior are documented in `docs/INTEGRATIONS.md`.
- Merge-block editing and ownership-aware force are still pending; do not market those as shipped.

Tests:

- registry contains stable platform IDs and file lists
- default behavior preserves current generated files
- selected platform install writes only selected files
- `--agents all` writes all Tier 1 assets
- dry-run writes nothing
- no-overwrite and force behavior
- invalid platform returns supported list
- generated files mention `llms.txt`, `agent.md`, `impact.md`, and `review.md`

## Four-Agent Implementation Model

Use four workstreams with disjoint ownership to avoid conflicts.

| Agent | Workstream | Primary Write Scope |
| --- | --- | --- |
| Agent 1 | Q&A / `ask` | `src/codeglance/ask/`, `src/codeglance/commands/ask.py`, CLI/API wiring, ask tests |
| Agent 2 | Domains/flows/processes | `src/codeglance/analyze/domains.py`, schema fields, TOON/schema docs, domain tests |
| Agent 3 | Localization | `src/codeglance/i18n.py`, render options, template strings, CLI/config language flags, i18n tests |
| Agent 4 | Integrations/installers | `src/codeglance/integrations/`, `init`/`agents` CLI, templates, installer tests |

Shared files require coordination:

- `src/codeglance/cli/parser.py`
- `src/codeglance/commands/__init__.py`
- `src/codeglance/api.py`
- `src/codeglance/services/projects.py`
- `src/codeglance/schema.py`
- `src/codeglance/output/llm.py`
- `tests/test_smoke.py`
- `README.md`
- docs

Rule: each workstream lands its core package first, then one integration patch touches shared files.

## Implementation Order

Do not implement all four at once. The dependency order should be:

1. **Foundation split**
   - create new packages: `ask`, `integrations`, `i18n`
   - add tests for pure helpers
   - avoid shared renderer churn
2. **Schema/domain persistence**
   - add domain/flow/process fields to graph model
   - migrate current renderer-derived domain logic into persisted data
3. **Q&A retrieval**
   - build graph evidence index
   - implement `codeglance ask` retrieval-only mode
4. **Localization shell**
   - add config loader and language flags
   - localize static shell labels while preserving English default
5. **Installer registry**
   - move current `init` assets into integration templates
   - add platform selection/dry-run
6. **Generated output expansion**
   - update agent context, wiki, TOON, schema contract, and review checks
7. **Optional LLM lanes**
   - Q&A synthesis over evidence
   - generated text localization only when requested
8. **HTML polish**
   - process subview
   - localized terminal/help
   - ask-style graph commands in terminal
9. **Validation gauntlet**
   - full tests
   - wheel install
   - generated outputs
   - screenshots for desktop/mobile/localized HTML
   - large repo smoke

## Pre-Push Completion Gate

Do not push until all are true:

- `codeglance ask` works offline and cites evidence.
- `knowledge-graph.json` persists domains, flows, processes, and steps. **Done.**
- `glance.html` can render localized UI in at least English, Spanish, Japanese, and one RTL locale.
  **Done for UI/runtime labels: English, Spanish, Japanese, and Arabic.**
- `codeglance init --agents all --dry-run` shows all Tier 1 platform outputs. **Done.**
- `codeglance review` validates the expanded bundle.
- Full test suite passes.
- Wheel install smoke passes.
- Docs explain the four capabilities clearly.

## Non-Goals

- No hosted chat service.
- No mandatory LLM API key.
- No vector database dependency.
- No Node/npm runtime.
- No agent platform SDK dependency.
- No automatic post-commit hook unless the user explicitly requests it.

## Open Questions

- Which optional LLM providers should be supported after the Anthropic path: OpenAI, local OpenAI-compatible endpoint, or both?
- Should `ask-index.json` be generated by default, or built on demand from `knowledge-graph.json`?
- Should `flows.md` be a default `all` profile artifact once flows are persisted?
- Which localized catalogs need human review before release?
- Should marketplace manifests ship in the package or be generated only with `--marketplace-manifests`?
