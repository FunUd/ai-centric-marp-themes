---
name: theme-creator
description: Activate this skill when the user wants to create a new Marp CSS theme from scratch or based on an existing theme. Covers the full workflow from design concept through CSS implementation, theme-expert skill generation, and sample slide creation. Trigger when the user mentions creating a new theme, designing a theme, adding a new color scheme, or building a custom Marp theme.
---

# Theme Creator

A comprehensive guide for creating new Marp CSS themes in this project.
This skill covers the entire workflow: design concept → CSS implementation → theme-expert skill → sample slides → documentation.

## When to Use

- User wants to create a brand-new Marp theme
- User wants to fork/adapt an existing theme with significant changes
- User wants to add a new color scheme or visual identity to the collection

## Phase 1: Design Concept

Before writing any CSS, establish the theme's identity with the user.

### 1.1 Gather Requirements

Ask the user about:

1. **Theme name** — Should be two-word, kebab-case (e.g., `azure-clarity`, `nebula-glass`, `prism-edge`)
2. **Visual tone** — Professional/corporate, creative/artistic, dark/moody, warm/friendly, futuristic/tech
3. **Base model** — Start from an existing theme or build from the shared foundation?
4. **Color palette** — Primary, accent, text, background, and semantic colors (success/warning/danger)
5. **Typography** — System fonts or custom fonts? Japanese support needed?
6. **Special features** — Unique cover styles, custom layouts, glassmorphism, gradients, etc.
7. **Target audience** — Business presentations, tech talks, creative pitches, education, etc.

### 1.2 Define the Color System

Every theme must define these CSS variable categories:

| Category | Variables | Purpose |
|----------|-----------|---------|
| Primary | `primary`, `primary-dark`, `primary-light`, `primary-pale` | Brand color in multiple tones |
| Text | `text`, `text-sub` | Main and secondary text colors |
| Background | `white`/`bg` | Slide background |
| Border | `border`, `border-light` | Separators and card edges |
| Semantic | `success`, `warning`, `danger` | Callout and badge colors |
| Effects | `shadow`, `radius`, `radius-lg` | Shadows and corner radii |

Use a consistent prefix for all variables: `--xx-` (2-letter theme abbreviation, e.g., `--ac-` for azure-clarity, `--pe-` for prism-edge).

### 1.3 Choose Typography

**System fonts approach** (like Azure Clarity, Crimson Clarity):
```css
font-family: 'Segoe UI', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans JP', sans-serif;
```

**Custom fonts approach** (like Prism Edge, Nebula Glass):
- Requires `@font-face` declarations at the top of the CSS
- Font files stored in `assets/fonts/`
- Use themed font-family names (e.g., `'Prism Grotesk'`, `'Nebula Header'`)
- Always include a Japanese font fallback

## Phase 2: CSS Architecture

### 2.1 File Structure

Create the theme at `themes/<theme-name>.css`. The file must follow this exact section order:

```
1.  /* @theme <theme-name> */
2.  @import 'default';
3.  @font-face declarations (if custom fonts)
4.  :root { CSS Variables }
5.  Base Slide (section)
6.  Typography (h1-h6, p, a)
7.  Lists (ul, ol, li, markers)
8.  Table (thead, tbody, hover)
9.  Code & Blockquote (code, pre, blockquote)
10. Syntax Highlighting (hljs classes)
11. Text Emphasis (strong, em, mark)
12. Images (img, center, shadow)
13. Header & Footer (header, footer)
14. Pagination (section::after)
15. Utility: Header/Footer/Pagination control
16. Cover Slide (section.cover, .subtitle, .meta)
17. Theme-specific cover variants (if any)
18. TOC (section.toc)
19. TOC Focus (section.toc-focus)
20. Column Layouts (cols-2, cols-3)
21. Split Layouts (split-2, split-3)
22. Grid Quadrant (grid-quadrant)
23. Grid Sharp (grid-sharp)
24. Timetable
25. Steps
26. Profile
27. Key Message
28. Content Density (dense, extra-dense)
29. Timeline
30. Checklist
31. Callouts (blue, green, orange, red)
32. Badges
33. Alignment Utilities
34. Highlight / Text color utilities
35. Theme-specific unique classes (if any)
```

### 2.2 Critical Rules

These are non-negotiable requirements that every theme must satisfy:

1. **Slide dimensions**: Always `width: 1280px; height: 720px;`
2. **Theme declaration**: First line must be `/* @theme <theme-name> */`
3. **Import default**: Second line must be `@import 'default';`
4. **Overflow hidden**: `section` must have `overflow: hidden;`
5. **Flex column**: `section` must use `display: flex; flex-direction: column;`
6. **Pagination content**: Must use `content: attr(data-marpit-pagination) ' / ' attr(data-marpit-pagination-total);`
7. **Header padding**: `section:has(header)` and `section.with-header` must adjust `padding-top`
8. **Callout colors**: Must use `blue`, `green`, `orange`, `red` class names (not semantic names like info/success/warning/danger)
9. **Syntax highlighting**: Must override `--color-prettylights-syntax-*` variables AND provide `.hljs-*` class overrides for `pre code`

### 2.3 Shared Layout Classes (Required)

Every theme **must** implement these layout classes to remain compatible with the shared `theme-expert-common` skill. **Read the existing CSS files for the exact implementation pattern**—do not deviate from the established HTML structure.

**Required classes:**
- `cover` (with `subtitle` and `meta` modifiers)
- `toc`, `toc-focus`
- `cols-2`, `cols-3` (with `> div.columns` and `.col`)
- `split-2`, `split-3` (with `> div.columns`)
- `grid-quadrant`, `grid-sharp` (with `> div.grid` and `.cell`)
- `timetable`
- `steps`
- `profile` (with `.profile-layout`, `.profile-image`, `.profile-content`)
- `key-message`
- `dense`, `extra-dense`
- `timeline`
- `checklist`
- Callouts (`.callout.blue`, `.callout.green`, `.callout.orange`, `.callout.red`)
- Badges (`.badge`, `.badge.blue`, `.badge.green`, `.badge.orange`, `.badge.red`)
- Alignment (`text-left/center/right`, `align-left/center/right`, `v-top/center/bottom`)
- Display control (`no-header`, `no-footer`, `no-pagination`, `pagination-left`, `with-header`)
- Text utilities (`text-blue`, `text-accent`, `text-green`, `text-orange`, `text-red`, `text-sub`, `text-large`, `text-small`)
- Background utilities (`bg-pale`, `bg-light`)

### 2.4 Building from an Existing Theme

When forking from an existing theme (recommended for consistency):

1. Copy the base CSS file
2. Replace the theme comment: `/* @theme new-name */`
3. Replace all CSS variable prefixes (e.g., `--ac-` → `--nt-`)
4. Update the color palette in `:root`
5. Adjust typography, cover styles, and any unique features
6. Add theme-specific classes if needed

> **Tip**: Azure Clarity and Crimson Clarity are the simplest bases (system fonts, straightforward layouts). Prism Edge and Nebula Glass are more advanced (custom fonts, complex cover variants, unique classes).

## Phase 3: Theme-Expert Skill

After the CSS is ready, create a matching `theme-expert-<theme-name>` skill so the AI can properly use the theme during slide creation.

### 3.1 Skill File

Create `skills/theme-expert-<theme-name>/SKILL.md`:

```markdown
---
name: theme-expert-<theme-name>
description: Activate this skill ONLY when the Marp implementation phase has begun and the <Theme Name> theme has already been chosen. DO NOT activate during outlining.
---

# <Theme Name> Theme Expert

<One-sentence description of the theme's personality and best use cases.>

Use this skill after the content structure is decided. For outline planning or story shaping, use `slide-content-designer` or the relevant domain skill first.

## What <Theme Name> Is Best For

- <Use case 1>
- <Use case 2>
- <Use case 3>

## <Theme Name>-Specific Cues

- <Cover class usage guidance>
- <Unique class usage>
- <Tone and style guidance>
- <Any theme-specific patterns>

## Shared Mechanics

For the exact syntax of the shared Marp patterns, read `theme-expert-common` only when the slide needs one of these:

- Cover and title layout
- TOC and agenda layout
- Columns, grids, density, profile, key message
- Steps, timeline, checklist, timetable
- Callouts, alignment, and image placement

## Design Tips

- <Tip 1>
- <Tip 2>
- <Tip 3>
```

### 3.2 Skill Design Guidelines

- Keep the SKILL.md concise (30-50 lines is ideal)
- Focus on what makes this theme **different** from others
- Document any theme-specific classes not covered by `theme-expert-common`
- Explain the design philosophy in 1-2 sentences
- Reference `theme-expert-common` for shared patterns instead of duplicating instructions

## Phase 4: Sample Slides

Create a comprehensive sample slide deck at `slides/sample-slide/<theme-name>-sample.md`.

### 4.1 Sample Slide Requirements

The sample must demonstrate **all** major layout classes:

1. Cover slide (with subtitle and meta)
2. TOC or TOC Focus
3. Regular content slide (h1 + bullet points)
4. Two-column layout (`cols-2`)
5. Three-column layout (`cols-3`)
6. Grid quadrant (`grid-quadrant`)
7. Steps layout
8. Timeline
9. Profile
10. Key message
11. Callouts (at least 2 colors)
12. Table
13. Code block
14. Dense content slide
15. Any theme-specific unique layouts

### 4.2 Sample Content Language

- Use Japanese text for sample content (consistent with existing samples)
- Include realistic, domain-appropriate content (not lorem ipsum)

## Phase 5: Verification

### 5.1 Pre-verification Checklist

Before considering the theme complete, verify:

- [ ] CSS file is at `themes/<theme-name>.css`
- [ ] First line is `/* @theme <theme-name> */`
- [ ] All required layout classes are implemented
- [ ] Callouts use color-based class names (`blue`, `green`, `orange`, `red`)
- [ ] Syntax highlighting variables AND hljs overrides are present
- [ ] `theme-expert-<theme-name>` skill exists in `skills/`
- [ ] Sample slide exists at `slides/sample-slide/<theme-name>-sample.md`
- [ ] Sample slide renders without errors:
  ```powershell
  python skills/marp-slide-creator/scripts/marp-lint.py slides/sample-slide/<theme-name>-sample.md
  ```

### 5.2 Visual Verification

Export and visually check the sample slides:

```powershell
npx -y @marp-team/marp-cli --no-stdin --allow-local-files --theme themes/<theme-name>.css slides/sample-slide/<theme-name>-sample.md -o slides/sample-slide/preview.html
```

### 5.3 Sync Skills

After creating the theme-expert skill, sync it to all agent directories:

```powershell
python scripts/sync-skills.py
```

## Phase 6: Documentation

Update `README.md` to include the new theme:

1. Add a theme description in the Themes section
2. Add screenshot previews (if available)
3. Update any theme count references

## Quick Reference: CSS Variable Naming

| Theme | Prefix | Example |
|-------|--------|---------|
| Azure Clarity | `--ac-` | `--ac-primary: #2C7BE5` |
| Crimson Clarity | `--cc-` | `--cc-primary: #DC2626` |
| Prism Edge | `--pe-` | `--pe-primary: #4F46E5` |
| Warm Sunnyday | `--ws-` | `--ws-primary: #F59E0B` |
| Nebula Glass | `--ng-` | `--ng-primary: #7C3AED` |

When creating a new theme, choose a unique 2-letter prefix that doesn't conflict with existing ones.
