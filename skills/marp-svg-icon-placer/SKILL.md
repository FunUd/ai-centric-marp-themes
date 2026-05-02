---
name: marp-svg-icon-placer
description: ALWAYS activate this skill when placing, copying, or selecting SVG icons in any Marp presentation. Use this skill to select, customize, and insert SVG icons into Marp presentations. It helps maintain visual consistency by pulling from a predefined AI-friendly icon library, adjusting size and color to fit the slide's layout, or generating new cohesive icons if none fit. Must be activated before using any icon copy scripts or referencing the icon catalog.
---

# Marp SVG Icon Placer

This skill helps you appropriately place SVG icons into Marp presentations (`.md` files) to enhance visual appeal and communication without disrupting design consistency.

## 1. Select an Icon
- Always refer to `references/svg-icons-catalog.md` (located in the skill's references directory) for a catalog of available icons.
- Search for an icon that matches the semantic meaning of the content where it will be placed.
- Inside the catalog, you will find the description, usage, and the path to the actual SVG file (e.g., `icons/target.svg`).
- **DO NOT** modify the `svg-icons-catalog.md` file or the SVG files in the `icons/` directory. They are read-only catalogs for your reference.

## 2. Copy Icon to Slide Assets

> **⚠️ IMPORTANT: Never use shell commands** (`Copy-Item`, `cp`, etc.) to copy icons. Use the Python script instead for cross-platform compatibility.

### Using the Copy Script (Recommended)

```python
# Copy specific icons to a project
python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation lightbulb.svg gear.svg

# Copy all icons to a project
python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation all

# List all available icons
python skills/marp-svg-icon-placer/scripts/copy-icons.py --list
```

The script will:
- Copy icons from `skills/marp-svg-icon-placer/references/icons/` to `slides/[project-name]/assets/`
- Verify the project's assets directory exists
- Handle file paths correctly on Windows, macOS, and Linux

### Manual Copy (Alternative)

If you need to copy manually:
- Source: `skills/marp-svg-icon-placer/references/icons/[icon-name].svg`
- Target: `slides/[slide-name]/assets/[icon-name].svg`
- If the `assets/` directory doesn't exist, create it first.
- Example: Copy `references/icons/target.svg` → `slides/my-presentation/assets/target.svg`

## 3. Customize the Icon (Optional)

> **⚠️ IMPORTANT: Never edit SVG color attributes by hand with shell commands** (`sed`, `powershell -replace`, etc.). Use the Python script instead for cross-platform compatibility.

### Changing Icon Colors with the Recolor Script (Recommended)

```python
# Recolor specific icons in a project
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#2563eb" lightbulb.svg gear.svg

# Recolor all icons in a project
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#ffffff" all

# Reset to theme-driven color
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "currentColor" all

# List SVG icons currently in the project's assets directory
python skills/marp-svg-icon-placer/scripts/recolor-icons.py --list-assets my-presentation
```

The script will:
- Replace `fill` and `stroke` color values (both attribute-style and inline-style) in every targeted SVG
- Operate only on copies inside `slides/[project-name]/assets/` — the catalog originals are never touched
- Work identically on Windows, macOS, and Linux

### Manual Color Edit (Alternative)
- If you need to customize the icon (color, size adjustments), edit the copied SVG file in the slide's `assets/` directory:
  - **Size**: Modify `width` and `height` attributes in the SVG file itself.
  - **Color**: Change `fill="currentColor"` to a specific color (e.g., `fill="#2563eb"`).
- Keep the original icon in `references/icons/` unchanged for future reuse.

## 4. Place the Icon — Placement Patterns

Choosing the right placement pattern is critical. Use one of the approved patterns below based on the context:

### Pattern A: Inline with Heading (most common)
Place the icon as an image reference directly inside the heading text.

```markdown
# Slide Title ![icon](./assets/target.svg)
```

- Use `width:28px` or `width:36px` in the image syntax for standard headings: `![icon width:32px](./assets/target.svg)`
- This is the **default pattern** for decorating slide titles.

### Pattern B: Inline with Subheading / List Item
For icons inside `###` subheadings or list items, use standard image syntax.

```markdown
### ![icon](./assets/lightbulb.svg) Section Title
- ![icon](./assets/check.svg) List item with icon
```

- Add size if needed: `![icon width:1em](./assets/check.svg)`
- The icon flows naturally inline with the text.

### Pattern C: Large Centered Icon (feature/column cards)
For column cards (`cols-2`, `cols-3`) where the icon is the visual centerpiece above text, place the image as a standalone element.

```markdown
<div class="col v-center text-center">

![icon width:48px](./assets/database.svg)

### Card Title
Card description text here.

</div>
```

- Use `width:48px` for feature card icons.
- Place the image on its own line with blank lines above and below.

### Pattern D: Background Image with Text Overlay

> **⚠️ IMPORTANT: Do NOT use catalog icons for backgrounds**
> 
> Icons from this catalog are NOT suitable for `bg` usage or any large-scale display that covers more than 30% of the slide area. For backgrounds and large decorative images:
> - Create them using `.drawio.svg` format instead
> - If that's not feasible, ask the user to provide appropriate background images
> - Catalog icons are designed for small inline/decorative use only

For large decorative icons, use Marp's `bg` directive.

```markdown
![bg right:40% opacity:0.1](./assets/cloud-network.svg)

# Slide with Background Icon
Content here appears on the left while the icon serves as a subtle background element.
```

- Adjust `opacity` to make the icon less prominent (typically `0.1` to `0.3`).
- Use `left` or `right` to position the background icon.

## 5. Generate New Icons (Fallback)
- If the catalog does NOT contain a suitable icon for the requested concept, you must generate a new SVG icon.
- **Design Consistency Constraints**:
  - Must match the existing style in `references/icons/` (professional, clean, monotone).
  - Set `width="1em"` and `height="1em"` by default.
  - Set `fill="currentColor"`.
  - Ensure the path data is clean and concise.
- Save the new icon to both locations:
  1. `references/icons/[icon-name].svg` (for the catalog)
  2. `slides/[slide-name]/assets/[icon-name].svg` (for immediate use)
- Add an entry to `references/svg-icons-catalog.md` following the existing format.

## 6. Self-Review Checklist
After placing icons, verify each slide:

- [ ] All icon SVG files are copied to the slide's `assets/` directory
- [ ] Icon references use correct relative paths (e.g., `./assets/icon-name.svg`)
- [ ] Icons in headings use appropriate size (e.g., `width:32px`)
- [ ] Icons in column cards are properly sized (typically `width:48px`)
- [ ] Icon colors match the theme (customize in the SVG file if needed)
- [ ] The `assets/` directory is created if it didn't exist
- [ ] Markdown remains clean and readable without embedded SVG code
