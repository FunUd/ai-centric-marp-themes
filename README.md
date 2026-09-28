# AI-Centric Marp Themes

A curated collection of **production-ready, AI-optimized Marp themes** designed for professional business presentations. Each theme offers a complete visual system — cover slides, multi-column layouts, callouts, timelines, grids, and more — all controllable via simple CSS classes in your Markdown.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Themes

| Theme | Style | Best For |
|-------|-------|----------|
| **Azure Clarity** | Clean, corporate blue | Business reports, project proposals, technical documentation |
| **Crimson Clarity** | Deep, energetic corporate red | High-impact proposals, strategic plans, executive summaries |
| **Prism Edge** | Editorial indigo-cyan, polished and restrained | Keynotes, product launches, investor pitches |
| **Nebula Glass** | Dark glassmorphism, cyber-luxe | Tech demos, premium keynotes, high-sense product presentations |
| **Warm Sunnyday** | Warm orange, friendly rounded | Casual presentations, workshops, community talks |
| **Slate Minimal** | Monochrome, serif typography, extreme minimalism | Academic research, design concepts, philosophical talks |


> Theme details, cover variants, and slide previews: [docs/themes.md](docs/themes.md).

---

## Quick Start

1. **Install [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)** or use the [Marp CLI](https://github.com/marp-team/marp-cli).

2. **Copy the theme CSS** you want from the `themes/` folder into your Marp workspace (or configure `themeSet` in `marp.config.js`). If you use `prism-edge`, `nebula-glass`, `warm-sunnyday`, or `slate-minimal`, also copy `assets/fonts/` so the `@font-face` paths (`../assets/fonts/*.ttf`) keep resolving. Nebula Glass needs `Poppins-Bold/Regular`, `NotoSansJP-Variable`, and `JetBrainsMono-Regular`. When exporting HTML/PDF to another folder, reproduce the same relative layout next to the output (e.g. `<out>/../assets/fonts/…` for an HTML file that references `../assets/fonts/…`) — Marp inlines the CSS but keeps `url()` paths as-is, so fonts 404 otherwise. A `[WARN] Cannot register theme CSS: themes\_base.css` line during `--theme-set themes` builds is benign: `_base.css` is the shared development source, not a selectable theme.

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

### 5. Setup for AI Agents (Recommended)

If you are using AI coding assistants like **Claude Code, Windsurf, Cursor, Kiro, or VS Code Copilot**, you can enable the custom "Skills" (specialized prompts and tools) included in this repo.

Run the synchronization script to install these skills into your editor's configuration directory:

```bash
python scripts/sync-skills.py
```

This copies the contents of `skills/` (the single source of truth) into `.claude/skills/`, `.agents/skills/`, `.windsurf/skills/`, `.kiro/skills/`, `.codex/skills/`, `.agent/skills/` and `.github/skills/`, so the AI understands the layout classes and best practices for these themes. Existing skill directories with the `theme-expert-`, `slide-expert-`, `marp-`, `theme-creator`, or `slide-content-designer` names are replaced; nothing else is touched. Re-run it after editing anything under `skills/`.

**You can also copy a single skill directory anywhere** — including
`~/.claude/skills/` for a personal, machine-wide install. `marp-diagram-creator`
is self-contained: it carries its own copy of the diagram engine under
`vendor/`, so every command in it resolves without this repository present.
`marp-slide-creator` and `marp-svg-icon-placer` are likewise self-contained.
The `slide-expert-*`, `theme-expert-*`, `slide-content-designer` and
`theme-creator` skills are prose-only and need nothing beyond their own files.

---

## Layout Classes Overview

The full class reference (layouts, alignment, color utilities, components) lives in
[docs/classes.md](docs/classes.md). It is CI-verified against `themes/*.css`.

---

## Project Structure

```
ai-centric-marp-themes/
├── docs/
│   ├── themes.md                # Theme details, cover variants, slide previews
│   ├── classes.md               # Layout class reference (CI-verified)
│   └── diagrams.md              # Diagram engines, templates, embedding guide
├── themes/
│   ├── _base.css                # Shared structural CSS (SSoT; propagated by sync-theme-base.py)
│   ├── azure-clarity.css      # Corporate blue theme
│   ├── crimson-clarity.css       # Deep corporate red theme
│   ├── nebula-glass.css       # Dark glassmorphism theme
│   ├── prism-edge.css         # Bold modern theme
│   ├── warm-sunnyday.css      # Warm friendly theme
│   └── slate-minimal.css      # Monochrome minimalist theme
├── slides/
│   ├── sample-slide/
│   │   ├── azure-clarity-sample.md
│   │   ├── crimson-clarity-sample.md
│   │   ├── nebula-glass-sample.md
│   │   ├── prism-edge-sample.md
│   │   ├── warm-sunnyday-sample.md
│   │   ├── slate-minimal-sample.md
│   │   ├── quality-showcase.md
│   │   └── assets/
├── scripts/
│   ├── sync-skills.py                 # Setup tool for AI agent skills
│   ├── sync-skill-vendor.py           # Vendors the diagram runtime into marp-diagram-creator (`--check` in CI)
│   ├── take-screenshots.py            # Regenerates assets/screenshots/*.png from the sample decks
│   └── diagrams/
│       ├── render-slide-diagram.py    # Mermaid / draw.io / JSON → themed SVG
│       ├── validate-slide-diagram.py  # Canvas constraint validator
│       ├── layout_spec.py             # Canonical layout geometry (single source of truth)
│       ├── theme_classes.py           # Canonical class semantics, parsed from themes/*.css
│       ├── tool_versions.py           # Pinned @mermaid-js/mermaid-cli + @marp-team/marp-cli
│       ├── check-catalog-sync.py      # Template registry consistency check
│       ├── check-templates.py         # Renders + validates every template at its supported layouts
│       ├── check-class-docs.py        # README ⇔ theme class system consistency
│       ├── sync-tokens-from-css.py    # themes/*.css → theme-styles/*.json (`--check` in CI)
│       ├── sync-theme-classes.py      # theme_classes.py → skills/…/theme-classes.json (`--check` in CI)
│       ├── ADD_NEW_DIAGRAM_TYPE.md    # Procedure for adding JSON diagram types
│       ├── templates/
│       │   ├── mermaid/               # .mmd templates (5 patterns)
│       │   ├── drawio/                # .drawio templates (2 patterns)
│       │   ├── charts/                # JSON chart templates (5)
│       │   ├── concepts/              # JSON concept templates (4)
│       │   └── organization/          # JSON org-chart template
│       ├── theme-styles/              # Per-theme color palette JSON (6 themes)
│       └── tests/                     # pytest suite
├── skills/
│   ├── marp-diagram-creator/          # Diagram creation skill (self-contained)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── print-engine-path.py     # Resolves the vendored engine to an absolute path
│   │   ├── vendor/                      # Vendored diagram runtime (generated, drift-checked)
│   │   │   ├── render-slide-diagram.py  # Mermaid / draw.io / JSON → themed SVG
│   │   │   ├── validate-slide-diagram.py
│   │   │   ├── templates/               # 28 templates
│   │   │   └── theme-styles/            # 6 theme palettes
│   │   └── references/
│   │       ├── diagram-patterns.md
│   │       └── template-catalog.md
│   ├── slide-content-designer/SKILL.md
│   ├── marp-slide-creator/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── post-edit-check.py         # Post-edit sanity (glued `---`, slide count, language)
│   │       ├── marp-diagnostics.py        # Overflow / layout diagnostics helper
│   │       ├── marp-dom-extractor.py      # Playwright DOM metrics extractor for text-only AI review
│   │       ├── marp-lint.py               # Pre-render linter (structural + diagram embedding checks)
│   │       ├── setup-slide-project.py     # Project scaffolding helper
│   │       └── theme-classes.json         # Generated class manifest read by marp-lint.py
│   ├── marp-svg-icon-placer/SKILL.md
│   ├── theme-creator/SKILL.md
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
│   ├── theme-expert-nebula-glass/SKILL.md
│   ├── theme-expert-prism-edge/SKILL.md
│   ├── theme-expert-warm-sunnyday/SKILL.md
│   └── theme-expert-slate-minimal/SKILL.md
└── README.md
```

- **`themes/`** — Theme CSS files ready to use with Marp. Each theme file is standalone (copy one file and use it — no build step). `themes/_base.css` is the development source for the structurally identical sections (22 sections, 84 regions across 6 themes for a11y, 4 for layout); `python scripts/sync-theme-base.py` propagates edits into the `<base:name>` marker regions (`--check` in CI).
- **`slides/sample-slide/`** — Comprehensive demo decks showcasing every layout and component for each theme, plus `quality-showcase.md` as the lint-clean reference deck.
- **`assets/screenshots/`** — Generated by `python scripts/take-screenshots.py` and embedded throughout this README. Regenerate after editing any sample deck.
- **`skills/`** — Detailed skill documentation for AI assistants (e.g., prompts, class references, best practices).
- **`skills/marp-diagram-creator/`** — The only skill that *executes* code from this repository, so it is the only one that had to become self-contained. It ships a generated copy of the diagram engine under `vendor/` (renderer, validator, 28 templates, 6 theme palettes — 46 files), so the skill works when installed to `~/.claude/skills/`, a colleague's machine, or a vendored checkout. `scripts/diagrams/` remains the development source; `python scripts/sync-skill-vendor.py --check` fails if the two drift. Repository-only tooling (`check-*.py`, `sync-*.py`, the test suite) is deliberately *not* vendored — it reads `README.md` and `themes/*.css` and cannot work outside a checkout.
- **`skills/marp-slide-creator/scripts/`** — Scripting toolkit for high-quality Marp generation:
  - `post-edit-check.py`: Catches the edit-time damage `marp-lint.py` structurally cannot — a `---` glued to text (which silently merges two slides), a slide count that disagrees with the approved outline, a missing EOF newline, and out-of-language characters.
  - `marp-lint.py`: Catches structural mistakes (missing class directives, lists on title layouts, diagram embedding errors) *before* rendering. Its class semantics come from the generated `theme-classes.json`, so they stay in step with `themes/*.css`.
  - `marp-diagnostics.py`: Surfaces overflow and broken-image risks *after* rendering to HTML, with support for exporting clean, bespoke-UI-free screenshots for visual inspection.
  - `marp-dom-extractor.py`: Playwright-based metrics extractor for AI-driven layout review.
  - `setup-slide-project.py`: Project scaffolding helper.
- **`scripts/diagrams/`** — Diagram generation engine for slide-optimized SVGs:
  - `render-slide-diagram.py`: Renders Mermaid, draw.io, or structured JSON sources into theme-aware SVGs, with automatic canvas validation.
  - `validate-slide-diagram.py`: Validates rendered SVG and draw.io files against slide canvas and geometry constraints.
  - `layout_spec.py`: Canonical layout geometry (`full`/`col2`/`asym`/`col3`) shared by the renderer, validator, and linter.
  - `theme_classes.py`: Canonical class semantics — which layouts are title/message layouts, which are exempt from the weak-title check, and the class → layout-profile map — parsed from `themes/*.css` so the CSS stays the authority on what exists.
  - `check-catalog-sync.py`: Verifies templates on disk stay in sync with the README table and `template-catalog.md`.
  - `check-templates.py`: Renders and validates every template at each layout it supports, and fails when a template is missing from that list. Mermaid templates need Node; pass `--skip-mermaid` for an offline run.
  - `check-class-docs.py`: Verifies the class reference above against `themes/*.css` in both directions — an implemented class must be documented, and a class documented as universal must exist in every theme.
  - `sync-tokens-from-css.py`: Derives `theme-styles/*.json` from `themes/*.css`; `--check` is the CI gate and reports drift for colors, shapes, effects, signature, and the derived draw.io styles.
  - `tool_versions.py`: Pinned Node tool versions, mirrored into `package.json`. Unpinned, `npx -y <pkg>` downloads whatever is newest, so the same deck renders differently tomorrow and the golden SVG fixtures fail for reasons nobody changed. Override with `MARP_CLI_SPEC` / `MERMAID_CLI_SPEC`.
  - `sync-theme-classes.py`: Generates `skills/marp-slide-creator/scripts/theme-classes.json` from `theme_classes.py`; `--check` is the CI gate. Run it after changing a theme CSS or the class semantics.
  - `ADD_NEW_DIAGRAM_TYPE.md`: Step-by-step procedure for adding a new JSON diagram type.
  - `templates/mermaid/`: Five ready-to-use Mermaid (`.mmd`) diagram templates.
  - `templates/drawio/`: Two ready-to-use draw.io (`.drawio`) diagram templates.
  - `templates/charts|concepts|organization/`: Ten ready-to-use JSON diagram templates.
  - `theme-styles/`: Per-theme color palette definitions (JSON) for all 6 themes.
  - `tests/`: pytest suite. Run with `python -m pytest scripts/diagrams/tests/ -q`.

### Skill Routing

Use the smallest set of skills that fully covers the task:

If the deck will be exported to PDF or PPTX, design to the static slide canvas from the start. Do not rely on scrollable panels or clipped overflow.

1. Topic, audience, output format, outline, or structure still unclear -> `slide-content-designer`
2. Outline approved, or you need Marp Markdown, layout fixes, overflow checks, or export -> `marp-slide-creator`
3. SVG icons need to be selected, copied, or recolored -> `marp-svg-icon-placer`
4. A diagram (flowchart, sequence, architecture, matrix) needs to be created or embedded -> `marp-diagram-creator`
5. One domain-specific presentation type is involved -> pick one matching `slide-expert-*` skill
6. Theme-specific layout polish is needed -> pick one matching `theme-expert-*` skill after the theme is known
7. A **new** theme needs to be designed from scratch -> `theme-creator`
8. Generic Marp layout mechanics are needed -> open `theme-expert-common` only for the shared class reference

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

---

## Diagram Creation

Theme-aware, slide-safe diagrams are documented in [docs/diagrams.md](docs/diagrams.md)
(engines, generation, embedding widths, template catalogs, lint integration).

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

Each theme is built on CSS custom properties. To tweak colors globally, edit the `:root` block at the top of the theme's CSS file:

```css
:root {
  --ac-primary: #2C7BE5;       /* Main brand color */
  --ac-primary-dark: #1B4F72;
  --ac-primary-light: #D0EBFF;
  --ac-primary-pale: #EDF5FF;
  --ac-accent: #1B4F72;
  --ac-text: #1A1A2E;          /* Body text */
  --ac-bg: #FAFCFF;            /* Background tint */
  --ac-radius: 0px;            /* Corner rounding */
}
```

**Each theme has its own prefix and its own token names** — using the wrong prefix
silently does nothing:

| Theme | Prefix | Text token | Notable differences |
|---|---|---|---|
| `azure-clarity` | `--ac-` | `--ac-text` / `--ac-text-sub` | — |
| `crimson-clarity` | `--cc-` | `--cc-text` / `--cc-text-sub` | — |
| `prism-edge` | `--pe-` | `--pe-text` / `--pe-text-sub` | accents use `--pe-cyan` |
| `nebula-glass` | `--ng-` | `--ng-text` / `--ng-text-muted` | no derived `*-dark/light/pale`; uses `--ng-glass-*`, `--ng-glow-*` |
| `warm-sunnyday` | `--ws-` | `--ws-text` / `--ws-text-sub` | warm orange palette, rounded `--ws-radius: 12px` |
| `slate-minimal` | `--sm-` | `--sm-ink` / `--sm-ink-soft` | `ink*` instead of `text*` |

The diagram renderer reads the same variables. After editing a theme, regenerate
the derived diagram tokens and confirm nothing drifted:

```bash
python scripts/diagrams/sync-tokens-from-css.py            # rewrite theme-styles/*.json
python scripts/diagrams/sync-tokens-from-css.py --check    # CI gate: fail on drift
```

No build step required — changes are live on save.

---

## Requirements

- [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) **or**
- [Marp CLI](https://github.com/marp-team/marp-cli) v4.2.3 (pinned in `package.json` / `scripts/diagrams/tool_versions.py`; override via `MARP_CLI_SPEC`)

Slide dimensions: **1280 x 720 px** (16:9)

### Accessibility

- **Reduced motion**: `prefers-reduced-motion` disables the Prism Edge aurora animation and item transitions (shipped via `themes/_base.css`, 4 themes that animate).
- **Keyboard focus**: `section:focus-visible` draws a 3px indicator in the theme primary (warm-sunnyday uses `--ws-primary-dark`: its primary orange is 2.3:1 on the background, below the 3:1 floor).
- **Contrast**: body/muted text meets AA (4.5:1) on every theme's background, verified by `tests/test_slide_contrast.py` from the generated `theme-styles/*.json` palette. Diagram labels use maximum-ratio ink selection (`design_tokens.best_text_on`).

### Optional: Playwright (for AI DOM-based & Visual Review)

Playwright is required to extract slide DOM metrics (enabling layout overflow detection) and to generate clean, bespoke-UI-free slide screenshots for AI visual inspection:

```bash
pip install playwright
playwright install chromium
```

This enables the diagnostics and screenshot capture pipeline described in `skills/marp-slide-creator/SKILL.md` and `skills/marp-slide-creator/scripts/marp-diagnostics.py`.

### Offline Execution Policy

- Apart from installation, slide data is never sent to an external server.
- Network access happens only at tool-install time: `npm install` / `pip install` / `playwright install chromium`.
- All execution after that is local: Mermaid / Marp CLI run locally via `npx`, and screenshots / DOM extraction use `file://` + local Chromium.
- A remote fetch occurs only when your own deck embeds a `https://` image URL.
- Using an AI assistant sends deck content to the LLM provider separately. Keep confidential decks out of Skills scope.

---

## Third-party Assets

- SVG icons in `skills/marp-svg-icon-placer/references/icons/`: [Phosphor Icons](https://phosphoricons.com/) — [MIT License](https://github.com/phosphor-icons/core/blob/main/LICENSE)
- Bundled fonts in `assets/fonts/` (see [`assets/fonts/NOTICE.md`](assets/fonts/NOTICE.md) for the per-theme mapping):
  - **Serif/Sans**: [Caladea](https://github.com/huertatipografica/Caladea), [Poppins](https://github.com/itfoundry/poppins), [Space Grotesk](https://github.com/floriankarsten/space-grotesk)
  - **Japanese**: [Noto Sans JP](https://github.com/notofonts/noto-cjk), [Zen Maru Gothic](https://github.com/googlefonts/zen-marugothic)
  - **Mono**: [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
  - All under [SIL Open Font License 1.1](https://scripts.sil.org/OFL)
  - `azure-clarity` and `crimson-clarity` bundle nothing and use the OS font stack.

## Original Assets

- `slides/sample-slide/assets/sample_image.jpg` is an original image created by the repository author and is not a third-party asset.

## License

MIT License — Copyright (c) 2026 FunUd

See [LICENSE](LICENSE) for full details.
