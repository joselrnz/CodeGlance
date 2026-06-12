# Competitive Audit: Codeglance vs Understand Anything

This audit compares Codeglance against the public Understand Anything feature set as of
2026-06-12. It is not a clone plan. It is a push-readiness check for whether Codeglance has a clear
product reason to exist.

Sources checked:

- https://github.com/Egonex-AI/Understand-Anything
- https://understand-anything.com/
- https://dev.to/arshtechpro/understand-anything-turn-any-codebase-into-an-interactive-knowledge-graph-37ed

## Bottom Line

Codeglance is already stronger for a Python package workflow:

- `pip install` shape instead of plugin-first install.
- Pure Python CLI and static output.
- Self-contained `glance.html` that works from disk.
- Generated agent context bundle: `llms.txt`, `agent.md`, TOON, JSON, schema, review report.
- Local output browser with watch mode and quiet refresh.
- Release-oriented validation through `codeglance review`.

Understand Anything is still stronger in four visible areas:

- Natural-language chat/Q&A.
- Business process flow cards.
- Localized generated UI/content.
- Broad multi-agent/plugin marketplace distribution.

Those four areas should drive the next roadmap after release hardening.

## Component Scorecard

| Component | Understand Anything Public Claim | Codeglance Status | Decision Before Push |
| --- | --- | --- | --- |
| Interactive graph | Hierarchical drill-down, smart layout, community clustering | Shipped: overview, drill, explore, folder drill-down, breadcrumbs, canvas graph | Good enough to push; keep validating on large repos |
| File/function/class graph | Every file, function, class, dependency | Shipped across Python and tree-sitter languages | Good enough to push |
| Domain view | Business domains, flows, process steps | Partial: domain cards and cross-domain flow edges exist; process steps are not explicit | Not a push blocker; next product gap |
| Knowledge graph | Wiki/docs graph with implicit relationships and claims | Partial: Markdown/docs nodes and knowledge mode exist; claim extraction is not done | Not a push blocker |
| Search | Fuzzy and semantic search | Shipped: fuzzy and offline keyword semantic ranking | Good enough to push; true embedding search later |
| Filters | Type, complexity, layer | Shipped: category/type/layer/filter controls | Good enough to push |
| Dependency path finder | Shortest path between components | Shipped: path finder and terminal graph commands | Good enough to push |
| Guided tours | AI-generated walkthroughs | Shipped deterministic tours; optional LLM layer naming/summaries exist | Good enough to push |
| Diff impact | Ripple effects before commit | Shipped: `impact.md` and changed-file overlay | Good enough to push |
| Persona UI | Junior dev, PM, power user | Partial: Overview/Drill/Explore/Tour view presets | Not a push blocker; needs clearer persona naming later |
| Language concepts | Pattern explanations in context | Partial: symbol extraction and language notes exist; concept cards not implemented | Not a push blocker |
| Chat/Q&A | Ask anything about the codebase | Missing: planned `codeglance ask` | Biggest functional gap after release |
| Localization | UI labels, summaries, tours in supported languages | Missing | Not a push blocker for `0.0.1`; roadmap item |
| Auto-update | Auto-update hook and incremental updates | Partial: fingerprints and `serve --watch`; no post-commit hook | Not a push blocker |
| Plugin distribution | Claude, Codex, Cursor, Copilot, Gemini, more | Partial: generated Codex/Claude-style assets; no broad installer | Not a push blocker for PyPI-first package |
| Team sharing | Commit graph artifacts, Git LFS guidance | Partial: release/team sharing docs now exist | Good enough to push after `.gitignore` cleanup |
| Output validation | Not emphasized as a primary feature | Shipped: `codeglance review` | Codeglance advantage |
| Static/offline bundle | Dashboard/plugin oriented | Shipped: HTML/Markdown/JSON/TOON work without backend | Codeglance advantage |

## What Codeglance Should Be Better At

Codeglance should not try to win by having the most animated graph. It should win by being the most
practical, packageable, agent-readable version:

1. Install with pip.
2. Generate one deterministic bundle.
3. Open HTML locally or from a phone.
4. Give agents a compact read-first protocol.
5. Validate outputs before pushing.

That means the push bar is not "clone every Understand Anything feature." The push bar is:

- core graph works
- generated files are coherent
- CLI package builds and installs
- docs explain the workflow
- known gaps are explicit

## Push Blockers

These should be fixed before pushing:

- Build artifacts and release-smoke folders must stay ignored.
- Full test suite must pass.
- Wheel must build and install into a clean venv.
- Installed CLI must run `init`, `generate`, `review`, and `context`.
- Generated review report must be clean.

## Not Push Blockers

These are product gaps but should not block the first GitHub push:

- `codeglance ask`
- `codeglance doctor`
- process-step extraction
- concept cards
- localization
- broad plugin installers
- GitHub Actions release workflow

## Next Product Work

After push readiness:

1. `codeglance doctor`
2. `codeglance ask`
3. explicit business flow/process extraction
4. concept cards
5. localization
6. plugin/skill templates for more agent platforms

This order keeps Codeglance useful today while directly addressing the places where Understand
Anything is visibly ahead.
