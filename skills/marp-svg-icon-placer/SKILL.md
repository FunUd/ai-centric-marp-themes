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
  - **Spacing/Alignment**: Wrap the SVG in a `<span>` or `<div>` with appropriate classes if you need layout control.

## 3. Place the Icon
- Insert the customized SVG code directly into the Marp markdown file at the intended location.

## 4. Generate New Icons (Fallback)
- If the catalog does NOT contain a suitable icon for the requested concept, you must generate a new SVG icon inline.
- **Design Consistency Constraints**:
  - Must match the existing style in `references/icons/` (professional, clean, monotone).
  - Set `width="1em"` and `height="1em"` by default.
  - Set `fill="currentColor"`.
  - Ensure the path data is clean and concise.
