# Layout Classes Overview

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
| `cover-nebula` | *(Nebula Glass)* Architectural left-aligned cover with light beams |
| `hero` | *(Prism Edge)* Single large centered message (H1 at 72px) |
| `title-only` | *(Prism Edge)* Minimal large left-aligned title (H1 at 64px) |
| `title-elegant` | *(Prism Edge)* Elegant centered title slide (adapts to subtitle presence) |
| `toc` | Two-column table of contents |
| `toc-focus` | Single-column large-number agenda |
| `cols-2` / `cols-3` | Card-style columns with background/border |
| `split-2` / `split-3` | Clean columns without card styling |
| `split-asym` / `split-asym-reverse` | *(Prism Edge)* Asymmetric 65:35 split columns |
| `split-glass` | *(Nebula Glass)* 50/50 split, right column wrapped in a glass panel |
| `glass-card-layout` | *(Nebula Glass)* Focused key message: centered title with a left-aligned card |
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
| `grid-quadrant` + `axes` | Adds axis labels to a quadrant matrix: `<div class="grid">` with `<span class="axis-y">` / `<span class="axis-x">` + 4x `<div class="cell">` in order (`<span>` axes required so `div:nth-of-type` stays aligned; `<div>` axes also work via `:nth-child` fallback) |
| `steps` + `arrows` | Adds connector arrows between step cards |
| `dense` | High-density slide (body 18px; H1 title stays full size) |
| `extra-dense` | Maximum density (body 15px; H1 title stays full size) |
| `section-number` | *(Prism Edge)* Large decorative section numeral in the corner |

### Alignment & Utilities

| Class | Description |
|-------|-------------|
| `v-center` / `v-middle` / `v-top` / `v-bottom` | Vertical alignment (`v-middle` is an alias of `v-center`) |
| `text-center` / `text-left` / `text-right` | Horizontal alignment |
| `align-center` / `align-left` / `align-right` | Whole-slide horizontal alignment (all themes) |
| `no-pagination` | Hide page number |
| `no-header` / `no-footer` | Hide header/footer |
| `with-header` | Extra top padding for header space |
| `pagination-left` | Move page number to bottom-left |
| `text-large` / `text-small` | 1.3em / 0.85em text size utility |

### Color Utilities

Text tint and background utilities.

| Class | Description |
|-------|-------------|
| `text-accent` | Theme accent colour |
| `text-sub` | Muted secondary text |
| `text-muted` | *(Nebula Glass)* Nebula's name for `text-sub`; `text-sub` also works there |
| `text-blue` / `text-green` / `text-orange` / `text-red` | Fixed semantic tints, contrast-adjusted per theme |
| `text-violet` / `text-cyan` / `text-rose` / `text-white` | *(Nebula Glass)* neon tints |
| `text-magenta` | *(Prism Edge)* accent tint |
| `bg-pale` / `bg-light` | Slide background tints (all 6 themes) |
| `bg-dark` | *(Prism Edge only)* dark background tint |

### Components

| Component | Usage |
|-----------|-------|
| **Callouts** | `<div class="callout blue">...</div>` (types: `blue`, `green`, `orange`, `red`; Nebula Glass also accepts `violet`, `cyan`, `rose` and maps `blue`→cyan, `orange`/`red`→rose) — independent alert blocks |
| **Badges** | `<span class="badge red">NEW</span>` (types: `blue`, `green`, `orange`, `red`; Nebula Glass also accepts `violet`, `cyan`, `rose` with the same mapping; Slate Minimal also accepts `ink`) |
| **Glass Panel** | *(Prism Edge / Nebula Glass)* `<div class="glass-panel">...</div>` — frosted glass container |
| **Gradient Text** | *(Prism Edge / Nebula Glass)* `<span class="gradient-text">Text</span>` — gradient fill |
| **Glow Violet** | *(Nebula Glass)* `<span class="glow-violet">Text</span>` — subtle violet light emission |
| **Glow Cyan** | *(Nebula Glass)* `<span class="glow-cyan">Text</span>` — subtle cyan light emission |
| **Highlight Box** | *(Prism Edge)* `<div class="highlight-box">...</div>` — inline emphasis block for key insights |
| **Quote Large** | *(Prism Edge)* `<div class="quote-large">...</div>` — 32px italic editorial blockquote |
| **Underline Accent** | *(Prism Edge)* `<span class="underline-accent">Text</span>` — gradient underline |
| **Stat Number** | *(Prism Edge)* `<span class="stat-number">42</span><span class="stat-label">Label</span>` |
| **Images** | `![center shadow width:600px](path)` or `![bg right:45% shadow](path)` |

> **Class reference is CI-verified.** `themes/*.css` is the authority for what
> exists; `python scripts/diagrams/check-class-docs.py` fails if a class is
> implemented but undocumented here, or documented as universal when a theme
> lacks it. Theme-specific classes carry a *(Theme)* marker.
