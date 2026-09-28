---
name: theme-expert-nebula-glass
description: Activate this skill ONLY when the Marp implementation phase has begun and the Nebula Glass theme has already been chosen. DO NOT activate during outlining.
---

# Nebula Glass Theme Expert

This skill is for slides that need to feel ultra-modern, "high-sense," tech-premium, and "cyber-luxe."
It is the most advanced theme in the collection, surpassing Prism Edge in visual depth and sophistication.

## Theme File
The theme is `themes/nebula-glass.css` in the `ai-centric-marp-themes` repository. To render a deck with it, copy the CSS into your own project (e.g. `<deck>/themes/nebula-glass.css`) and pass `--theme themes/nebula-glass.css` to Marp; the `@font-face` rules reference `../assets/fonts/`, so copy `assets/fonts/` alongside it to keep the bundled Poppins (Regular/Italic/Bold/BoldItalic), Noto Sans JP (Variable), and JetBrains Mono (Regular/Bold/Italic/BoldItalic) type.

## Nebula Glass-Specific Cues

- Use `cover-nebula` for a sophisticated, architectural opening or closing. It features a left-aligned layout with a subtle top border and refined light beams.
- Use `glass-card-layout` with a `<div class="card">` wrapper for a focused key message. Inside the card, text is left-aligned for better list presentation, while the title remains centered. This is a single centered column budgeted as 2-column, so keep diagrams at the 2-column budget (`width:500px`, max 520px) — see `layout_spec.py::CLASS_TO_LAYOUT`.
- Use `split-glass` for a 50/50 split where the right column is a glass panel. It is a bare `1fr 1fr` grid: the slide must contain **exactly two divs**, with the heading **inside** `.content`. Any other shape silently collapses:
  ```markdown
  <!-- _class: split-glass -->

  <div class="content">

  # Heading goes here, not above the divs

  </div>

  <div class="glass-panel">

  ### Points

  </div>
  ```
  Diagram width budget is the 2-column limit (`width:500px`, max 520px), not the asymmetric one.
- Use `steps` on a list (specifically `li`) for minimal, glass-style numbered indicators.
- Use `<span class="gradient-text">` for elegant keyword emphasis.
- Use `<span class="glow-violet">` or `<span class="glow-cyan">` for subtle light emission effects.
- Use `blockquote` for refined, glass-textured quotes.

## Design Philosophy

- **Subtlety**: Move away from heavy glows; favor refined transparency and sharp borders.
- **Asymmetry**: Avoid "centered-everything" for a more modern, architectural feel.
- **Harmony**: Ensure Japanese typography (Noto Sans JP) is well-balanced with English (Poppins).


## Shared Mechanics

For generic Marp patterns, read `theme-expert-common` only when you need TOC, columns, grids, density, or image placement. Note that Nebula Glass often handles hierarchy better via glass panels than standard columns.
