---
name: marp-svg-icon-placer
description: Activate this skill ONLY when specifically placing, copying, or selecting SVG icons in any Marp presentation.
---

# Marp SVG Icon Placer

This skill helps you appropriately place SVG icons into Marp presentations to enhance visual appeal without disrupting design consistency.

## 1. Select an Icon

**Step 1: Search by keyword first** (avoids loading the full catalog into context):
```powershell
python skills/marp-svg-icon-placer/scripts/copy-icons.py --search "target"
```

**Step 2: If search returns candidates**, use the name directly.
**Step 3: If no match**, run `--list` to see all icons, or refer to `references/svg-icons-catalog.md` for full metadata and usage examples.
- **DO NOT** modify catalog files or SVG files in `icons/` directory


## 2. Copy Icon to Slide Assets

> **⚠️ IMPORTANT: Never use shell commands** (`Copy-Item`, `cp`, etc.). Use the Python script for cross-platform compatibility.

### Using the Copy Script (Recommended)

```python
# Copy specific icons
python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation lightbulb.svg gear.svg

# Copy all icons
python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation all

# List available icons
python skills/marp-svg-icon-placer/scripts/copy-icons.py --list
```

The script copies from `skills/marp-svg-icon-placer/references/icons/` to `slides/[project-name]/assets/`

### Manual Copy (Alternative)

- Source: `skills/marp-svg-icon-placer/references/icons/[icon-name].svg`
- Target: `slides/[slide-name]/assets/[icon-name].svg`
- Create `assets/` directory if needed

## 3. Customize the Icon (Optional)

> **⚠️ IMPORTANT: Never edit SVG colors with shell commands**. Use the Python script for cross-platform compatibility.

### Recolor Script (Recommended)

```python
# Recolor specific icons
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#2563eb" lightbulb.svg gear.svg

# Recolor all icons
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#ffffff" all

# Reset to theme color
python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "currentColor" all

# List icons in project
python skills/marp-svg-icon-placer/scripts/recolor-icons.py --list-assets my-presentation
```

### Manual Color Edit (Alternative)

Edit the copied SVG in `slides/[project-name]/assets/`:
- **Size**: Modify `width` and `height` attributes
- **Color**: Change `fill="currentColor"` to specific color (e.g., `fill="#2563eb"`)
- Keep original in `references/icons/` unchanged

## 4. Placement Patterns

### Pattern A: Inline with Heading (most common)

```markdown
# Slide Title ![icon width:32px](./assets/target.svg)
```

Use `width:28px` or `width:36px` for standard headings. This is the **default pattern**.

### Pattern B: Inline with Subheading / List

```markdown
### ![icon](./assets/lightbulb.svg) Section Title
- ![icon width:1em](./assets/check.svg) List item
```

### Pattern C: Large Centered Icon (feature cards)

```markdown
<div class="col v-center text-center">

![icon width:48px](./assets/database.svg)

### Card Title
Description text

</div>
```

Use `width:48px` for feature card icons. Place on its own line with blank lines.

### Pattern D: Background Image

> **⚠️ IMPORTANT: Do NOT use catalog icons for backgrounds**
> 
> Catalog icons are NOT suitable for `bg` usage or large-scale display (>30% of slide area). For large visuals, hero art, or backgrounds:
> - Create them using `.drawio.svg` format
> - Ask user to provide appropriate background images
> - Catalog icons are for small inline/decorative use only

For large decorative icons (if appropriate):

```markdown
![bg right:40% opacity:0.1](./assets/cloud-network.svg)

# Slide with Background Icon
Content on left
```

Adjust `opacity` to `0.1` to `0.3`. Use `left` or `right` positioning.

## 5. Generate New Icons (Fallback)

If catalog lacks a suitable icon:
- Generate new SVG matching existing style (professional, clean, monotone)
- Set `width="1em"`, `height="1em"`, `fill="currentColor"`
- Save to both:
  1. `references/icons/[icon-name].svg` (catalog)
  2. `slides/[slide-name]/assets/[icon-name].svg` (immediate use)
- Add entry to `references/svg-icons-catalog.md`

## 6. Self-Review Checklist

- [ ] All icon SVG files copied to slide's `assets/` directory
- [ ] Icon references use correct relative paths (e.g., `./assets/icon-name.svg`)
- [ ] Icons in headings use appropriate size (e.g., `width:32px`)
- [ ] Icons in column cards properly sized (typically `width:48px`)
- [ ] Icon colors match theme (customize if needed)
- [ ] `assets/` directory created if didn't exist
- [ ] Markdown remains clean without embedded SVG code
