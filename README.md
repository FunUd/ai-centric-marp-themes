# AI-Centric Marp Themes

A curated collection of **production-ready, AI-optimized Marp themes** designed for professional business presentations. Each theme offers a complete visual system — cover slides, multi-column layouts, callouts, timelines, grids, and more — all controllable via simple CSS classes in your Markdown.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Themes

| Theme | Style | Best For |
|-------|-------|----------|
| **Azure Clarity** | Clean, corporate blue | Business reports, project proposals, technical documentation |
| **Crimson Clarity** | Deep, energetic corporate red | High-impact proposals, strategic plans, executive summaries |
| **Prism Edge** | Bold indigo-cyan, modern edge | Keynotes, product launches, investor pitches |
| **Warm Sunnyday** | Warm orange, friendly rounded | Casual presentations, workshops, community talks |

### Azure Clarity

A calm, trustworthy blue theme built for clarity and readability.

- Professional card-based layouts with subtle borders
- TOC, agenda, comparison columns, 4-quadrant grids
- Steps, timelines, checklists, timetables, callouts
- Profile slides, key-message slides, dense information slides

```yaml
---
marp: true
theme: azure-clarity
paginate: true
---
```

<details>
<summary>📸 Slides Preview</summary>

![Azure Clarity Cover](assets/screenshots/azure-clarity-cover.png)
![Azure Clarity TOC](assets/screenshots/azure-clarity-toc.png)
![Azure Clarity Columns](assets/screenshots/azure-clarity-cols.png)
![Azure Clarity Grid](assets/screenshots/azure-clarity-grid.png)
![Azure Clarity Timeline](assets/screenshots/azure-clarity-timeline.png)
![Azure Clarity Callout](assets/screenshots/azure-clarity-callout.png)
![Azure Clarity Step](assets/screenshots/azure-clarity-step.png)

</details>

### Crimson Clarity

A strong, energetic red theme built for high-impact business presentations.

- Vibrant professional layouts with energetic accents
- TOC, agenda, comparison columns, 4-quadrant grids
- Steps, timelines, checklists, timetables, callouts
- Profile slides, key-message slides, dense information slides

```yaml
---
marp: true
theme: crimson-clarity
paginate: true
---
```

<details>
<summary>📸 Slides Preview</summary>

![Crimson Clarity Cover](assets/screenshots/crimson-clarity-cover.png)
![Crimson Clarity TOC](assets/screenshots/crimson-clarity-toc.png)
![Crimson Clarity Columns](assets/screenshots/crimson-clarity-cols.png)
![Crimson Clarity Grid](assets/screenshots/crimson-clarity-grid.png)
![Crimson Clarity Timeline](assets/screenshots/crimson-clarity-timeline.png)
![Crimson Clarity Callout](assets/screenshots/crimson-clarity-callout.png)
![Crimson Clarity Step](assets/screenshots/crimson-clarity-step.png)

</details>


### Prism Edge

A striking, modern theme with advanced cover designs and bold visuals.

- **Five cover variants**: Classic, Wave, Diagonal, Noir, Aurora
- Glass panels, gradient text, accent borders
- All Azure Clarity layouts inherited and enhanced

```yaml
---
marp: true
theme: prism-edge
paginate: true
---
```

<details>
<summary>📸 Slides Preview</summary>

![Prism Edge Cover Wave](assets/screenshots/prism-edge-cover-wave.png)
![Prism Edge Cover Diagonal](assets/screenshots/prism-edge-cover-diagonal.png)
![Prism Edge Cover Noir](assets/screenshots/prism-edge-cover-noir.png)
![Prism Edge Columns](assets/screenshots/prism-edge-cols.png)
![Prism Edge Grid](assets/screenshots/prism-edge-grid.png)
![Prism Edge gradnum](assets/screenshots/prism-edge-gradnum.png)
![Prism Edge statnum](assets/screenshots/prism-edge-statnum.png)

</details>

### Warm Sunnyday

A welcoming, warm-toned theme with rounded corners and soft aesthetics.

- Friendly orange palette with generous rounding
- Same rich layout system as Azure Clarity
- Ideal for less formal, engaging presentations

```yaml
---
marp: true
theme: warm-sunnyday
paginate: true
---
```

<details>
<summary>📸 Slides Preview</summary>

![Warm Sunnyday Cover](assets/screenshots/warm-sunnyday-cover.png)
![Warm Sunnyday Profile](assets/screenshots/warm-sunnyday-profile.png)
![Warm Sunnyday Columns](assets/screenshots/warm-sunnyday-cols.png)
![Warm Sunnyday Steps](assets/screenshots/warm-sunnyday-steps.png)
![Warm Sunnyday Callouts](assets/screenshots/warm-sunnyday-callouts.png)

</details>

---

## Quick Start

1. **Install [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)** or use the [Marp CLI](https://github.com/marp-team/marp-cli).

2. **Copy the theme CSS** you want from the `themes/` folder into your Marp workspace (or configure `themeSet` in `marp.config.js`).

3. **Reference the theme** in your slide deck's YAML frontmatter:

   ```yaml
   ---
   marp: true
   theme: azure-clarity
   paginate: true
   header: "My Presentation"
   footer: "© 2026"
   ---
   ```

4. **Use layout classes** to unlock rich designs without writing HTML:

   ```markdown
   <!-- _class: cover subtitle meta -->
   <!-- _paginate: false -->

   # Slide Title
   ## Subtitle here
   Author | Department | Date
   ```

---

## Layout Classes Overview

All themes share a unified class system. Apply any class via the Marp directive:

```markdown
<!-- _class: cols-2 -->
```

### Layouts

| Class | Description |
|-------|-------------|
| `cover` | Title slide with gradient background |
| `cover-wave` | *(Prism Edge)* Animated wave bottom |
| `cover-diagonal` | *(Prism Edge)* Sharp diagonal split |
| `cover-noir` | *(Prism Edge)* Dark dramatic background |
| `cover-aurora` | *(Prism Edge)* Soft aurora rotating gradient |
| `hero` | *(Prism Edge)* Single large centered message (H1 at 72px) |
| `title-only` | *(Prism Edge)* Minimal large left-aligned title (H1 at 64px) |
| `title-elegant` | *(Prism Edge)* Elegant centered title slide (adapts to subtitle presence) |
| `toc` | Two-column table of contents |
| `toc-focus` | Single-column large-number agenda |
| `cols-2` / `cols-3` | Card-style columns with background/border |
| `split-2` / `split-3` | Clean columns without card styling |
| `split-asym` / `split-asym-reverse` | *(Prism Edge)* Asymmetric 65:35 split columns |
| `grid-quadrant` | 2x2 matrix (SWOT, priority analysis) |
| `grid-sharp` | 2x2 border-only matrix (no backgrounds) |
| `steps` | Horizontal step cards with STEP badges |
| `timeline` | Vertical timeline with dates |
| `checklist` | Checkmark-styled bullet list |
| `timetable` | Styled schedule table |
| `key-message` | Full-slide centered message |
| `accent-left` | *(Prism Edge)* Gradient left-border accent on slide |
| `bg-grid` | *(Prism Edge)* Subtle grid pattern background |
| `bg-noise` | *(Prism Edge)* Soft noise texture background |
| `profile` | Self-introduction / team member profile |
| `dense` | High-density slide (18px base font) |
| `extra-dense` | Maximum density (15px base font) |

### Alignment & Utilities

| Class | Description |
|-------|-------------|
| `v-center` / `v-middle` / `v-top` / `v-bottom` | Vertical alignment |
| `text-center` / `text-left` / `text-right` | Horizontal alignment |
| `no-pagination` | Hide page number |
| `no-header` / `no-footer` | Hide header/footer |
| `with-header` | Extra top padding for header space |
| `pagination-left` | Move page number to bottom-left |
| `text-large` / `text-small` | 1.3em / 0.85em text size utility |

### Components

| Component | Usage |
|-----------|-------|
| **Callouts** | `<div class="callout blue">...</div>` (types: `blue`, `green`, `orange`, `red`) — independent alert blocks |
| **Badges** | `<span class="badge red">NEW</span>` (types: `blue`, `green`, `orange`, `red`) |
| **Glass Panel** | *(Prism Edge)* `<div class="glass-panel">...</div>` — frosted glass container |
| **Gradient Text** | *(Prism Edge)* `<span class="gradient-text">Text</span>` — indigo-to-cyan gradient fill |
| **Highlight Box** | *(Prism Edge)* `<div class="highlight-box">...</div>` — inline emphasis block for key insights |
| **Quote Large** | *(Prism Edge)* `<div class="quote-large">...</div>` — 32px italic editorial blockquote |
| **Stat Number** | *(Prism Edge)* `<span class="stat-number">42</span><span class="stat-label">Label</span>` |
| **Images** | `![center shadow width:600px](path)` or `![bg right:45% shadow](path)` |

---

## Project Structure

```
ai-centric-marp-themes/
├── themes/
│   ├── azure-clarity.css      # Corporate blue theme
│   ├── crimson-clarity.css       # Deep corporate red theme
│   ├── prism-edge.css         # Bold modern theme
│   └── warm-sunnyday.css      # Warm friendly theme
├── slides/
│   └── sample-slide/
│       ├── azure-clarity-sample.md
│       ├── prism-edge-sample.md
│       ├── warm-sunnyday-sample.md
│       └── assets/
├── skills/
│   ├── slide-content-designer/SKILL.md
│   ├── marp-slide-creator/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── marp-diagnostics.py        # Overflow / layout diagnostics helper
│   │       ├── marp-dom-extractor.py      # Playwright DOM metrics extractor for text-only AI review
│   │       ├── marp-lint.py               # Pre-render linter for structural mistakes
│   │       └── setup-slide-project.py     # Project scaffolding helper
│   ├── marp-svg-icon-placer/SKILL.md
│   ├── slide-expert-api-architecture/SKILL.md
│   ├── slide-expert-design-review/SKILL.md
│   ├── slide-expert-postmortem/SKILL.md
│   ├── slide-expert-progress-report/SKILL.md
│   ├── slide-expert-release-notes/SKILL.md
│   ├── slide-expert-requirements-specification/SKILL.md
│   ├── slide-expert-self-introduction/SKILL.md
│   ├── slide-expert-tech-selection/SKILL.md
│   ├── slide-expert-tech-sharing/SKILL.md
│   ├── theme-expert-azure-clarity/SKILL.md
│   ├── theme-expert-crimson-clarity/SKILL.md
│   ├── theme-expert-common/SKILL.md
│   ├── theme-expert-prism-edge/SKILL.md
│   └── theme-expert-warm-sunnyday/SKILL.md
└── README.md
```

- **`themes/`** — Theme CSS files ready to use with Marp.
- **`slides/sample-slide/`** — Comprehensive demo decks showcasing every layout and component for each theme.
- **`skills/`** — Detailed skill documentation for AI assistants (e.g., prompts, class references, best practices).
- **`skills/marp-slide-creator/scripts/`** — Scripting toolkit for high-quality Marp generation:
  - `marp-lint.py`: Catches structural mistakes (missing class directives, centered lists) *before* rendering.
  - `marp-diagnostics.py`: Surfaces overflow and broken-image risks *after* rendering to HTML.
  - `marp-dom-extractor.py`: Playwright-based metrics extractor for AI-driven layout review.
  - `setup-slide-project.py`: Project scaffolding helper.

### Skill Routing

Use the smallest set of skills that fully covers the task:

If the deck will be exported to PDF or PPTX, design to the static slide canvas from the start. Do not rely on scrollable panels or clipped overflow.

1. Topic, audience, output format, outline, or structure still unclear -> `slide-content-designer`
2. Outline approved, or you need Marp Markdown, layout fixes, overflow checks, or export -> `marp-slide-creator`
3. SVG icons need to be selected, copied, or recolored -> `marp-svg-icon-placer`
4. One domain-specific presentation type is involved -> pick one matching `slide-expert-*` skill

   | Skill | Use case |
   |-------|----------|
   | `slide-expert-design-review` | Design content (structure / IF / state transitions / exception handling) |
   | `slide-expert-requirements-specification` | Functional / non-functional requirements, constraints, assumptions |
   | `slide-expert-tech-selection` | Multi-option trade-off comparison and recommendation |
   | `slide-expert-api-architecture` | System-wide architecture, data flows, responsibility segregation |
   | `slide-expert-progress-report` | Implementation results, milestone tracking, stakeholder updates |
   | `slide-expert-release-notes` | Release value, impact scope, migration steps |
   | `slide-expert-postmortem` | Incident cause, impact, timeline, preventive actions |
   | `slide-expert-tech-sharing` | Knowledge sharing, study groups, best practices |
   | `slide-expert-self-introduction` | Personal background, skills, interests for new assignments |
5. Theme-specific layout polish is needed -> pick one matching `theme-expert-*` skill after the theme is known
6. Generic Marp layout mechanics are needed -> open `theme-expert-common` only for the shared class reference

---

## Sample Slides

Each theme includes a fully-featured sample deck demonstrating:

- Cover slides and section dividers
- Bullet lists with grouped items
- Tables (including pricing and schedule styles)
- 2-column and 3-column layouts (card and split variants)
- 4-quadrant grids with text and images
- Process steps and project timelines
- Checklists and callout boxes
- Code blocks and dense information slides
- Image placement, shadows, and background splits
- Profile slides and key-message slides

Open any `*-sample.md` in VS Code with the Marp extension to preview.

---

## Customization

Each theme is built on CSS custom properties. To tweak colors globally, edit the `:root` block at the top of the CSS file:

```css
:root {
  --ac-primary: #2C7BE5;       /* Main brand color */
  --ac-text: #1A1A2E;          /* Body text */
  --ac-bg: #FAFCFF;            /* Background tint */
  --ac-radius: 0px;            /* Corner rounding */
}
```

No build step required — changes are live on save.

---

## Requirements

- [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) **or**
- [Marp CLI](https://github.com/marp-team/marp-cli) v2.x+

Slide dimensions: **1280 x 720 px** (16:9)

### Optional: Playwright (for AI DOM-based review)

If you want AI models without image support to review slide layouts, install the Playwright-based DOM extractor:

```bash
pip install playwright
playwright install chromium
```

This enables the alternative text-only review pipeline described in `skills/marp-slide-creator/SKILL.md` and `skills/marp-slide-creator/scripts/marp-diagnostics.py`.

---

## Third-party Assets

- SVG icons in `skills/marp-svg-icon-placer/references/icons/`: [Phosphor Icons](https://phosphoricons.com/) — [MIT License](https://github.com/phosphor-icons/core/blob/main/LICENSE)
- Bundled fonts in `assets/fonts/`:
  - **Serif/Sans**: [Carlito](https://github.com/googlefonts/carlito), [Caladea](https://github.com/huertatipografica/Caladea), [Poppins](https://github.com/itfoundry/poppins), [Space Grotesk](https://github.com/floriankarsten/space-grotesk)
  - **Japanese**: [Noto Sans JP](https://github.com/googlefonts/noto-cjk), [Zen Maru Gothic](https://github.com/googlefonts/zen-marugothic)
  - **Mono**: [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono), [Liberation Mono](https://github.com/liberationfonts/liberation-fonts)
  - All under [SIL Open Font License 1.1](https://scripts.sil.org/OFL)

## License

MIT License — Copyright (c) 2026 FunUd

See [LICENSE](LICENSE) for full details.
