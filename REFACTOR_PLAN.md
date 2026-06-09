# ScopingLang — Software-Engineering Refactor Plan

> Goal: make the codebase clean, packaged, and **configuration-driven** so visual/behavioural
> tweaks happen in **one typed place** instead of hunting magic numbers across files.
> Status: PLAN ONLY — no code changed yet. Implement after review.

---

## Part A — Current architecture (what we have)

```
src/scopinglang/
  __init__.py        public API — exports schema classes only
  cli.py             argparse CLI (analyze / render / dashboard)   ✅ clean
  schema.py          dataclasses: Node/Edge/Layer/TourStep/Project/KnowledgeGraph  ✅ good
  layout.py          force-directed + swimlane layout              ⚠ hardcoded dims
  graph.py           orchestrates analysis → KnowledgeGraph
  fingerprint.py     incremental-analysis hashing
  ignore.py          .gitignore-style filtering
  scan.py            project file inventory
  analyze/           language extractors (tree-sitter), layers, tour, llm, pipeline
  render/
    __init__.py      build_view_model() — colors + card dims       ⚠ scattered config
    template.py      interactive canvas HTML (data+JS+CSS inlined)  ⚠ JS constants separate
    static.py        zero-JS SVG renderer                          ⚠ hardcoded ocean colors
    icons.py         vendored devicon SVGs
```

**Already solid:** dataclasses with `to_dict`/`from_dict`, type hints, `validate()`, packaged via
`pyproject.toml` (hatchling, `scopinglang` console script, pure-pip deps).

### Full repository tree (root → every source file)
```
scopinglang/
├── .claude
│   └── launch.json
├── demo
│   └── *.html  (generated, gitignored)
├── examples
│   ├── flaskapp
│   │   ├── blueprints
│   │   │   ├── auth.py
│   │   │   └── blog.py
│   │   ├── templates
│   │   │   ├── base.html
│   │   │   └── index.html
│   │   ├── README.md
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── models.py
│   ├── microservices
│   │   ├── services
│   │   │   ├── cart
│   │   │   │   └── cart.py
│   │   │   ├── catalog
│   │   │   │   └── catalog.py
│   │   │   ├── gateway
│   │   │   │   └── gateway.py
│   │   │   ├── notifications
│   │   │   │   └── notifications.py
│   │   │   ├── orders
│   │   │   │   └── orders.py
│   │   │   ├── payments
│   │   │   │   └── payments.py
│   │   │   ├── recommendations
│   │   │   │   └── recommendations.py
│   │   │   └── shipping
│   │   │       └── shipping.py
│   │   └── README.md
│   ├── taskman
│   │   ├── app
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   └── routes.py
│   │   ├── tests
│   │   │   └── test_routes.py
│   │   ├── README.md
│   │   └── requirements.txt
│   ├── terraform-aws
│   │   ├── modules
│   │   │   └── network
│   │   │       ├── main.tf
│   │   │       ├── outputs.tf
│   │   │       └── variables.tf
│   │   ├── README.md
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   └── wiki
│       ├── attention.md
│       ├── embeddings.md
│       ├── index.md
│       ├── training.md
│       └── transformers.md
├── src
│   └── scopinglang
│       ├── analyze
│       │   ├── languages
│       │   │   ├── __init__.py
│       │   │   ├── c.py
│       │   │   ├── cpp.py
│       │   │   ├── csharp.py
│       │   │   ├── generic.py
│       │   │   ├── go.py
│       │   │   ├── java.py
│       │   │   ├── javascript.py
│       │   │   ├── kotlin.py
│       │   │   ├── lua.py
│       │   │   ├── php.py
│       │   │   ├── python.py
│       │   │   ├── ruby.py
│       │   │   ├── rust.py
│       │   │   ├── scala.py
│       │   │   ├── swift.py
│       │   │   └── typescript.py
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── imports.py
│       │   ├── layers.py
│       │   ├── llm.py
│       │   ├── pipeline.py
│       │   ├── registry.py
│       │   ├── tour.py
│       │   └── ts_core.py
│       ├── render
│       │   ├── __init__.py
│       │   ├── icons.py
│       │   ├── static.py
│       │   └── template.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── fingerprint.py
│       ├── graph.py
│       ├── ignore.py
│       ├── layout.py
│       ├── scan.py
│       └── schema.py
├── tests
│   ├── fixtures
│   │   ├── imports
│   │   │   ├── store
│   │   │   │   └── store.go
│   │   │   ├── util
│   │   │   │   └── Helper.java
│   │   │   ├── Main.java
│   │   │   ├── app.cpp
│   │   │   ├── go.mod
│   │   │   ├── lib.h
│   │   │   ├── main.go
│   │   │   ├── main.rs
│   │   │   └── util.rs
│   │   ├── legacy
│   │   │   ├── Lib.hs
│   │   │   ├── alu.sv
│   │   │   ├── calc.adb
│   │   │   ├── calc.jl
│   │   │   ├── counter.vhd
│   │   │   ├── hello.cob
│   │   │   ├── lib.ml
│   │   │   ├── main.tf
│   │   │   ├── mathmod.f90
│   │   │   ├── token.sol
│   │   │   └── widget.dart
│   │   └── multilang
│   │       ├── Program.cs
│   │       ├── Server.java
│   │       ├── app.js
│   │       ├── helper.js
│   │       ├── index.php
│   │       ├── lib.rs
│   │       ├── main.go
│   │       ├── model.rb
│   │       ├── script.lua
│   │       ├── service.ts
│   │       └── util.cpp
│   └── test_smoke.py
├── .gitignore
├── README.md
├── REFACTOR_PLAN.md
└── pyproject.toml
```

### Current package tree (the software itself)
```
src/scopinglang/
├── __init__.py          public API — re-exports schema classes only
├── __main__.py          `python -m scopinglang`
├── cli.py               argparse CLI (analyze / render / dashboard)     ✅
├── schema.py        ★   models: Node/Edge/Layer/TourStep/Project/Graph  ✅ + loose string sets
├── graph.py             analysis orchestrator (scan → analyze → graph)
├── scan.py              project file inventory
├── ignore.py            .gitignore-style filtering
├── fingerprint.py       incremental-analysis hashing
├── layout.py        ⚠   force-directed + swimlane layout (CARD_W/CARD_H/gaps hardcoded)
├── analyze/
│   ├── base.py, registry.py, pipeline.py, imports.py, layers.py, tour.py, llm.py, ts_core.py
│   └── languages/       16 extractors (python, go, rust, java, ts, …)
└── render/
    ├── __init__.py  ⚠   build_view_model() — TYPE_COLORS / LAYER_PALETTE / card dims scattered
    ├── template.py  ⚠   interactive canvas HTML (THEMES/accents live in inlined JS)
    ├── static.py    ⚠   zero-JS SVG — 10 hardcoded ocean hex colors (out of sync w/ gold)
    └── icons.py         vendored devicon SVGs
```
(plus `examples/` — 6 sample projects, and `tests/` — `test_smoke.py` + `fixtures/` for ~40 languages.)

### Target package tree (after this refactor — ★ = new, ✦ = touched)
```
src/scopinglang/
├── enums.py        ★   NodeType · Complexity · EdgeType · ThemeName   (str-enums, JSON-safe)
├── schema.py       ✦   uses enums; validate() checks type/complexity validity
├── layout.py       ✦   compute_layered_layout(records, n_layers, config=DEFAULT_CONFIG)
└── render/
    ├── config.py   ★   VizConfig — every card dim/gap/palette/colour/theme in ONE typed place
    ├── __init__.py ✦   build_view_model(graph, root, config=DEFAULT_CONFIG)
    ├── template.py ✦   default theme injected from config.default_theme
    └── static.py   ✦   colours pulled from config/theme (no more hardcoded ocean)
```
Public API (`__init__.py`) gains: `VizConfig`, `DEFAULT_CONFIG`, `NodeType`, `Complexity`, `ThemeName`.

---

## Part B — Problems found (with evidence)

### B1. Visual/layout config is scattered as magic numbers (the "nasty to update" problem)
The same *kind* of value lives in 4 different files with no single source of truth:

| Value | Where it lives now |
|---|---|
| Node card size `216 × 82` | `layout.py:19-20` (`CARD_W`, `CARD_H`) |
| Swimlane gaps/pad/header | `layout.py:21-29` (`_GAP_X _GAP_Y _PAD _HEADER _LANE_GAP _LEFT _TOP _MAX_COLS`) |
| Type → color map | `render/__init__.py:17-23` (`TYPE_COLORS`, `DEFAULT_TYPE_COLOR`) |
| Layer palette | `render/__init__.py:26-31` (`LAYER_PALETTE`, `UNASSIGNED_COLOR`) |
| Layer card dims `300×150` + gaps | `render/__init__.py:208` (`LW, LH, GX, GY` — inline locals) |
| Domain card dims + gaps | `render/__init__.py:309` (`DW, DH, DGX, DGY` — inline locals) |
| Knowledge card dims | `render/__init__.py:128` (`KW, KH` — inline locals) |
| Max embedded source bytes | `render/__init__.py:34` (`_MAX_SOURCE_BYTES`) |
| Themes / accents / default theme | `template.py` JS (`THEMES`, `ACCENTS`, `THEME_STATE`) |
| Static-render colors | `static.py` — **10 hardcoded ocean hex values** |

→ To change a card size you edit `layout.py`; to change a color you edit `render/__init__.py`;
to change the theme you edit JS. There is **no way to pass overrides in**.

### B2. Categorical values are loose string sets/dicts, not enums
- `schema.py:19` `NODE_TYPES` (set of 13 strings)
- `schema.py:40` `COMPLEXITY_VALUES = {"simple","moderate","complex"}`
- `schema.py:30` `EDGE_WEIGHTS` (dict keyed by edge-type strings)
- `render/__init__.py` `_ENTITY_TYPES`, `FILE_LEVEL_TYPES`
- Theme names (`"gold"`, `"ocean"`, …) are bare strings in JS.

→ No autocomplete, no typo protection, no single definition. Magic strings everywhere.

### B3. Static renderer is out of sync
`static.py` still paints the **old ocean theme** (`#0a0e14`, `#e8edf2`, `rgba(91,164,207,…)`, …)
while the interactive default is now **gold**. It also ignores node/layer colors from config.

### B4. `validate()` doesn't check value validity
`KnowledgeGraph.validate()` checks ids/edges/orphans but never verifies that
`node.type ∈ NODE_TYPES` or `node.complexity ∈ COMPLEXITY_VALUES`.

### B5. Docstrings & encapsulation are uneven
- Helpers like `edge_weight`, `_kebab`, several `layout.py`/`render` functions lack docstrings.
- Palette indexing (`LAYER_PALETTE[i % len(...)]`) is repeated inline in 3 spots instead of a
  single accessor ("getter").

---

## Part C — Proposed plan (phased, each phase keeps tests green)

### Phase 1 — Enums (new `src/scopinglang/enums.py`)
`str`-based enums so JSON stays **byte-identical** (value *is* the string):
```python
class NodeType(str, Enum):
    FILE="file"; FUNCTION="function"; CLASS="class"; MODULE="module"; CONCEPT="concept"
    CONFIG="config"; DOCUMENT="document"; SERVICE="service"; TABLE="table"
    ENDPOINT="endpoint"; PIPELINE="pipeline"; SCHEMA="schema"; RESOURCE="resource"      # 13

class Complexity(str, Enum):
    SIMPLE="simple"; MODERATE="moderate"; COMPLEX="complex"

class EdgeType(str, Enum):                          # weights stay in EDGE_WEIGHTS keyed by .value
    CONTAINS="contains"; INHERITS="inherits"; IMPLEMENTS="implements"; CALLS="calls"
    EXPORTS="exports"; IMPORTS="imports"; DEPENDS_ON="depends_on"; CONFIGURES="configures"
    TRIGGERS="triggers"; TESTED_BY="tested_by"; DOCUMENTS="documents"; SERVES="serves"
    ROUTES="routes"; DEPLOYS="deploys"; PROVISIONS="provisions"; MIGRATES="migrates"; DEFINES_SCHEMA="defines_schema"

class ThemeName(str, Enum):
    GOLD="gold"; OCEAN="ocean"; FOREST="forest"; ROSE="rose"; LIGHT="light"
```
- Derive legacy sets so every current import keeps working:
  `NODE_TYPES = frozenset(t.value for t in NodeType)` (same for `COMPLEXITY_VALUES`).
- `FILE_LEVEL_TYPES` and the domain `_ENTITY_TYPES` become enum-derived frozensets.
- `Node.type` / `Node.complexity` stay `str` on the wire; helpers accept `str` **or** the enum
  (since `NodeType.FILE == "file"` is `True` for a `str`-enum).

### Phase 2 — Central typed config (new `src/scopinglang/render/config.py`)
```python
@dataclass(frozen=True)
class VizConfig:
    # node cards
    card_w: float = 216.0
    card_h: float = 82.0
    # swimlane layout
    lane_gap_x: float = 26.0; lane_gap_y: float = 22.0; lane_pad: float = 18.0
    lane_header: float = 36.0; lane_spacing: float = 48.0
    lane_left: float = 48.0; lane_top: float = 48.0; max_cols: int = 8
    # layer overview cards / domain cards / knowledge cards
    layer_card_w: float = 300.0; layer_card_h: float = 150.0; layer_gap_x: float = 48.0; layer_gap_y: float = 44.0
    domain_card_w: float = 300.0; domain_card_h: float = 150.0; domain_gap_x: float = 60.0; domain_gap_y: float = 70.0
    knowledge_card_w: float = 280.0; knowledge_card_h: float = 150.0
    # colors + theme
    type_colors: Mapping[str, str] = <devicon-style palette>
    default_type_color: str = "#94a3b8"
    layer_palette: tuple[str, ...] = (...16 hues...)
    unassigned_color: str = "#64748b"
    default_theme: ThemeName = ThemeName.GOLD
    # source embedding
    max_source_bytes: int = 16_000

    # encapsulated accessors ("getters")
    def color_for_type(self, t: str) -> str: ...
    def layer_color(self, i: int) -> str: ...

DEFAULT_CONFIG = VizConfig()
```
All current magic numbers move here **with identical defaults** → output unchanged.

### Phase 3 — Thread the config through (pass-in variables)
```python
compute_layered_layout(records, n_layers, config=DEFAULT_CONFIG)
build_view_model(graph, root=None, config=DEFAULT_CONFIG)
render_interactive(graph, root=None, config=DEFAULT_CONFIG)
render_static(graph,  root=None, config=DEFAULT_CONFIG)
```
- Keep module-level aliases (`TYPE_COLORS = DEFAULT_CONFIG.type_colors`, etc.) for back-compat.
- Inject `config.default_theme` into `template.py` (replace the hardcoded `name:'gold'`), so the
  Python config controls the landing theme.
- Rewrite `static.py` to pull colors from the active theme/config (fixes B3).
- Optional: expose `--card-width`, `--theme`, etc. as CLI flags that build a `VizConfig`.

### Phase 4 — Validation + docstrings
- Extend `KnowledgeGraph.validate()` to warn on `type ∉ NodeType` and `complexity ∉ Complexity`.
- Docstring sweep on the undocumented helpers; ensure every public function has one.

### Phase 5 — Tests
- `test_viz_config_overrides`: a custom `VizConfig(card_w=300)` is reflected in the output.
- `test_enums_match_legacy_sets`: enum-derived sets equal the old constants (compat guarantee).
- `test_validate_flags_bad_type`: validation catches an unknown node type.
- `test_static_uses_theme`: static render reflects the configured theme, not hardcoded ocean.

---

## Part D — Compatibility & risk

- **Zero behavioural change** in phases 1-2: defaults equal today's values, JSON schema untouched
  (`str` enums serialize to the same strings). Existing 32 tests must stay green throughout.
- Highest-risk step is Phase 3 wiring; do it module-by-module, re-running tests each time.
- Back-compat aliases mean no external import breaks.

---

## Part E — Output parity vs the original (review "what we missed")

✅ Already matched: gold accent, collapsible clusters, card hierarchy (badge/complexity/heading/
description), rounded accent bar, edge-label pills, entity pills, selection heartbeat, responsive
header, offline terminal.

🔲 Still open / candidate adds (separate from this refactor):
- Node-card **metrics row** (degree + line range), **inline code peek**, **connection dots**.
- **Side-by-side** cluster layout option (we stack swimlanes vertically).
- Optional **Python (Pyodide)** execution in the terminal (online-only).
- `static.py` visual parity with the interactive render (covered by Phase 3).

---

## Suggested order to implement
1. Phase 1 (enums) → 2. Phase 2 (config) → 3. Phase 3 wiring (layout → render → template → static)
→ 4. Phase 4 (validate + docstrings) → 5. Phase 5 (tests) → re-render demos → commit + push.
