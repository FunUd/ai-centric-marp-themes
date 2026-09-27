# Diagram Creation

The `marp-diagram-creator` skill generates theme-aware, slide-safe SVG diagrams from **Mermaid**, **draw.io**, and structured **JSON** sources. Text-only patterns (timelines, steps, matrices, checklists) use **CSS Native** theme classes — no image needed. All tools are permissive OSS (MIT / Apache-2.0).

### Supported Engines

| Engine | Best For |
|---|---|
| **Mermaid** (`@mermaid-js/mermaid-cli`, MIT) | Flowcharts, sequence diagrams, state machines, 3-tier architecture |
| **draw.io** (Apache-2.0 mxGraph XML) | Cloud infrastructure, complex multi-container systems |
| **JSON SVG** (stdlib Python) | Pie/donut charts, pyramids, cycles, org charts, radial concepts, funnels |
| **CSS Native** (theme classes, no image) | Text-only ≤5 items: `timeline` / `steps`+`arrows` / `grid-quadrant`+`axes` / `checklist` / `timetable` |

> Engine choice SSoT: `skills/marp-diagram-creator/references/diagram-patterns.md` §3 is the decision table; `SKILL.md` §2 mirrors it.

### Generating a Diagram

The engine ships inside the `marp-diagram-creator` skill, so it is available
wherever the skill is installed. Resolve it once:

```bash
ENGINE=$(python skills/marp-diagram-creator/scripts/print-engine-path.py)
```

```bash
# From a Mermaid template (requires Node / npx)
python "$ENGINE/render-slide-diagram.py" \
  -i "$ENGINE/templates/mermaid/sequence-api.mmd" \
  -o slides/my-deck/assets/diagrams/api-flow.svg \
  --theme azure-clarity --layout full

# From a draw.io template
python "$ENGINE/render-slide-diagram.py" \
  -i "$ENGINE/templates/drawio/system-architecture.drawio" \
  -o slides/my-deck/assets/diagrams/system-arch.svg \
  --theme prism-edge --layout full

# Inline Mermaid code (always pass --layout explicitly; default full shrunk into col2/asym overflows or degrades)
python "$ENGINE/render-slide-diagram.py" \
  --code "flowchart LR; A[入力] --> B[処理] --> C[出力]" \
  -o slides/my-deck/assets/diagrams/simple-flow.svg \
  --theme nebula-glass --layout full

# From a JSON chart template (pure stdlib — no Node, no network)
python "$ENGINE/render-slide-diagram.py" \
  -i "$ENGINE/templates/charts/revenue-pie.json" \
  -o slides/my-deck/assets/diagrams/revenue-pie.svg \
  --theme azure-clarity --layout full
```

> Inside a clone of this repository the engine source is at
> `scripts/diagrams/`. That is the development SSoT and is kept
> byte-identical to the vendored copy (`python scripts/sync-skill-vendor.py --check`).
> Always resolve `ENGINE` via `print-engine-path.py` and use `$ENGINE/...` so the same
> command works inside and outside a checkout.

### Embedding in a Slide

```markdown
# システム構成

![width:1050px center](assets/diagrams/system-arch.svg)
```

Safe embedding widths by layout (canonical values: `scripts/diagrams/layout_spec.py`):

| Layout | `_class` directive | Recommended `width:` | Max safe width |
|---|---|---|---|
| Full slide | (default) | `width:1050px` | 1120px |
| 2-column | `cols-2`, `split-2`, `split-glass`, `glass-card-layout` | `width:500px` | 520px |
| Asymmetric split | `split-asym`, `split-asym-reverse` | `width:680px` | 710px |
| 3-column | `cols-3`, `split-3` | `width:320px` | 340px |

> These are the widths `marp-lint.py` enforces (`DIAGRAM_OVERFLOW_WIDTH`).
> The canonical mapping lives in `scripts/diagrams/layout_spec.py::CLASS_TO_LAYOUT`.

### Supported Template Layouts

Each shipped template declares the layouts it is verified against. Anything not
listed fails layout validation, so check this table before choosing a layout:

```bash
python scripts/diagrams/check-templates.py            # all templates, all engines
python scripts/diagrams/check-templates.py --skip-mermaid   # offline (no npx)
```

| Template | `full` | `col2` | `asym` | `col3` |
|---|:--:|:--:|:--:|:--:|
| `flowchart-linear.mmd` | ✅ | | | |
| `flowchart-col2.mmd` | ✅ | ✅ | ✅ | |
| `sequence-api.mmd` | ✅ | | | |
| `sequence-api-col2.mmd` | ✅ | | ✅ | |
| `architecture-3tier.mmd` | ✅ | | | |
| `architecture-3tier-col2.mmd` | ✅ | ✅ | ✅ | ✅ |
| `state-machine.mmd` | ✅ | | | |
| `state-machine-col2.mmd` | ✅ | ✅ | ✅ | ✅ |
| `system-architecture.drawio` | ✅ | | | |
| `cloud-infrastructure.drawio` | ✅ | | | |
| `charts/revenue-pie.json` | ✅ | ✅ | ✅ | ✅ |
| `charts/revenue-donut.json` | ✅ | ✅ | ✅ | ✅ |
| `charts/sales-bar.json` | ✅ | ✅ | ✅ | ✅ |
| `charts/quarterly-line.json` | ✅ | ✅ | ✅ | ✅ |
| `charts/channel-stacked-bar.json` | ✅ | ✅ | ✅ | ✅ |
| `concepts/team-pyramid.json` | ✅ | ✅ | ✅ | ✅ |
| `concepts/improvement-cycle.json` | ✅ | ✅ | ✅ | ✅ |
| `concepts/team-radial.json` | ✅ | | | |
| `concepts/team-radial-compact.json` | ✅ | ✅ | ✅ | ✅ |
| `concepts/sales-funnel.json` | ✅ | ✅ | ✅ | ✅ |
| `organization/team-org-chart.json` | ✅ | ✅ | ✅ | ✅ |

> SSoT: `scripts/diagrams/check-templates.py::ALLOWED_LAYOUTS` is the authority.
> This table mirrors it. Every template works at `full`, so the default `width:1050px` embed is always safe.

### Lint Integration

`marp-lint.py` checks diagram embeddings automatically:

- **`DIAGRAM_MISSING_WIDTH`** (WARNING) — Diagram SVG embedded without `width:NNNpx`.
- **`DIAGRAM_OVERFLOW_WIDTH`** (ERROR) — Width exceeds the safe maximum for the current layout.
- **`DIAGRAM_ON_CENTERED_LAYOUT`** (WARNING) — Diagram on a cover/key-message slide where alignment may break.

### Available Templates

| Template | Engine | Description |
|---|---|---|
| `flowchart-linear.mmd` | Mermaid | Left-to-right linear process flow |
| `sequence-api.mmd` | Mermaid | REST API auth + order sequence |
| `sequence-api-col2.mmd` | Mermaid | Compact 3-party sequence for asym/full |
| `architecture-3tier.mmd` | Mermaid | Classic 3-tier web architecture |
| `architecture-3tier-col2.mmd` | Mermaid | Compact vertical 3-tier for all layouts |
| `flowchart-col2.mmd` | Mermaid | 2-column-safe compact flowchart |
| `state-machine.mmd` | Mermaid | State transition diagram |
| `state-machine-col2.mmd` | Mermaid | Compact vertical state flow for all layouts |
| `system-architecture.drawio` | draw.io | 3-layer system architecture with swimlanes |
| `cloud-infrastructure.drawio` | draw.io | Cloud VPC/subnet/ALB infrastructure |
| `charts/revenue-pie.json` | JSON SVG | Pie chart with themed legend |
| `charts/revenue-donut.json` | JSON SVG | Donut chart with center label |
| `charts/sales-bar.json` | JSON SVG | Vertical bar chart with values |
| `charts/quarterly-line.json` | JSON SVG | Multi-series line chart with legend |
| `charts/channel-stacked-bar.json` | JSON SVG | Stacked bar chart with legend |
| `concepts/team-pyramid.json` | JSON SVG | Layered pyramid |
| `concepts/improvement-cycle.json` | JSON SVG | Circular improvement process |
| `concepts/team-radial.json` | JSON SVG | Radial concept map (full only; dense) |
| `concepts/team-radial-compact.json` | JSON SVG | Compact radial for narrow columns |
| `concepts/sales-funnel.json` | JSON SVG | Sales/conversion funnel |
| `organization/team-org-chart.json` | JSON SVG | Hierarchical organization chart |

> Template registry is verified by `python scripts/diagrams/check-catalog-sync.py` (templates on disk vs. this table vs. `template-catalog.md`), and the supported-layout column by `python scripts/diagrams/check-templates.py`. The templates themselves ship inside the `marp-diagram-creator` skill at `vendor/templates/` (development source: `scripts/diagrams/templates/`).

