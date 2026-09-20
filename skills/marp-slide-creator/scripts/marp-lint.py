#!/usr/bin/env python3
"""Marp Markdown pre-render linter.

Catches common structural mistakes and readability anti-patterns in Marp Markdown files.
- Structural issues: silent layout failures, broken directives, centered lists, oversized icons.
- Readability issues: bullet point overload, weak/topic-only titles, dense text walls, unlabeled lists.

Exit codes:
  0 — clean (no errors/warnings)
  1 — file error (not found, etc.)
  2 — lint issues found (errors, or warnings with --strict)
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Layout div patterns and their required _class directives
LAYOUT_REQUIREMENTS: dict[str, list[str]] = {
    "columns": ["cols-2", "cols-3", "split-2", "split-3", "split-asym", "split-asym-reverse"],
    "grid": ["grid-quadrant", "grid-sharp"],
    "profile-layout": ["profile"],
}

# Classes that center text — bullet lists are broken on these
CENTERED_CLASSES = {
    "cover", "cover-wave", "cover-diagonal", "cover-noir", "cover-aurora",
    "key-message", "align-center",
}

# Classes that are title-only or special, exempt from WEAK_TITLE checks
EXEMPT_TITLE_CLASSES = {
    "cover", "cover-wave", "cover-diagonal", "cover-noir", "cover-aurora",
    "toc", "toc-focus", "key-message", "hero", "title-only", "title-elegant",
}

# Max icon size in pixels before it's flagged as too large
ICON_MAX_WIDTH_PX = 200

# Readability thresholds
MAX_RECOMMENDED_BULLETS = 5  # >= 5 items triggers BULLET_HELL
MAX_RECOMMENDED_CHARS = 400  # Total plain text chars before DENSE_CONTENT warning

# Regex patterns
CLASS_DIRECTIVE_RE = re.compile(r"<!--\s*_class:\s*(.+?)\s*-->")
DIV_CLASS_RE = re.compile(r'<div\s+class="([^"]*)"', re.I)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMG_WIDTH_RE = re.compile(r"width:(\d+)px")
SLIDE_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+(.+)$", re.MULTILINE)
SCOPED_LIST_OVERRIDE_RE = re.compile(
    r"<style\s+scoped>.*?section\s+(?:ul|ol).*?text-align:\s*left.*?</style>",
    re.S | re.I,
)
HEADING_RE = re.compile(r"^\s*(#{1,3})\s+(.+)$", re.MULTILINE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")

# Topic-only / generic title keywords (So What? missing)
WEAK_TITLE_PATTERNS = [
    # Japanese patterns
    r"^.*(について|の概要|のまとめ|の現状|の検討)$",
    r"^(概要|まとめ|アジェンダ|目次|背景|課題|対策|アーキテクチャ|システム構成|導入事例|今後の展望|質疑応答|QA)$",
    # English patterns
    r"^(overview|summary|agenda|background|architecture|system overview|next steps|conclusion|introduction|q&a)$",
]
WEAK_TITLE_REGEXES = [re.compile(p, re.I) for p in WEAK_TITLE_PATTERNS]


@dataclass
class LintIssue:
    slide: int
    severity: str  # "ERROR" or "WARNING"
    code: str
    message: str

    def __str__(self) -> str:
        icon = "🚨" if self.severity == "ERROR" else "⚠️"
        return f"Slide {self.slide} [{self.severity} - {self.code}]: {self.message}"


@dataclass
class SlideInfo:
    number: int
    raw_content: str
    classes: set[str] = field(default_factory=set)
    div_classes: list[str] = field(default_factory=list)
    images: list[tuple[str, str]] = field(default_factory=list)  # (alt, src)
    list_items: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    plain_text_len: int = 0
    has_scoped_list_override: bool = False


def extract_plain_text(markdown: str) -> str:
    """Extract readable text by stripping comments, styles, and HTML tags."""
    text = COMMENT_RE.sub("", markdown)
    text = STYLE_RE.sub("", text)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    # Remove markdown formatting characters
    text = re.sub(r"[#*_`~\[\]\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_slides(markdown: str) -> list[SlideInfo]:
    """Split Marp markdown into individual slides and extract metadata."""
    # Remove YAML frontmatter
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

        slide = SlideInfo(number=i, raw_content=raw)

        # Extract _class directives
        for match in CLASS_DIRECTIVE_RE.finditer(raw):
            classes_str = match.group(1)
            slide.classes.update(c.strip() for c in classes_str.split())

        # Extract div classes
        for match in DIV_CLASS_RE.finditer(raw):
            div_classes_str = match.group(1)
            slide.div_classes.extend(div_classes_str.split())

        # Extract images
        for match in IMG_RE.finditer(raw):
            slide.images.append((match.group(1), match.group(2)))

        # Extract headings
        for match in HEADING_RE.finditer(raw):
            slide.headings.append(match.group(2).strip())

        # Extract list items
        for match in LIST_ITEM_RE.finditer(raw):
            slide.list_items.append(match.group(2).strip())

        # Plain text length calculation
        plain = extract_plain_text(raw)
        slide.plain_text_len = len(plain)

        # Check for scoped list alignment override
        slide.has_scoped_list_override = bool(SCOPED_LIST_OVERRIDE_RE.search(raw))

        slides.append(slide)

    return slides


# ==========================================
# 1. Structural Lint Checks (Severity: ERROR)
# ==========================================

def lint_missing_class_directive(slide: SlideInfo) -> list[LintIssue]:
    """Check for layout divs without matching _class directive."""
    issues: list[LintIssue] = []
    for div_class, required_classes in LAYOUT_REQUIREMENTS.items():
        if div_class in slide.div_classes:
            if not slide.classes.intersection(required_classes):
                required_str = " / ".join(required_classes)
                issues.append(LintIssue(
                    slide=slide.number,
                    severity="ERROR",
                    code="MISSING_CLASS_DIRECTIVE",
                    message=(
                        f'Found <div class="{div_class}"> without matching '
                        f'<!-- _class: {required_str} --> directive. '
                        f"Layout will NOT activate and content will stack vertically."
                    ),
                ))
    return issues


def lint_centered_lists(slide: SlideInfo) -> list[LintIssue]:
    """Check for bullet/numbered lists on centered-layout slides."""
    issues: list[LintIssue] = []
    if slide.list_items and slide.classes.intersection(CENTERED_CLASSES):
        if not slide.has_scoped_list_override:
            centered = slide.classes.intersection(CENTERED_CLASSES)
            issues.append(LintIssue(
                slide=slide.number,
                severity="ERROR",
                code="CENTERED_LIST",
                message=(
                    f'Slide uses class "{", ".join(centered)}" which centers text, '
                    f"causing bullet lists to render centered instead of left-aligned. "
                    f"Move lists to a standard content slide or add scoped left alignment."
                ),
            ))
    return issues


def lint_oversized_icons(slide: SlideInfo) -> list[LintIssue]:
    """Check for SVG icons used at sizes exceeding 200px."""
    issues: list[LintIssue] = []
    for alt, src in slide.images:
        if alt.startswith("bg"):
            continue

        src_path = Path(src)
        if src_path.suffix.lower() not in {".svg"}:
            continue

        src_lower = src.lower()
        if "diagram" in src_lower or "chart" in src_lower:
            continue

        width_match = IMG_WIDTH_RE.search(alt)
        if width_match:
            width = int(width_match.group(1))
            if width > ICON_MAX_WIDTH_PX:
                issues.append(LintIssue(
                    slide=slide.number,
                    severity="ERROR",
                    code="OVERSIZED_ICON",
                    message=(
                        f"SVG icon '{src_path.name}' is used at width:{width}px "
                        f"(max {ICON_MAX_WIDTH_PX}px for icons). Icons are for small "
                        f"inline/card accents. For large visuals, use diagrams."
                    ),
                ))
        elif "center" in alt and "icon" not in alt.lower():
            issues.append(LintIssue(
                slide=slide.number,
                severity="ERROR",
                code="OVERSIZED_ICON",
                message=(
                    f"SVG '{src_path.name}' is centered without a width constraint. "
                    f"Catalog icons will render too large. Specify width:48px or similar."
                ),
            ))
    return issues


# ==========================================
# 2. Content & Readability Checks (Severity: WARNING)
# ==========================================

def lint_bullet_hell(slide: SlideInfo) -> list[LintIssue]:
    """Check for bullet point overload (Magic Number 3 violation)."""
    issues: list[LintIssue] = []
    # If the slide uses 'checklist' or 'timetable', multiple items are natural
    if "checklist" in slide.classes or "timetable" in slide.classes:
        return issues

    count = len(slide.list_items)
    
    # Adapt threshold for multi-column layouts (each column can cleanly hold 3 items)
    is_3col = bool(slide.classes.intersection({"cols-3", "split-3"}))
    is_2col = bool(slide.classes.intersection({"cols-2", "split-2", "split-asym", "split-asym-reverse"}))

    if is_3col:
        max_allowed = 9  # 3 per column
    elif is_2col:
        max_allowed = 6  # 3 per column
    else:
        max_allowed = 4  # single column

    if count > max_allowed:
        issues.append(LintIssue(
            slide=slide.number,
            severity="WARNING",
            code="BULLET_HELL",
            message=(
                f"Slide contains {count} bullet points (recommended max is {max_allowed} for this layout). "
                f"High cognitive load: consider reducing items, converting to steps/timeline, "
                f"or splitting across multiple slides."
            ),
        ))
    return issues


def lint_weak_title(slide: SlideInfo) -> list[LintIssue]:
    """Check for generic topic-only headings lacking conclusion/takeaway."""
    issues: list[LintIssue] = []
    if slide.classes.intersection(EXEMPT_TITLE_CLASSES):
        return issues

    for heading in slide.headings:
        # Strip badge tags if present: <span class="...">Badge</span> Title
        clean_heading = TAG_RE.sub("", heading).strip()

        for pattern in WEAK_TITLE_REGEXES:
            if pattern.search(clean_heading):
                issues.append(LintIssue(
                    slide=slide.number,
                    severity="WARNING",
                    code="WEAK_TITLE",
                    message=(
                        f"Heading '{clean_heading}' appears to be a generic topic noun. "
                        f"State the conclusion or takeaway (So What?) directly in the title "
                        f"(e.g., instead of 'Architecture', use 'Microservices reduce deploy time by 60%')."
                    ),
                ))
                break
    return issues


def lint_unlabeled_list(slide: SlideInfo) -> list[LintIssue]:
    """Check for long bullet items lacking bold key labels."""
    issues: list[LintIssue] = []
    if not slide.list_items:
        return issues

    unlabeled_long_items = 0
    for item in slide.list_items:
        # Check if item starts with bold text like **Label**: or **[Label]**
        is_labeled = item.startswith("**") or item.startswith("<b>") or item.startswith("<strong>")
        # If not labeled and text length is substantial (> 35 chars)
        if not is_labeled and len(item) > 35:
            unlabeled_long_items += 1

    if unlabeled_long_items >= 2:
        issues.append(LintIssue(
            slide=slide.number,
            severity="WARNING",
            code="UNLABELED_LIST",
            message=(
                f"Found {unlabeled_long_items} long bullet items without bold key labels. "
                f"Structure bullets with bold labels (e.g., `- **[Key Label]**: Brief explanation`) "
                f"so the audience can scan in under 3 seconds."
            ),
        ))
    return issues


def lint_dense_content(slide: SlideInfo) -> list[LintIssue]:
    """Check for excessive text density per slide."""
    issues: list[LintIssue] = []
    if "dense" in slide.classes or "extra-dense" in slide.classes:
        return issues

    if slide.plain_text_len > MAX_RECOMMENDED_CHARS:
        issues.append(LintIssue(
            slide=slide.number,
            severity="WARNING",
            code="DENSE_CONTENT",
            message=(
                f"Slide body has ~{slide.plain_text_len} plain characters (recommended 200-350 max). "
                f"Excess text reduces presentation impact. Trim filler words, move background "
                f"to presenter notes (<!-- ... -->), or split the slide."
            ),
        ))
    return issues


def lint_slide(slide: SlideInfo, structural_only: bool = False) -> list[LintIssue]:
    """Run all lint checks on a single slide."""
    issues: list[LintIssue] = []
    # Structural checks (Errors)
    issues.extend(lint_missing_class_directive(slide))
    issues.extend(lint_centered_lists(slide))
    issues.extend(lint_oversized_icons(slide))

    # Readability checks (Warnings)
    if not structural_only:
        issues.extend(lint_bullet_hell(slide))
        issues.extend(lint_weak_title(slide))
        issues.extend(lint_unlabeled_list(slide))
        issues.extend(lint_dense_content(slide))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pre-render structural and readability linter for Marp Markdown files."
    )
    parser.add_argument("markdown_file", help="Path to the Marp Markdown file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output issues as JSON",
    )
    parser.add_argument(
        "--structural-only",
        action="store_true",
        help="Only check structural CSS errors, ignore readability warnings",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat readability warnings as failures (exit code 2)",
    )
    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"Error: file not found: {md_path}", file=sys.stderr)
        return 1

    markdown = md_path.read_text(encoding="utf-8", errors="ignore")
    slides = parse_slides(markdown)

    all_issues: list[LintIssue] = []
    for slide in slides:
        all_issues.extend(lint_slide(slide, structural_only=args.structural_only))

    errors = [i for i in all_issues if i.severity == "ERROR"]
    warnings = [i for i in all_issues if i.severity == "WARNING"]

    if args.json:
        import json
        data = [
            {
                "slide": i.slide,
                "severity": i.severity,
                "code": i.code,
                "message": i.message,
            }
            for i in all_issues
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        if all_issues:
            print(f"Found {len(all_issues)} issue(s) ({len(errors)} error(s), {len(warnings)} warning(s)):\n")
            for issue in all_issues:
                print(f"  {issue}")
            print()
        else:
            print("No structural or readability issues found. Excellent slide quality! ✨")

    # Exit code determination
    if errors:
        return 2
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
