---
name: theme-expert-nebula-glass
description: Activate this skill ONLY when the Marp implementation phase has begun and the Nebula Glass theme has already been chosen. DO NOT activate during outlining.
---

# Nebula Glass Theme Expert

This skill is for slides that need to feel ultra-modern, "high-sense," tech-premium, and "cyber-luxe."
It is the most advanced theme in the collection, surpassing Prism Edge in visual depth and sophistication.

## Theme File
The theme is located at `themes/nebula-glass.css`.

## Nebula Glass-Specific Cues

- Use `cover-nebula` for a sophisticated, architectural opening or closing. It features a left-aligned layout with a subtle top border and refined light beams.
- Use `glass-card-layout` with a `<div class="card">` wrapper for a focused key message. Inside the card, text is left-aligned for better list presentation, while the title remains centered.
- Use `split-glass` with a `<div class="glass-panel">` to create a modern, asymmetric layout.
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
