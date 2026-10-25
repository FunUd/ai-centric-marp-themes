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
- **DO NOT** modify the *installed copy* of catalog files or SVG files in `icons/` during normal slide work. If you are contributing a genuinely new icon to the catalog (Section 5 fallback), adding it to `references/icons/` + `svg-icons-catalog.md` is the documented maintainer exception.


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

The script copies from `skills/marp-svg-icon-placer/references/icons/` to `slides/[project-name]/assets/`. When it copies one or more icons, it also places the required Phosphor license notice at `slides/[project-name]/assets/PHOSPHOR-LICENSE.txt`; include this file when distributing the slide project.

### Manual Copy (Alternative)

- Source: `skills/marp-svg-icon-placer/references/icons/[icon-name].svg`
- Target: `slides/[slide-name]/assets/[icon-name].svg`
- Also copy `skills/marp-svg-icon-placer/references/icons/LICENSE` to `slides/[slide-name]/assets/PHOSPHOR-LICENSE.txt` and include it when distributing the slide project.
- Create `assets/` directory if needed

## 3. Customize the Icon (Optional)

> **⚠️ Dark themes (e.g. nebula-glass):** icons copied with `fill="currentColor"` render nearly black and invisible on dark headings. Always recolor to a light tone immediately after copying.
> ```powershell
> python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#67E8F9" all
> ```

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

> **⚠️ Raw inline HTML:** Markdown image syntax `![...]` is NOT parsed inside a single-line HTML block (e.g. `<h4>`, callout headings) — the alt text renders literally. Use `<img>` instead.
> ```markdown
> <!-- NG: renders as literal text -->
> <h4>Title ![icon](./assets/lightbulb.svg)</h4>
>
> <!-- OK -->
> <h4>Title <img src="./assets/lightbulb.svg" width="16" alt=""></h4>
> ```

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

### Pattern D: Background / Large Visual

> **🚨 HARD RULE: Catalog icons MUST NOT exceed width:200px, and MUST NOT be used as `![bg ...]` backgrounds — with one narrow exception below.**
>
> Catalog icons are designed for small inline/decorative use ONLY:
> - **Headings**: `width:28px` to `width:36px`
> - **List items**: `width:1em`
> - **Feature cards**: `width:48px`
> - **Maximum**: `width:200px` (absolute ceiling — no exceptions)
>
> **NEVER** use a catalog icon as:
> - A hero/feature image (e.g., `width:300px` centered on slide)
> - Any element covering >15% of slide area
>
> For large visuals, hero art, or backgrounds:
> - Create them using `.drawio.svg` format
> - Ask the user to provide appropriate images
> - Use `generate_image` tool if available

Exception — subtle decorative watermark only (opacity ≤ 0.15, never a content carrier):

```markdown
![bg right:40% opacity:0.1](./assets/cloud-network.svg)

# Slide with Background Icon
Content on left
```

Adjust `opacity` to `0.1` to `0.15`. Use `left` or `right` positioning.

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
- [ ] `PHOSPHOR-LICENSE.txt` included when distributing copied catalog icons
- [ ] Icon references use correct relative paths (e.g., `./assets/icon-name.svg`)
- [ ] Icons in headings use appropriate size (e.g., `width:32px`)
- [ ] Icons in column cards properly sized (typically `width:48px`)
- [ ] Icon colors match theme (customize if needed)
- [ ] `assets/` directory created if didn't exist
- [ ] Markdown remains clean without embedded SVG code
