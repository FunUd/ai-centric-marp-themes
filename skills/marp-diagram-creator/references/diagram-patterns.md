# Slide Diagram Canvas Spec & Pattern Catalog (Diagram Patterns & Specifications)

This document is the strict design spec for placing diagrams (Mermaid / draw.io) on Marp slides
while **absolutely preventing breakage (overflow, shrunken illegible text, layout collapse)**.

---

## 1. Slide Canvas Spec (Canvas Contract)

The standard Marp slide size is **1280px × 720px** (16:9).
Excluding padding and the space taken by the slide title (H1) and footer, the safe diagram
placement area is standardized as follows.

| Layout | Max Width | Max Height | Recommended Aspect | Max Chars per Node | Recommended Nodes |
|---|---|---|---|---|---|
| **Full Slide (single full-width column)** | **1120px** | **460px** | **2.2:1 – 2.5:1 (landscape)** | Japanese: max 20 chars | 3–6 nodes (horizontal) |
| **2-Column (one side of a split)** | **520px** | **460px** | **1.1:1 – 1.2:1 (square/portrait)** | Japanese: max 15 chars | 3–5 nodes (vertical) |
| **Split-Asym (65% main pane)** | **710px** | **460px** | **1.5:1 – 1.6:1 (standard landscape)** | Japanese: max 18 chars | 4–6 nodes |
| **3-Column (one pane of three)** | **340px** | **460px** | **0.7:1 – 0.8:1 (portrait)** | Japanese: max 10 chars | 2–3 nodes (vertical) |

> ⚠️ **Absolute prohibitions (Anti-Patterns)**:
> - Creating diagrams taller than `460px` (the leading cause of bottom overflow).
> - Placing tall/portrait diagrams (height far exceeding width) on a Full Slide (they get shrunk to 460px height and text becomes unreadably small).
> - Stuffing long text (25+ chars) into a single node (breaks out of borders or collapses via extreme auto-wrapping).

> ※ **Canvas ratio control**: pin the SVG canvas ratio with `--aspect 2.4` (or `16:9`) on
> `render-slide-diagram.py`, a JSON source field `"aspect": 2.4` (derives `height` from `width`;
> never combine with `height`), or a Mermaid `%% aspect: 16:9` comment directive. JSON diagrams
> reflow to the ratio; Mermaid/draw.io canvases are *padded* — content is centered, never scaled
> or cropped — and padding beyond the layout's hard limits fails with the feasible range.
> `validate-slide-diagram.py` warns when the final ratio falls outside the recommended band.

---

## 2. Slide Placement Patterns and Syntax

When embedding a generated SVG file (`assets/diagram.svg`) into slide Markdown, always use the following syntax.

### Pattern A: Full Slide Centered (default)
The standard pattern for showing a process or architecture across the whole slide.

```markdown
# System Architecture Overview

![width:1050px center](./assets/system-arch.svg)
```
- ※ Specify `width:` to fit the slide width. Height scales automatically.
- ※ If vertical space is tight, specify `height:420px center` instead. **Never specify both at once (distorts the aspect ratio).**

---

### Pattern B: 2-Column Contrast (diagram + bullet notes)
The most frequently used real-world pattern: diagram on the left, key bullets on the right.

```markdown
<!-- _class: cols-2 -->

# Auth Flow

<div class="columns">
<div class="col v-center text-center">

![width:500px center](./assets/auth-flow-col2.svg)

</div>
<div class="col v-center">

### Points

- **Stateless auth with JWT**
  - No session DB access needed
- **Automatic refresh-token rotation**
  - 7-day expiry, rotation in operation
- **Role-Based Access Control**
  - Separated admin/standard-user privileges

</div>
</div>
```

---

### Pattern C: Split-Asym (diagram 65% : notes 35%)
Show a slightly larger diagram while supplementing key points in a sidebar.

```markdown
<!-- _class: split-asym -->

# Cloud Infrastructure

<div class="columns">
<div class="col v-center text-center">

![width:680px center](./assets/cloud-infra.svg)

</div>
<div class="col v-center">

### Infra Requirements

- Multi-AZ redundancy
- Autoscaling (2–10 nodes)
- Encrypted traffic (TLS 1.3)

</div>
</div>
```

---

## 3. Diagram-Type to Engine Decision Criteria

> Canonical: this table is the source of truth for engine selection. The summary in `SKILL.md` §2 must stay consistent with it.
> Apply top-down: ① numeric data → JSON SVG / ② text-only with ≤5 items → CSS Native / ③ fixed-precision layout → draw.io / ④ everything else → Mermaid.

| Diagram Type | Recommended Engine | Rationale |
|---|---|---|
| **Numeric data visuals** (bar/line/stacked, composition, pyramid, cycle, org, radial, funnel) | **JSON SVG** | Deterministic slide-safe geometry with structural validation. |
| **Text-only with ≤5 items** (steps, milestones, checklists) | **CSS Native** (`steps`+`arrows` / `timeline` / `checklist` / `timetable`) | 100% theme match, no images needed. |
| **2-axis matrix / quadrant (text-only, ≤5 items)** | **CSS Native** (`grid-quadrant`+`axes`) | 100% theme match, no images needed. Use draw.io only when coordinate precision is required. |
| **Flowchart (horizontal process)** | **Mermaid (`graph LR`)** | Simplest and fastest for linear process steps. |
| **Flowchart (vertical / branching)** | **Mermaid (`graph TD`)** / **draw.io** for complex cases | draw.io gives perfect control over arrow crossings when branching is heavy. |
| **Sequence diagram (API/messages)** | **Mermaid (`sequenceDiagram`)** | Best for 3–4 participants with 5–6 request/response messages. |
| **3-tier architecture** | **Mermaid / draw.io** | Mermaid for simple interactions, draw.io for detailed layouts. |
| **Cloud infra / composite diagrams** | **draw.io** | The only choice for AWS/GCP/Azure icons and complex boundaries/network zones. |
| **State machine** | **Mermaid (`stateDiagram-v2`)** | Extremely fast for 4–5 state transitions. |
