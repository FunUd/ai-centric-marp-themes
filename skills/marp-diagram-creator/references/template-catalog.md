# Slide Diagram Template Catalog

This catalog lists the preset templates available for immediate use when creating slides, with their characteristics and applicable scenes.

> **Where the templates live.** A copy ships inside this skill at
> `vendor/templates/`, so the paths below work with the skill installed anywhere.
> In a clone of `ai-centric-marp-themes` the same files are at
> `scripts/diagrams/templates/`, which is the development source; the two are
> kept byte-identical by `python scripts/sync-skill-vendor.py --check`.
>
> **Maintenance** (repository only — these scripts are not vendored):
> this catalog, the Available Templates table in `README.md`, and the on-disk
> templates are sync-checked via `python scripts/diagrams/check-catalog-sync.py`.
> When adding a new template, follow `scripts/diagrams/ADD_NEW_DIAGRAM_TYPE.md` inside
> a checkout of `ai-centric-marp-themes`,
> then run `python scripts/sync-skill-vendor.py` to refresh the vendored copy.
>
> The **Verified Layouts** column below is enforced, not advisory: every template is
> rendered and canvas-validated at each listed layout by
> `python scripts/diagrams/check-templates.py`. A template that does not fit a layout
> is not listed there and will fail validation if you try.

---

## 1. Mermaid Templates (`vendor/templates/mermaid/`)

| Filename | Type | Verified Layouts | Purpose |
|---|---|---|---|
| `flowchart-linear.mmd` | Flowchart | Full | Standard left-to-right business/process flow. Pinned to `%% aspect: 2.4` (embeds at 1050x437). |
| `flowchart-col2.mmd` | Flowchart | Full, Col2, Asym | Top-to-bottom flow with a decision branch. Compact enough for half-width columns. |
| `sequence-api.mmd` | Sequence diagram | Full | Request/response round-trips between client, API Gateway, auth, and DB. With autonumber. |
| `architecture-3tier.mmd` | Architecture diagram | Full | Classic 3-tier web architecture (presentation / application / data) with service interactions. |
| `state-machine.mmd` | State machine | Full | State transitions such as draft, in review, approved, returned, and published. Laid out left-to-right and padded to `%% aspect: 2.4`. Ends at publish; the archive state was omitted for slide fit. |

---

## 2. draw.io Templates (`vendor/templates/drawio/`)

| Filename | Verified Layouts | Purpose | Re-editable in VS Code |
|---|---|---|---|
| `system-architecture.drawio` | Full | Slide-optimized 3-layer system diagram (client / API / data layers stacked vertically). | Yes (`hediet.vscode-drawio`) |
| `cloud-infrastructure.drawio` | Full | Cloud infrastructure covering VPC, DMZ/public subnets, private container clusters, RDS/Redis. | Yes (`hediet.vscode-drawio`) |

> Both are wide swimlane layouts: they only fit the full slide width.

## 3. JSON SVG Templates (`vendor/templates/`)

| Filename | Type | Verified Layouts | Purpose |
|---|---|---|---|
| `charts/revenue-pie.json` | Pie chart | Full | Comparing composition ratios. |
| `charts/revenue-donut.json` | Donut chart | Full, Col2, Asym, Col3 | Composition ratios with a center metric. |
| `charts/sales-bar.json` | Bar chart | Full, Col2, Asym, Col3 | Comparing quantities across time periods or categories. |
| `charts/quarterly-line.json` | Line chart | Full, Col2, Asym, Col3 | Multi-series trend comparison (with legend). |
| `charts/channel-stacked-bar.json` | Stacked bar chart | Full, Col2, Asym, Col3 | Comparing breakdown composition over time. |
| `concepts/team-pyramid.json` | Pyramid | Full, Col2, Asym, Col3 | Stacked layers such as maturity or priority. |
| `concepts/improvement-cycle.json` | Cycle | Full, Col2, Asym, Col3 | Continuous improvement and iterative processes. |
| `concepts/team-radial.json` | Radial concept map | Full | Relationships between a central concept and categories. |
| `concepts/sales-funnel.json` | Funnel | Full, Col2, Asym, Col3 | Sales funnels and conversion narrowing. |
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
