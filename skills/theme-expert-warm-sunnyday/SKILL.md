---
name: theme-expert-warm-sunnyday
description: A skill for maximizing the use of the Warm Sunnyday theme (for Marp) to create friendly, approachable presentations for self-introductions, icebreakers, and casual chats. Trigger this skill when the user wants to design or modify slides for informal settings using the Warm Sunnyday theme.
---

# Warm Sunnyday Theme Expert

This skill provides guidelines for using the Warm Sunnyday theme — designed for self-introductions, icebreakers, casual meetings with warm oranges, pinks, and rounded fonts (Nunito / Zen Maru Gothic).

## Basic Principles

Foster communication and a friendly atmosphere. Rounded corners, soft colors, and playful fonts reduce tension — perfect for onboarding, team building, or casual lightning talks.

## Layout Guide by Use Case

### 1. Cover / Title Slide
- **Classes**: `<!-- _class: cover subtitle meta -->`
- **Directives**: `<!-- _paginate: false -->`, `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Features: Warm gradient background, friendly tone

### 2. Agenda / TOC
- **Many items**: `<!-- _class: toc -->` (2-column numbered)
- **Few items (4-5)**: `<!-- _class: toc-focus -->` (large single column)

### 3. Profile / Self-Introduction
- **Class**: `<!-- _class: profile -->`
- **Structure**:
  ```html
  <div class="profile-layout">
    <div class="profile-image">
      ![](photo.jpg)
    </div>
    <div class="profile-content">
  # Name
  ## Role / Hometown
  - Hobby 1
  - Hobby 2
    </div>
  </div>
  ```
- Features: Circular photo (200×200px) with warm border

### 4. Hobbies / Interests (Columns)

**Card Type**:
- `<!-- _class: cols-2 -->` or `<!-- _class: cols-3 -->`
- Structure: `<div class="columns"><div class="col">...</div></div>`
- Add `v-center text-center` for friendly showcase

**Simple Type**:
- `<!-- _class: split-2 -->` or `<!-- _class: split-3 -->`

### 5. Icebreaker / Q&A Grid
- **Class**: `<!-- _class: grid-quadrant -->`
- **Structure**:
  ```html
  <div class="grid">
    <div class="cell v-center text-center">
      ### 🐕 Dogs or 🐈 Cats?
      I love dogs!
    </div>
    <div class="cell">...</div>
  </div>
  ```

### 5-2. Sharp Grid
- **Class**: `<!-- _class: grid-sharp -->`
- Features: Border-only, no backgrounds

### 6. Step-by-Step Process
- **Class**: `<!-- _class: steps -->`
- Ordered list → horizontal cards with "STEP N" badges
- `**Bold text**` = step title

### 7. Timeline / History
- **Class**: `<!-- _class: timeline -->`
- Ordered list → vertical timeline with dots
- **IMPORTANT**: Bold date and text on same line:
  ```markdown
  1. **2024 Q1** Project kickoff
  2. **2024 Q3** Prototype complete
  ```

### 8. Motto / Key Message
- **Class**: `<!-- _class: key-message no-pagination -->`
- **Directives**: `<!-- _header: "" -->`, `<!-- _footer: "" -->`
- Structure: Main message in `> blockquote`

### 9. Schedule / Timetable
- **Class**: `<!-- _class: timetable -->`
- Table → first column highlighted in orange

### 10. Information Density
- **Slightly compact (18px)**: `<!-- _class: dense -->`
- **Very compact (15px)**: `<!-- _class: extra-dense -->`

### 10-2. Fine-Grained Font Scale
```markdown
<style scoped>
section { --font-scale: 0.85; }
</style>
```
Range: `0.7` to `1.0`. Common: `0.95`, `0.9`, `0.85`, `0.75`, `0.7`

## Header / Footer / Pagination

| Class | Effect |
|-------|--------|
| `no-header` | Hide header |
| `no-footer` | Hide footer |
| `no-pagination` | Hide page number |
| `pagination-left` | Move to bottom-left |
| `with-header` | Add top padding |

## Component Guide

### Checklist
- **Class**: `<!-- _class: checklist -->`
- Unordered list → green rounded checkmarks
- Inline: `<ul class="checklist">...</ul>`

### Callouts
```html
<div class="callout info">
  <h4>💡 Tip</h4>
  Content
</div>
```
Types: `info` (orange), `success` (green), `warning` (amber), `danger` (red)

### Badges
`<span class="badge">Label</span>`
Types: `badge`, `badge primary` (orange), `badge success`, `badge warning`, `badge danger`

## Alignment & Images

### Alignment
- Vertical: `v-top`, `v-center`, `v-bottom`
- Horizontal: `text-left`, `text-center`, `text-right`

### Images
- `![center shadow width:600px](path)`
- `![bg right:45% shadow](path)`

## Text & Background Utilities

| Class | Effect |
|-------|--------|
| `text-primary` | Orange |
| `text-accent` | Dark brown |
| `text-success` | Green |
| `text-warning` | Amber |
| `text-danger` | Red/pink |
| `text-sub` | Muted warm gray |
| `text-large` | 1.3× size |
| `text-small` | 0.85× size |
| `bg-pale` | Soft pale orange |
| `bg-light` | Light orange |

## Design Tips

- **Use Emojis**: Blend well with Zen Maru Gothic and warm colors
- **Keep it Light**: Avoid `dense`/`extra-dense` unless necessary
- **Rounded Everything**: Theme uses `border-radius: 12px/24px` — lean into it
- **Friendly Highlights**: Use `<mark>` for inline highlights or badges
