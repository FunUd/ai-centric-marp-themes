---
name: theme-expert-slate-minimal
description: Activate this skill ONLY when the Marp implementation phase has begun and the Slate Minimal theme has already been chosen. DO NOT activate during outlining.
---

# Slate Minimal Theme Expert

An ultra-minimalist, monochrome theme focused entirely on typography, whitespace, and content clarity, eliminating all unnecessary decoration.

Use this skill after the content structure is decided. For outline planning or story shaping, use `slide-content-designer` or the relevant domain skill first.

## What Slate Minimal Is Best For

- Academic research presentations and philosophical talks
- Design concepts and mood boards where the content itself is the design
- Highly focused executive summaries
- Audiences that prefer extreme clarity over visual flair

## Slate Minimal-Specific Cues

- **Monochrome Elegance:** The theme uses only grayscale (Slate shades). Semantic colors (success, warning, danger) are mapped to subtle grays. Rely on typography and layout, not color, to convey meaning.
- **Typography:** Uses a beautiful Serif font (`Caladea`) for headings to give an editorial/academic feel, paired with a clean Sans-serif (`Poppins`) for body text. 
- **Restraint:** Do not add inline styles for colors. Embrace the whitespace. The design relies on emptiness to make the text stand out.

## Shared Mechanics

For the exact syntax of the shared Marp patterns, read `theme-expert-common` only when the slide needs one of these:

- Cover and title layout (Note: Cover is very simple, text-aligned left with a small accent line)
- TOC and agenda layout
- Columns, grids, density, profile, key message
- Steps, timeline, checklist, timetable
- Callouts, alignment, and image placement

## Core Principle: Lines Are a Last Resort

Slate Minimal follows the **4 Principles of Minimalism** (Reduction, Alignment, Emphasis, Whitespace). The most important rule for this theme:

> Use **whitespace, typography, and contrast** to express relationships between elements. Only use lines/borders where removing them would genuinely harm readability.

**Where borders ARE used** (structurally necessary):
- Tables (cell separation), timelines (vertical connector), blockquotes (left accent), links (underline), `grid-sharp` (intentional grid), badges (outline-only style), callouts (left accent)

**Where borders are NOT used** (whitespace/typography handles it):
- `h1` headings, column separators, TOC/TOC-focus items, steps separators, grid-quadrant cells, inline code, `bg-pale`/`bg-light` utilities

## Emphasis Without Color (色に頼らない強調パターン)

Grayscale cannot signal urgency by hue: `callout red` and `badge red` differ from other variants only in lightness. Use fill and typography instead.

- **Severity:** reserve `<span class="badge ink">` (solid `--sm-accent` fill, the darkest) for the highest severity only. Rank lower items with a callout's left border plus a bold label, not color names.
- **Closing:** use a `key-message` `##` (56px Serif), not `> 引用` (26px gray italic), for impact.
- **Shades:** `--sm-danger: #1E293B` is visibly darker than `--sm-warning: #64748B`; when both appear, assign danger to the stronger item.

```markdown
<span class="badge ink">CRITICAL</span>

<div class="callout red">

**原因:** 本文をここに書く

</div>

<!-- _class: key-message -->

## 締めの一文をここに書く
```

## Design Tips

- Keep text short and impactful. A minimalist theme falls apart if slides are cluttered with bullet points.
- Use `key-message` layouts to make powerful, single-sentence statements.
- **Never add decorative borders.** If you feel a section needs visual separation, increase spacing first. If that's not enough, try a subtle background difference. Reach for a border only as a final option.
