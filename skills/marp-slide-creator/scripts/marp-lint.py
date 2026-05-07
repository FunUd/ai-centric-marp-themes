#!/usr/bin/env python3
"""Marp Markdown pre-render linter.

Catches common structural mistakes in Marp Markdown files BEFORE HTML export.
This complements marp-diagnostics.py (which checks rendered output) by finding
issues that cause silent layout failures — the kind that diagnostics cannot
detect because the CSS never activates.

Exit codes:
  0 — no issues
  1 — error (file not found, etc.)
  2 — lint warnings found
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Layout div patterns and their required _class directives
LAYOUT_REQUIREMENTS: dict[str, list[str]] = {
    # div class → any of these _class values must be present
    "columns": ["cols-2", "cols-3", "split-2", "split-3", "split-asym", "split-asym-reverse"],
    "grid": ["grid-quadrant", "grid-sharp"],
    "profile-layout": ["profile"],
}

# Classes that center text — bullet lists are broken on these
CENTERED_CLASSES = {
    "cover", "cover-wave", "cover-diagonal", "cover-noir", "cover-aurora",
    "key-message", "align-center",
}

# Icon file extensions
ICON_EXTENSIONS = {".svg"}

# Max icon size in pixels before it's flagged as too large
# Roughly 30% of 1280px slide width ≈ 384px
ICON_MAX_WIDTH_PX = 200

# Regex patterns
CLASS_DIRECTIVE_RE = re.compile(r"<!--\s*_class:\s*(.+?)\s*-->")
DIV_CLASS_RE = re.compile(r'<div\s+class="([^"]*)"', re.I)
IMG_RE = re.compile(
    r"!\[([^\]]*)\]\(([^)]+)\)",
)
IMG_WIDTH_RE = re.compile(r"width:(\d+)px")
SLIDE_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*[-*+]\s+|^\s*\d+\.\s+", re.MULTILINE)
SCOPED_LIST_OVERRIDE_RE = re.compile(
    r"<style\s+scoped>.*?section\s+(?:ul|ol).*?text-align:\s*left.*?</style>",
    re.S | re.I,
)


@dataclass
class LintWarning:
    slide: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"Slide {self.slide}: [{self.code}] {self.message}"


@dataclass
class SlideInfo:
    number: int
    content: str
    classes: set[str] = field(default_factory=set)
    div_classes: list[str] = field(default_factory=list)
    images: list[tuple[str, str]] = field(default_factory=list)  # (alt, src)
    has_list: bool = False
    has_scoped_list_override: bool = False


def parse_slides(markdown: str) -> list[SlideInfo]:
    """Split Marp markdown into individual slides and extract metadata."""
    # Remove frontmatter
    if markdown.startswith("---"):
        end = markdown.find("---", 3)
        if end != -1:
            markdown = markdown[end + 3:]

    raw_slides = SLIDE_SEPARATOR.split(markdown)
    slides: list[SlideInfo] = []

    for i, raw in enumerate(raw_slides, start=1):
        raw = raw.strip()
        if not raw:
            continue

        slide = SlideInfo(number=i, content=raw)

        # Extract _class directives
        for match in CLASS_DIRECTIVE_RE.finditer(raw):
            classes_str = match.group(1)
            slide.classes = {c.strip() for c in classes_str.split()}

        # Extract div classes
        for match in DIV_CLASS_RE.finditer(raw):
            div_classes_str = match.group(1)
            slide.div_classes.extend(div_classes_str.split())

        # Extract images
        for match in IMG_RE.finditer(raw):
            slide.images.append((match.group(1), match.group(2)))

        # Check for lists
        slide.has_list = bool(LIST_ITEM_RE.search(raw))

        # Check for scoped list alignment override
        slide.has_scoped_list_override = bool(SCOPED_LIST_OVERRIDE_RE.search(raw))

        slides.append(slide)

    return slides


def lint_missing_class_directive(slide: SlideInfo) -> list[LintWarning]:
    """Check for layout divs without matching _class directive."""
    warnings: list[LintWarning] = []

    for div_class, required_classes in LAYOUT_REQUIREMENTS.items():
        if div_class in slide.div_classes:
            if not slide.classes.intersection(required_classes):
                required_str = " / ".join(required_classes)
                warnings.append(LintWarning(
                    slide=slide.number,
                    code="MISSING_CLASS_DIRECTIVE",
                    message=(
                        f'Found <div class="{div_class}"> but no matching '
                        f'<!-- _class: {required_str} --> directive. '
                        f"The layout will NOT activate and content will stack vertically, "
                        f"likely causing overflow."
                    ),
                ))

    return warnings


def lint_centered_lists(slide: SlideInfo) -> list[LintWarning]:
    """Check for bullet/numbered lists on centered-layout slides."""
    warnings: list[LintWarning] = []

    if slide.has_list and slide.classes.intersection(CENTERED_CLASSES):
        if not slide.has_scoped_list_override:
            centered_class = slide.classes.intersection(CENTERED_CLASSES)
            warnings.append(LintWarning(
                slide=slide.number,
                code="CENTERED_LIST",
                message=(
                    f'Slide uses class "{", ".join(centered_class)}" which centers text, '
                    f"but contains bullet/numbered lists. Lists will render centered "
                    f"instead of left-aligned. Move lists to a content slide or add "
                    f"<style scoped> section ul, section ol {{ text-align: left; }} </style>."
                ),
            ))

    return warnings


def lint_oversized_icons(slide: SlideInfo) -> list[LintWarning]:
    """Check for SVG icons used at sizes exceeding 30% of slide area."""
    warnings: list[LintWarning] = []

    for alt, src in slide.images:
        # Skip background images
        if alt.startswith("bg"):
            continue

        src_path = Path(src)
        if src_path.suffix.lower() not in ICON_EXTENSIONS:
            continue

        # Check if it's likely an icon (from assets/ directory, not diagrams)
        src_lower = src.lower()
        if "diagram" in src_lower or "chart" in src_lower:
            continue

        # Check width in alt text
        width_match = IMG_WIDTH_RE.search(alt)
        if width_match:
            width = int(width_match.group(1))
            if width > ICON_MAX_WIDTH_PX:
                warnings.append(LintWarning(
                    slide=slide.number,
                    code="OVERSIZED_ICON",
                    message=(
                        f"SVG icon '{src_path.name}' is used at width:{width}px "
                        f"(max {ICON_MAX_WIDTH_PX}px for icons). "
                        f"Catalog icons are for small inline/decorative use only. "
                        f"For large visuals, use .drawio.svg or a dedicated image."
                    ),
                ))
        elif "center" in alt and "icon" not in alt.lower():
            # Large centered SVG without explicit size — likely too big
            warnings.append(LintWarning(
                slide=slide.number,
                code="OVERSIZED_ICON",
                message=(
                    f"SVG '{src_path.name}' is used as a centered image without "
                    f"size constraint. If this is a catalog icon, it will render "
                    f"at full size (too large). Add width constraint or use a "
                    f"diagram/image file instead."
                ),
            ))

    return warnings


def lint_slide(slide: SlideInfo) -> list[LintWarning]:
    """Run all lint checks on a single slide."""
    warnings: list[LintWarning] = []
    warnings.extend(lint_missing_class_directive(slide))
    warnings.extend(lint_centered_lists(slide))
    warnings.extend(lint_oversized_icons(slide))
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pre-render lint for Marp Markdown files. "
        "Catches structural issues before HTML export."
    )
    parser.add_argument("markdown_file", help="Path to the Marp Markdown file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output warnings as JSON instead of text",
    )
    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"Error: file not found: {md_path}", file=sys.stderr)
        return 1

    markdown = md_path.read_text(encoding="utf-8", errors="ignore")
    slides = parse_slides(markdown)

    all_warnings: list[LintWarning] = []
    for slide in slides:
        all_warnings.extend(lint_slide(slide))

    if args.json:
        import json
        data = [
            {"slide": w.slide, "code": w.code, "message": w.message}
            for w in all_warnings
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        if all_warnings:
            print(f"Found {len(all_warnings)} issue(s):\n")
            for w in all_warnings:
                print(f"  [!] {w}")
            print()
        else:
            print("No structural issues found.")

    return 2 if all_warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
