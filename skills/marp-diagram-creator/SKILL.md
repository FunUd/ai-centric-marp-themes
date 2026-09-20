---
name: marp-diagram-creator
description: Activate this skill when creating, embedding, or updating diagrams (flowcharts, architecture, sequence diagrams, state machines, comparison matrices) for Marp presentation slides using Mermaid or draw.io. Enforces strict slide canvas boundaries to prevent layout breakage and overflow.
---

# Marp Diagram Creator

This skill guides AI agents in generating and embedding high-quality, production-ready diagrams into Marp presentations using **Mermaid** and **draw.io**.

All diagrams are strictly constrained to slide canvas bounds (`1120x460` for full slide, `520x460` for 2-column) and automatically synchronized with the presentation's active theme.

---

## 1. When to Use This Skill

Activate this skill when the user asks to:
- "Add a diagram to the slide", "draw a flowchart", "visualize the architecture"
- "Create a sequence diagram for the API call", "make a 2-column comparison matrix"
- "Embed a Mermaid or draw.io diagram into the presentation"
- "Show the system components or data flow visually"

---

## 2. Choosing the Engine (Mermaid vs draw.io)

Select the most suitable engine based on diagram characteristics:

| Engine | Best For | Pros |
|---|---|---|
| **Mermaid** | Standard flowcharts, API sequence diagrams, 3-tier architectures, simple state machines | Fast code generation, minimal token overhead, version-controllable text DSL |
| **draw.io** | Cloud infrastructure (VPC/Subnet/ALB), complex multi-container systems, 2-axis / 4-quadrant matrices | Absolute layout precision, zero unexpected auto-wrapping, editable via VS Code extension (`hediet.vscode-drawio`) |
| **JSON SVG** | Pie/donut charts, pyramids, cycles, timelines, org charts, radial concepts | Deterministic slide-safe geometry and structured validation |

---

## 3. Step-by-Step Generation Workflow

### Step 1: Identify Context & Constraints
1. **Target Slide Theme**: Identify the theme (`azure-clarity`, `crimson-clarity`, `prism-edge`, `nebula-glass`, `warm-sunnyday`, `slate-minimal`).
2. **Slide Layout**:
   - `full`: Full-width diagram (`max 1120px × 460px`, aspect ratio ~2.3:1)
   - `col2`: 2-column layout (`max 520px × 460px`, aspect ratio ~1.15:1)
   - `asym`: Split asymmetric layout (`max 710px × 460px`, aspect ratio ~1.55:1)

### Step 2: Generate the Diagram File

#### Option A: Quick Generation via CLI (Recommended)
Use `scripts/diagrams/render-slide-diagram.py` to compile Mermaid or draw.io into a themed SVG:

```powershell
# From Mermaid code string
python scripts/diagrams/render-slide-diagram.py --code "flowchart LR; A[受付] --> B[処理]; B --> C[完了]" -o slides/<deck-name>/assets/flow.svg --theme azure-clarity --layout full

# From Mermaid template / .mmd file
python scripts/diagrams/render-slide-diagram.py -i scripts/diagrams/templates/mermaid/sequence-api.mmd -o slides/<deck-name>/assets/api-sequence.svg --theme prism-edge --layout full

# From draw.io template / .drawio file
python scripts/diagrams/render-slide-diagram.py -i scripts/diagrams/templates/drawio/system-architecture.drawio -o slides/<deck-name>/assets/system-arch.svg --theme nebula-glass --layout full

# From a JSON chart/concept template
python scripts/diagrams/render-slide-diagram.py -i scripts/diagrams/templates/charts/revenue-pie.json -o slides/<deck-name>/assets/revenue-pie.svg --theme azure-clarity --layout full
```

JSON diagrams require `type` and type-specific data. Supported types are `pie`, `donut`, `pyramid`, `cycle`, `timeline`, `org-chart`, and `radial`; `theme`, `layout`, `width`, and `height` are optional.

#### Option B: Customize from Template
Copy a template from `scripts/diagrams/templates/` to `slides/<deck-name>/assets/`, customize the node labels and connections, then run `render-slide-diagram.py` to produce the final SVG.

#### draw.io Connector Routing

For draw.io architecture diagrams, connectors must be routed around node rectangles. Do not rely on
`edgeStyle=orthogonalEdgeStyle` alone: the slide renderer resolves edges independently from the
draw.io editor. Use explicit `<Array as="points">` waypoints for intentional routes, and use
`exitX`/`exitY` plus `entryX`/`entryY` when a connector must leave or enter from a specific side.
Connectors without waypoints are automatically routed around non-container vertices, and the
validator fails when a route crosses an intermediate node.

### Step 3: Automated Validation (Crucial for Anti-Breakage)
Every generated SVG is automatically checked against slide boundaries. You can also run the validator manually:

```powershell
python scripts/diagrams/validate-slide-diagram.py slides/<deck-name>/assets/my-diagram.svg --layout full
```

> ⚠️ **Zero Breakage Rule**:
> - Height must NOT exceed `460px`.
> - Do not place tall/vertical diagrams on a `full` layout slide without multi-row arrangement (avoids text shrinking).
> - Node text must not exceed 20 characters per box (use line breaks `\n` or `<br/>`).

### Step 4: Embed in Marp Slide

#### Pattern 1: Full Slide
```markdown
# 処理フロー概要

![width:1050px center](./assets/flow.svg)
```

#### Pattern 2: 2-Column (Diagram + Key Points)
```markdown
<!-- _class: cols-2 -->

# システム構成と特徴

<div class="columns">
<div class="col v-center text-center">

![width:500px center](./assets/architecture.svg)

</div>
<div class="col v-center">

### 主なアーキテクチャ設計

- **疎結合なマイクロサービス構成**
- **Read/Write分離による高スループット**
- **障害検知時の自動フェイルオーバー**

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
