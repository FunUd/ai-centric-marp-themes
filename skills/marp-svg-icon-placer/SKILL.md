---
name: marp-svg-icon-placer
description: Use this skill to select, customize, and insert SVG icons into Marp presentations. It helps maintain visual consistency by pulling from a predefined AI-friendly icon library, adjusting size and color to fit the slide's layout, or generating new cohesive icons if none fit.
---

# Marp SVG Icon Placer

This skill helps you appropriately place SVG icons into Marp presentations (`.md` files) to enhance visual appeal and communication without disrupting design consistency.

## 1. Select an Icon
- Always refer to `references/svg-icons-catalog.md` (located in the skill's references directory) for a catalog of available icons.
- Search for an icon that matches the semantic meaning of the content where it will be placed.
- Inside the catalog, you will find the description, usage, and the path to the actual SVG file (e.g., `icons/target.svg`). Read the SVG file content when you need to insert it.
- **DO NOT** modify the `svg-icons-catalog.md` file or the SVG files in the `icons/` directory. They are read-only catalogs for your reference.

## 2. Customize the Icon
- Once an icon is selected and its content is read from its file, modify the icon's properties inline to fit the specific slide's context:
  - **Size**: Change `width` and `height` (e.g., from `1em` to `48px`, `2em`, or leaving it as `1em` depending on the layout).
  - **Color**: By default, it uses `fill="currentColor"`. You can change this to a specific color (e.g., `#2563eb` or `var(--color-primary)`) if the design calls for it, or rely on CSS inheritance.

## 3. Place the Icon — Placement Patterns

Choosing the right placement pattern is critical. **Never use `float` or negative `margin-top` to position icons** — these cause icons to escape the slide's layout flow and appear in unexpected positions (e.g., floating in the top-right corner, overlapping the scrollbar area).

Use one of the approved patterns below based on the context:

### Pattern A: Inline with Heading (most common)
Place the icon directly inside the heading text using `vertical-align: middle`. This keeps the icon anchored to the heading and never overflows.

```markdown
# Slide Title <svg ... style="vertical-align:middle;margin-left:8px">...</svg>
```

- Use size `28px`–`36px` for standard headings.
- Always add `margin-left: 8px` to create breathing room between text and icon.
- This is the **default pattern** for decorating slide titles.

### Pattern B: Inline with Subheading / List Item
For icons inside `###` subheadings or list items, use `width="1em" height="1em"` so the icon scales with the text.

```markdown
### <svg width="1em" height="1em" ...>...</svg> Section Title
- <svg width="1em" height="1em" ...>...</svg> List item with icon
```

- Do **not** set explicit `px` sizes here — `1em` ensures the icon matches the surrounding font size.
- No extra `style` attribute needed; the icon flows naturally inline.

### Pattern C: Large Centered Icon (feature/column cards)
For column cards (`cols-2`, `cols-3`) where the icon is the visual centerpiece above text, place the SVG as a standalone block element.

```markdown
<div class="col v-center text-center">

<svg width="48px" height="48px" fill="#2563eb" ...>...</svg>

### Card Title
Card description text here.

</div>
```

- Use `48px` size.
- Place the SVG on its own line with blank lines above and below so Marp treats it as a block.
- Do **not** add any `style` positioning attributes.

### ❌ Forbidden Patterns
Never use these — they break the slide layout and cause overflow or misalignment:

```markdown
<!-- WRONG: float pushes icon outside the layout flow -->
<svg style="float:right; margin-top:-60px">...</svg>

<!-- WRONG: absolute/fixed positioning escapes the slide container -->
<svg style="position:absolute; top:20px; right:20px">...</svg>

<!-- WRONG: negative margins cause unpredictable overlap -->
<svg style="margin-top:-40px">...</svg>
```

## 4. Generate New Icons (Fallback)
- If the catalog does NOT contain a suitable icon for the requested concept, you must generate a new SVG icon inline.
- **Design Consistency Constraints**:
  - Must match the existing style in `references/icons/` (professional, clean, monotone).
  - Set `width="1em"` and `height="1em"` by default.
  - Set `fill="currentColor"`.
  - Ensure the path data is clean and concise.
- After generating a new icon and confirming it renders correctly in the slide, **add it to the catalog** by appending an entry to `references/svg-icons-catalog.md` following the existing format, and save the SVG file to `references/icons/`.

## 5. Self-Review Checklist
After placing icons, verify each slide visually:

- [ ] No icon is floating outside the slide boundary or overlapping the scrollbar
- [ ] Icons in headings use `vertical-align: middle` (Pattern A)
- [ ] Icons in column cards are standalone block elements (Pattern C)
- [ ] No `float`, `position: absolute`, or negative `margin` is used on any icon
- [ ] Icon color matches the theme (use `#2563eb` for Azure Clarity primary blue, or `currentColor` to inherit)
- [ ] Icon size is appropriate for context (1em for inline, 28–36px for titles, 48px for feature cards)
