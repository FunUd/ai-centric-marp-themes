# Slide Diagram Template Catalog

This catalog lists the preset templates available for immediate use when creating slides, with their characteristics and applicable scenes.

> **Where the templates live.** A copy ships inside this skill at
> `vendor/templates/`, so the paths below work with the skill installed anywhere.
> In a clone of `ai-centric-marp-themes` the same files are at
> `scripts/diagrams/templates/`, which is the development source; the two are
> kept byte-identical by `python scripts/sync-skill-vendor.py --check`.
>
> **Maintenance** (repository only — these scripts are not vendored):
> this catalog, the Available Templates table in `docs/diagrams.md`, and the on-disk
> templates are sync-checked via `python scripts/diagrams/check-catalog-sync.py`.
> When adding a new template, follow `scripts/diagrams/ADD_NEW_DIAGRAM_TYPE.md` inside
> a checkout of `ai-centric-marp-themes`,
> then run `python scripts/sync-skill-vendor.py` to refresh the vendored copy.
>
> The **Verified Layouts** column below is enforced, not advisory: every template is
> rendered and canvas-validated at each listed layout by
> `python scripts/diagrams/check-templates.py`, and the column contents are
> cross-checked against that authority by
> `python scripts/diagrams/check-catalog-sync.py`. A template that does not fit a layout
> is not listed there and will fail validation if you try.

---

## 1. Mermaid Templates (`vendor/templates/mermaid/`)

| Filename | Type | Verified Layouts | Embed | Purpose |
|---|---|---|---|---|
| `flowchart-linear.mmd` | Flowchart | Full | 1050px | Standard left-to-right business/process flow. Pinned to `%% aspect: 2.4` (embeds at 1050x437). |
| `flowchart-col2.mmd` | Flowchart | Full, Col2, Asym | 570px | Top-to-bottom flow with a decision branch. Compact enough for half-width columns. |
| `sequence-api.mmd` | Sequence diagram | Full | 950px | Request/response round-trips between client, API Gateway, auth, and DB. With autonumber. |
| `sequence-api-asym.mmd` | Sequence diagram | Full, Asym | 770px | Compact 3-party sequence (client/API/DB). Fits asym; too wide for col2 — use asym or full. |
| `architecture-3tier.mmd` | Architecture diagram | Full | 1050px | Classic 3-tier web architecture (presentation / application / data) with service interactions. |
| `architecture-3tier-col2.mmd` | Architecture diagram | Full, Col2, Asym, Col3 | 210px | Compact vertical 3-tier (Web/API-GW/logic/DB). Portrait canvas: embed narrow. |
| `state-machine.mmd` | State machine | Full | 1050px | State transitions such as draft, in review, approved, returned, and published. Laid out left-to-right and padded to `%% aspect: 2.4`. Ends at publish; the archive state was omitted for slide fit. |
| `state-machine-col2.mmd` | State machine | Full, Col2, Asym, Col3 | 460px | Compact vertical state flow (review/approved/returned). Fits all layouts. |
| `gantt-milestone.mmd` | Gantt | Full | 1050px | Project schedule, 3 sections / 7 tasks + 2 milestones. Pinned to `%% aspect: 2.4`. |
| `er-simple.mmd` | ER diagram | Full | 1050px | Entity relations with `direction LR`, 3 entities with attributes in one row. |
| `c4-context-compact.mmd` | Architecture diagram | Full, Asym | 900px | C4-style context: user + system + 3 externals. Too wide for col2. |
| `mindmap-compact.mmd` | Mind map | Full, Asym | 680px | Root + 3 branches, depth 2 max. Too wide for col2. |

---

## 2. draw.io Templates (`vendor/templates/drawio/`)

| Filename | Verified Layouts | Embed | Purpose | Re-editable in VS Code |
|---|---|---|---|---|
| `system-architecture.drawio` | Full | 1050px | Slide-optimized 3-layer system diagram (client / API / data layers stacked vertically). | Yes (`hediet.vscode-drawio`) |
| `cloud-infrastructure.drawio` | Full | 1050px | Cloud infrastructure covering VPC, DMZ/public subnets, private container clusters, RDS/Redis. | Yes (`hediet.vscode-drawio`) |

> Both are wide swimlane layouts: they only fit the full slide width.

## 3. JSON SVG Templates (`vendor/templates/`)

| Filename | Type | Verified Layouts | Purpose |
|---|---|---|---|
| `charts/revenue-pie.json` | Pie chart | Full, Col2, Asym, Col3 | Comparing composition ratios. Layout-agnostic (no hardcoded size). |
| `charts/revenue-donut.json` | Donut chart | Full, Col2, Asym, Col3 | Composition ratios with a center metric. |
| `charts/sales-bar.json` | Bar chart | Full, Col2, Asym, Col3 | Comparing quantities across time periods or categories. |
| `charts/quarterly-line.json` | Line chart | Full, Col2, Asym, Col3 | Multi-series trend comparison (with legend). |
| `charts/channel-stacked-bar.json` | Stacked bar chart | Full, Col2, Asym, Col3 | Comparing breakdown composition over time. |
| `charts/task-hbar.json` | Horizontal bar chart | Full, Col2, Asym, Col3 | Long-label quantities; horizontal bars with value labels. |
| `charts/channel-100-bar.json` | 100% stacked bar chart | Full, Col2, Asym, Col3 | Composition ratio per category (normalized to 100%). |
| `concepts/team-pyramid.json` | Pyramid | Full, Col2, Asym, Col3 | Stacked layers such as maturity or priority. |
| `concepts/improvement-cycle.json` | Cycle | Full, Col2, Asym, Col3 | Continuous improvement and iterative processes. |
| `concepts/team-radial.json` | Radial concept map | Full | Relationships between a central concept and categories (3 mains + 6 children; too dense for narrow). |
| `concepts/team-radial-compact.json` | Radial concept map | Full, Col2, Asym, Col3 | Compact radial (center + 3 nodes, no children) for narrow columns. |
| `concepts/sales-funnel.json` | Funnel | Full, Col2, Asym, Col3 | Sales funnels and conversion narrowing. |
| `concepts/tech-selection-matrix.json` | Comparison matrix | Full, Col2, Asym, Col3 | Scored 0-5 matrix (rows 2-6, columns 2-4) with row-winner rings and a 0-5 scale legend. |
| `organization/team-org-chart.json` | Org chart | Full, Col2, Asym, Col3 | Hierarchies and reporting lines. |

> On `col3`, prefer label-only funnel levels: value pills share a narrow gutter
> (the renderer prints a `[NOTE]` when it detects this).

---

## 4. Per-Theme Style Reference

| Theme | Mode | Primary | Accent | Character |
|---|---|---|---|---|
| **Azure Clarity** | Light | `#2C7BE5` (Blue) | `#1B4F72` (Navy) | Trustworthy mainstream business blue. Sharp with zero rounding. |
| **Crimson Clarity** | Light | `#D32F2F` (Red) | `#5C0000` (Dark Red) | Energetic, decisive corporate red. |
| **Prism Edge** | Light | `#4F46E5` (Indigo) | `#06B6D4` (Cyan) | Refined indigo & cyan. Modern geometric feel. |
| **Nebula Glass** | Dark | `#8B5CF6` (Violet) | `#22D3EE` (Cyan) | Dark background (`#040712`) with neon glow. Cyber feel. |
| **Warm Sunnyday** | Light | `#FF8C42` (Orange) | `#6E3B3B` (Brown) | Friendly warm orange. Soft design with large rounding. |
| **Slate Minimal** | Light | `#475569` (Slate) | `#111111` (Ink Black) | Minimalist monochrome stripped of decoration. |
