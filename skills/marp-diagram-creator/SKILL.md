---
name: marp-diagram-creator
description: Activate this skill when creating, embedding, or updating diagrams (flowcharts, architecture, sequence diagrams, state machines, comparison matrices) for Marp presentation slides using Mermaid or draw.io. Enforces strict slide canvas boundaries to prevent layout breakage and overflow.
---

# Marp Diagram Creator

This skill guides AI agents in generating and embedding high-quality, production-ready diagrams into Marp presentations using **Mermaid** and **draw.io**.

All diagrams are strictly constrained to slide canvas bounds (`1120x460` full, `520x460` 2-col, `710x460` asym, `340x460` 3-col) and automatically synchronized with the presentation's active theme.

---

## 1. When to Use This Skill

Activate this skill when the user asks to:
- "Add a diagram to the slide", "draw a flowchart", "visualize the architecture"
- "Create a sequence diagram for the API call", "make a 2-column comparison matrix"
- "Embed a Mermaid or draw.io diagram into the presentation"
- "Show the system components or data flow visually"

---

## 2. Choosing the Engine (Mermaid vs draw.io vs JSON SVG vs CSS Native)

Select the most suitable engine based on diagram characteristics.
The full decision table lives in `references/diagram-patterns.md` §3 — the summary below must stay consistent with it:

| Engine | Best For | Pros |
|---|---|---|
| **Mermaid** | Standard flowcharts, API sequence diagrams, 3-tier architectures, simple state machines | Fast code generation, minimal token overhead, version-controllable text DSL |
| **draw.io** | Cloud infrastructure (VPC/Subnet/ALB), complex multi-container systems, fixed-precision layouts | Absolute layout precision, zero unexpected auto-wrapping, editable via VS Code extension (`hediet.vscode-drawio`) |
| **JSON SVG** | Numeric data visuals: bar/line/stacked-bar charts, pie/donut charts, pyramids, cycles, org charts, radial concepts, funnels | Deterministic slide-safe geometry and structured validation |
| **CSS Native** | Text-only patterns with ≤5 items: timelines, steps, 2-axis matrices, checklists | 100% theme match, no images needed |

Decision tree (apply top-down):

1. **Numeric data to visualize?** (shares, counts, conversions) → **JSON SVG**
2. **Text-only and ≤5 items?** (steps, milestones, 2-axis matrix, checklist) → **CSS Native** (`steps`+`arrows`, `timeline`, `grid-quadrant`+`axes`)
3. **Fixed-precision layout required?** (VPC/subnets, swimlanes, exact coordinates) → **draw.io**
4. **Otherwise** (flows, sequences, state machines, simple architecture) → **Mermaid**

Quick ref: data-viz → JSON SVG; process/steps/matrix/timeline (≤5 items) → CSS Native; complex arch → draw.io; state machine → Mermaid.

---

## 3. Step-by-Step Generation Workflow

### Step 1: Identify Context & Constraints
1. **Target Slide Theme**: Identify the theme (`azure-clarity`, `crimson-clarity`, `prism-edge`, `nebula-glass`, `warm-sunnyday`, `slate-minimal`).
2. **Slide Layout** (canonical values: `vendor/layout_spec.py`):
   - `full`: Full-width diagram (`max 1120px × 460px`, aspect ratio ~2.3:1)
   - `col2`: 2-column layout (`max 520px × 460px`, aspect ratio ~1.15:1)
   - `asym`: Split asymmetric layout (`max 710px × 460px`, aspect ratio ~1.55:1)
   - `col3`: 3-column layout (`max 340px × 460px`, aspect ratio ~0.75:1)

### Step 2: Generate the Diagram File

#### Locating the Engine

The diagram engine ships **inside this skill**, under `vendor/`, so the skill
works wherever it is installed. Resolve it once per session:

```bash
ENGINE=$(python <skill-dir>/scripts/print-engine-path.py)
```

```powershell
# Windows PowerShell equivalent (bash `$(...)`, `head`, and `ls` do not work in pwsh)
$ENGINE = python <skill-dir>/scripts/print-engine-path.py
```

`<skill-dir>` is the folder containing this `SKILL.md`:

| Situation | `<skill-dir>` |
|---|---|
| Working in a clone of `ai-centric-marp-themes` | `skills/marp-diagram-creator` |
| Installed for Claude Code / Cursor / Windsurf | `~/.claude/skills/marp-diagram-creator` (or the agent's equivalent) |
| Synced by `scripts/sync-skills.py` | `.claude/skills/marp-diagram-creator` inside your deck repo |

All commands below use `<ENGINE>` for that resolved path. If you prefer to type
paths out, the in-repo form is
`python skills/marp-diagram-creator/vendor/render-slide-diagram.py …`.

#### Option A: Quick Generation via CLI (Recommended)
Use `<ENGINE>/render-slide-diagram.py` to compile Mermaid, draw.io or JSON into a themed SVG (`<ENGINE>` already points at `vendor/`):

```bash
# From Mermaid code string
python <ENGINE>/render-slide-diagram.py --code "flowchart LR; A[Intake] --> B[Process]; B --> C[Done]" -o slides/<deck-name>/assets/flow.svg --theme azure-clarity --layout full

# From Mermaid template / .mmd file
python <ENGINE>/render-slide-diagram.py -i <ENGINE>/templates/mermaid/sequence-api.mmd -o slides/<deck-name>/assets/api-sequence.svg --theme prism-edge --layout full

# From draw.io template / .drawio file
python <ENGINE>/render-slide-diagram.py -i <ENGINE>/templates/drawio/system-architecture.drawio -o slides/<deck-name>/assets/system-arch.svg --theme nebula-glass --layout full

# From a JSON chart/concept template
python <ENGINE>/render-slide-diagram.py -i <ENGINE>/templates/charts/revenue-pie.json -o slides/<deck-name>/assets/revenue-pie.svg --theme azure-clarity --layout full
```

> Inside this repository the equivalent is
> `python skills/marp-diagram-creator/vendor/render-slide-diagram.py …`.
> Both are the same file; `scripts/diagrams/` is the development source and is
> kept byte-identical by `python scripts/sync-skill-vendor.py --check`.

JSON diagrams require `type` and type-specific data. Supported types are `pie`, `donut`, `pyramid`, `cycle`, `org-chart`, `radial`, `funnel`, `bar`, `line`, and `stacked-bar` (registry: `vendor/diagram_models.py::DIAGRAM_TYPES`; `scripts/diagrams/tests/test_diagram_registry.py` enforces it); `theme`, `layout`, `width`, `height`, and `aspect` are optional. `aspect` (canvas width/height ratio, e.g. `"aspect": 2.4`) derives `height` from `width` — never combine it with an explicit `height`. Every engine also accepts `--aspect 2.4` (or `--aspect 16:9`), and Mermaid sources may declare `%% aspect: 16:9`; for Mermaid/draw.io the finished canvas is padded to the target ratio (content centered, never scaled) as long as it fits the layout's feasible range.

Timelines, step flows, and 2-axis matrices are not JSON diagram types. Use the theme's `timeline` / `steps` (+ `arrows`) / `grid-quadrant` (+ `axes`) slide classes instead.

#### JSON SVG quality rules

- Treat `full`, `col2`, `asym`, and `col3` as geometry profiles, not only output widths. Let the renderer choose the default dimensions unless the diagram has a documented custom aspect ratio (set it via JSON `"aspect"`, `--aspect 2.4|16:9`, or a Mermaid `%% aspect:` directive — see `references/diagram-patterns.md` §1).
- Do not place seven detailed diagrams into one presentation slide. Use a catalog slide only for comparison; use separate slides when labels, timelines, hierarchy, or child nodes must be readable.
- Keep one visual title: either use the JSON `title` or the surrounding slide/card heading. Do not duplicate long titles inside and outside the SVG.
- Prefer short labels. The renderer wraps long labels, but wrapping is a rescue mechanism, not a substitute for concise content. Use Japanese labels of roughly 6-12 characters per node and move explanations into `description` or presenter notes.
- Generate the SVG, run `validate-slide-diagram.py --strict`, and inspect a rendered Marp screenshot before reporting completion. A passing XML/bounds check is not visual approval.
- For compact layouts, generate with the target layout (`col2`/`col3`) rather than generating a `full` SVG and shrinking it in Markdown.
- Cartesian charts (`bar`/`line`/`stacked-bar`): keep categories within the readable budget — `full` ≤8, `asym` ≤6, `col2` ≤5, `col3` ≤4. Values are non-negative in v1 (negatives are rejected with a forward-compatible message).
- If a diagram has more than six visible labels, prefer a legend or a second slide over reducing the font size.

#### Option B: Customize from Template
Copy a template from `<ENGINE>/templates/` to `slides/<deck-name>/assets/`, customize the node labels and connections, then run `render-slide-diagram.py` to produce the final SVG.

To add a new JSON diagram type, follow `scripts/diagrams/ADD_NEW_DIAGRAM_TYPE.md` inside
a checkout of `ai-centric-marp-themes` (it documents the renderer internals, which are not vendored).

#### draw.io Connector Routing

For draw.io architecture diagrams, connectors must be routed around node rectangles. Do not rely on
`edgeStyle=orthogonalEdgeStyle` alone: the slide renderer resolves edges independently from the
draw.io editor. Use explicit `<Array as="points">` waypoints for intentional routes, and use
`exitX`/`exitY` plus `entryX`/`entryY` when a connector must leave or enter from a specific side.
Connectors without waypoints are automatically routed around non-container vertices, and the
validator fails when a route crosses an intermediate node.

### Step 3: Automated Validation (Crucial for Anti-Breakage)
Every generated SVG is automatically checked against slide boundaries. You can also run the validator manually:

```bash
python <ENGINE>/validate-slide-diagram.py slides/<deck-name>/assets/my-diagram.svg --layout full
```

The `check-*.py` and `sync-*.py` scripts are **not** vendored: they operate on the
repository (reading `README.md`, `themes/*.css`, the test suite) and are
meaningless outside it. From a checkout of `ai-centric-marp-themes` you can
validate every template at the layouts it supports:

```bash
python scripts/diagrams/check-templates.py            # all engines, needs Node
python scripts/diagrams/check-templates.py --skip-mermaid   # offline
```

> ⚠️ **Zero Breakage Rule**:
> - Height must NOT exceed `460px`.
> - Do not place tall/vertical diagrams on a `full` layout slide without multi-row arrangement (avoids text shrinking).
> - Node text must not exceed 20 characters per box (use line breaks `\n` or `<br/>`).

### Step 4: Embed in Marp Slide

#### Pattern 1: Full Slide
```markdown
# Process Flow Overview

![width:1050px center](./assets/flow.svg)
```

Recommended embed widths by layout (`layout_spec.py::EMBED_WIDTH`; never exceed the `CANVAS_MAX` gate enforced by `marp-lint.py`):

| Layout | Example `width:` | Hard max |
|---|---|---|
| Full slide | `width:1050px` | 1120px |
| 2-column (`cols-2`, `split-2`, `split-glass`, `glass-card-layout`) | `width:500px` | 520px |
| Asymmetric (`split-asym`, `split-asym-reverse`) | `width:680px` | 710px |
| 3-column (`cols-3`, `split-3`) | `width:320px` | 340px |

#### Pattern 2: 2-Column (Diagram + Key Points)
```markdown
<!-- _class: cols-2 -->

# System Architecture and Features

<div class="columns">
<div class="col v-center text-center">

![width:500px center](./assets/architecture.svg)

</div>
<div class="col v-center">

### Key Architecture Decisions

- **Loosely coupled microservices**
- **High throughput via read/write splitting**
- **Automatic failover on fault detection**

</div>
</div>
```

---

## 4. Visual Quality Checklist

Before completing your task:
1. [ ] **Theme Cohesion**: Does the diagram use the slide deck's color palette? (Dark background and neon accents for Nebula Glass, crisp blues for Azure Clarity, etc.)
2. [ ] **No Text Truncation**: Are all text labels readable without clipping or overlapping?
3. [ ] **Canvas Fit**: Does the image fit comfortably within the slide without pushing the footer down or overlapping headers?
4. [ ] **Visual Inspection**: If Playwright / Vision is active, check the rendered screenshot using `marp-diagnostics.py`.

### Art Direction (anti-cheap rules)
- **60-30-10**: base (pale/surface) 60%, primary 30%, accent/status 10%. Never place two saturated hues side-by-side in pies.
- **One accent only**: a single primary node per diagram; others stay pale/surface.
- **Edges**: theme line color, 1.5px+. Black arrowheads (`#0b0b0b`) and gray `rgba(185,185,185,1)` shadows are defects — the postprocessor now strips them.
- **Banned**: rainbow fills, 3D gradients, <12px labels, unbroken 20+ char node text.
