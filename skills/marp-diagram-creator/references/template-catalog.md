# Slide Diagram Template Catalog

This catalog lists the preset templates available for immediate use when creating slides, with their characteristics and applicable scenes.

> Maintenance: this catalog, the Available Templates table in `README.md`, and the on-disk templates
> are sync-checked via `python scripts/diagrams/check-catalog-sync.py`. When adding a new template,
> follow the procedure in `scripts/diagrams/ADD_NEW_DIAGRAM_TYPE.md`.

---

## 1. Mermaid Templates (`scripts/diagrams/templates/mermaid/`)

| Filename | Type | Recommended Layout | Purpose |
|---|---|---|---|
| `flowchart-linear.mmd` | Flowchart | Full | Standard left-to-right business/process flow. Icons and annotations can be added to each step. |
| `flowchart-col2.mmd` | Flowchart | 2-Column | Top-to-bottom flow with conditional branches, start/decision/end terminals. Best for vertical space. |
| `sequence-api.mmd` | Sequence diagram | Full | Request/response round-trips between client, API Gateway, auth, and DB. With autonumber. |
| `architecture-3tier.mmd` | Architecture diagram | Full | Classic 3-tier web architecture (presentation / application / data) with service interactions. |
| `state-machine.mmd` | State machine | 2-Column / Full | State transitions such as draft, in review, approved, returned, and published. |

---

## 2. draw.io Templates (`scripts/diagrams/templates/drawio/`)

| Filename | Recommended Layout | Purpose | Re-editable in VS Code |
|---|---|---|---|
| `system-architecture.drawio` | Full | Slide-optimized 3-layer system diagram (client / API / data layers stacked vertically). | Yes (`hediet.vscode-drawio`) |
| `cloud-infrastructure.drawio` | Full | Cloud infrastructure covering VPC, DMZ/public subnets, private container clusters, RDS/Redis. | Yes (`hediet.vscode-drawio`) |

## 3. JSON SVG Templates (`scripts/diagrams/templates/`)

| Filename | Type | Recommended Layout | Purpose |
|---|---|---|---|
| `charts/revenue-pie.json` | Pie chart | Full / Col2 | Comparing composition ratios. |
| `charts/revenue-donut.json` | Donut chart | Full / Col2 | Composition ratios with a center metric. |
| `charts/sales-bar.json` | Bar chart | Full / Col2 | Comparing quantities across time periods or categories. |
| `charts/quarterly-line.json` | Line chart | Full / Col2 | Multi-series trend comparison (with legend). |
| `charts/channel-stacked-bar.json` | Stacked bar chart | Full / Col2 | Comparing breakdown composition over time. |
| `concepts/team-pyramid.json` | Pyramid | Full / Col2 | Stacked layers such as maturity or priority. |
| `concepts/improvement-cycle.json` | Cycle | Full / Col2 | Continuous improvement and iterative processes. |
| `concepts/team-radial.json` | Radial concept map | Full / Col2 | Relationships between a central concept and categories. |
| `concepts/sales-funnel.json` | Funnel | Full / Col2 | Sales funnels and conversion narrowing. |
| `organization/team-org-chart.json` | Org chart | Full | Hierarchies and reporting lines. |

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
