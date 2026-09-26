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
import json
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

# Class semantics live in scripts/diagrams/theme_classes.py and are shipped as
# a generated manifest, because this file is copied standalone into agent
# directories and cannot import from scripts/. Regenerate with:
#     python scripts/diagrams/sync-theme-classes.py
THEME_CLASSES_PATH = Path(__file__).resolve().parent / "theme-classes.json"


def _load_theme_classes() -> dict:
    try:
        data = json.loads(THEME_CLASSES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(
            f"[ERROR] Cannot read theme class manifest: {THEME_CLASSES_PATH}\n"
            f"        {error}\n"
            f"        Regenerate: python scripts/diagrams/sync-theme-classes.py",
            file=sys.stderr,
        )
        raise SystemExit(1) from error
    return data


_THEME_CLASSES = _load_theme_classes()

# Title and single-message layouts, where a bullet list is a design error.
LIST_UNSUITABLE_CLASSES = set(_THEME_CLASSES["list_unsuitable"])

# Layouts where a generic heading is intended (covers, title slides, TOCs).
EXEMPT_TITLE_CLASSES = set(_THEME_CLASSES["title_exempt"])

# Layouts where many list items are structural, not a readability problem.
LIST_EXEMPT_CLASSES = set(_THEME_CLASSES["list_exempt"])

# Max icon size in pixels before it's flagged as too large
ICON_MAX_WIDTH_PX = 200

# Readability thresholds
MAX_RECOMMENDED_BULLETS = 4   # single-column bullet limit; see BULLET_MAX_PER_LAYOUT
MIN_LABELLED_CHARS = 35       # bullet length above which a bold key label is expected
UNLABELLED_LIST_MIN = 2       # report once this many long bullets lack labels
MAX_RECOMMENDED_CHARS = 400   # total plain text chars before DENSE_CONTENT

# Layout class -> diagram width budget (px), from the generated manifest.
# Canonical values: scripts/diagrams/layout_spec.py::CANVAS_MAX
DIAGRAM_LAYOUT_MAX_WIDTHS: dict[str, int] = {
    "full":  1120,   # full-width single column
    "col2":  520,    # 2-column layouts
    "col3":  340,    # 3-column layouts
    "asym":  710,    # asymmetric split
}

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
CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
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

    for raw in raw_slides:
        raw = raw.strip()
        if not raw:
            continue

        # Number by emitted slide, not by split index: a blank slide between two
        # `---` separators must not shift every later number, or the reported
        # slide no longer matches the section index Marp and the DOM extractor
        # use for the same deck.
        slide = SlideInfo(number=len(slides) + 1, raw_content=raw)

        # Strip fenced code blocks before analysis to avoid false positives
        # (e.g. SVG paths inside code examples triggering diagram/icon checks)
        raw_no_code = CODE_FENCE_RE.sub("", raw)

        # Extract _class directives
        for match in CLASS_DIRECTIVE_RE.finditer(raw_no_code):
            classes_str = match.group(1)
            slide.classes.update(c.strip() for c in classes_str.split())

        # Extract div classes
        for match in DIV_CLASS_RE.finditer(raw_no_code):
            div_classes_str = match.group(1)
            slide.div_classes.extend(div_classes_str.split())

        # Extract images (code-stripped to avoid false positives from code examples)
        for match in IMG_RE.finditer(raw_no_code):
            slide.images.append((match.group(1), match.group(2)))

        # Extract headings
        for match in HEADING_RE.finditer(raw_no_code):
            slide.headings.append(match.group(2).strip())

        # Extract list items (code-stripped to avoid counting code-block lines)
        for match in LIST_ITEM_RE.finditer(raw_no_code):
            slide.list_items.append(match.group(2).strip())

        # Plain text length calculation (use original raw for accurate char count)
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
    """Check for bullet/numbered lists on title and single-message layouts.

    These layouts exist to land one idea. A list either renders as centred dots
    or dilutes the message, so it is flagged either way — including on themes
    that deliberately left-align their covers.
    """
    issues: list[LintIssue] = []
    if slide.list_items and not slide.has_scoped_list_override:
        unsuitable = slide.classes.intersection(LIST_UNSUITABLE_CLASSES)
        if unsuitable:
            issues.append(LintIssue(
                slide=slide.number,
                severity="ERROR",
                code="CENTERED_LIST",
                message=(
                    f'Slide uses class "{", ".join(sorted(unsuitable))}", a title or '
                    f"single-message layout that does not suit a bullet list: the list "
                    f"either renders centered or dilutes the message. Move the list to a "
                    f"standard content slide, or add a scoped left-align override."
                ),
            ))
    return issues


def lint_oversized_icons(slide: SlideInfo) -> list[LintIssue]:
    """Check for SVG icons used at sizes exceeding 200px.

    Diagrams are skipped via the same predicate `lint_diagram_embedding` uses.
    They previously were skipped on a narrower, hard-coded pair of keywords
    ("diagram", "chart"), so a diagram named `assets/flow.svg` was classified as
    an icon here while being classified as a diagram there — producing a false
    `OVERSIZED_ICON` ERROR on a correct `width:500px` two-column embed.
    """
    issues: list[LintIssue] = []
    for alt, src in slide.images:
        if alt.startswith("bg"):
            continue

        src_path = Path(src)
        if src_path.suffix.lower() not in {".svg"}:
            continue

        if _is_diagram_src(src):
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


# ---------------------------------------------------------------------------
# Diagram classification and layout resolution
#
# Shared by lint_oversized_icons and lint_diagram_embedding so a file can never
# be an icon to one check and a diagram to the other.
# ---------------------------------------------------------------------------

# Keywords that identify a path as a diagram (not an icon)
DIAGRAM_PATH_KEYWORDS = frozenset(
    ["diagram", "chart", "flow", "arch", "seq", "state", "drawio", "mmd", "render"]
)


def _is_diagram_src(src: str) -> bool:
    """Return True when the image source looks like a rendered diagram (not an icon)."""
    src_lower = src.lower()
    return any(kw in src_lower for kw in DIAGRAM_PATH_KEYWORDS)


# Layout class -> layout profile, from the generated manifest (which sources
# scripts/diagrams/layout_spec.py::CLASS_TO_LAYOUT). One definition, so the
# diagram width budget and the bullet-count budget can never disagree.
DIAGRAM_LAYOUT_CLASSES: dict[str, str] = dict(_THEME_CLASSES["diagram_layout"])
_LAYOUT_CLASSES: dict[str, set[str]] = {}
for _cls, _profile in DIAGRAM_LAYOUT_CLASSES.items():
    _LAYOUT_CLASSES.setdefault(_profile, set()).add(_cls)


# Narrowest profile first: when a slide carries several layout classes the
# tightest constraint is the one that must hold. `asym` (710px) is wider than
# `col2` (520px), so col2 wins over asym when both appear.
_LAYOUT_PRIORITY = ("col3", "col2", "asym")


def _slide_layout_key(slide: SlideInfo) -> str:
    """Infer the applicable layout constraint key from the slide's _class directives."""
    for profile in _LAYOUT_PRIORITY:
        if slide.classes.intersection(_LAYOUT_CLASSES.get(profile, ())):
            return profile
    return "full"


def lint_diagram_embedding(slide: SlideInfo) -> list[LintIssue]:
    """Check diagram images for missing width, oversized width, and centered-layout placement.

    Checks:
    - DIAGRAM_MISSING_WIDTH (WARNING): Diagram SVG embedded without explicit width:NNNpx.
    - DIAGRAM_OVERFLOW_WIDTH (ERROR):  Diagram width exceeds the max for the slide layout.
    - DIAGRAM_ON_CENTERED_LAYOUT (WARNING): Diagram placed on a centered layout
      (cover, key-message, etc.) where it may render oddly.
    """
    issues: list[LintIssue] = []

    layout_key = _slide_layout_key(slide)
    max_width = DIAGRAM_LAYOUT_MAX_WIDTHS[layout_key]

    for alt, src in slide.images:
        # Skip background images
        if alt.startswith("bg"):
            continue

        src_path = Path(src)

        # Skip non-SVG files (diagrams are always exported as SVG)
        if src_path.suffix.lower() != ".svg":
            continue

        # Only process paths that look like diagrams
        if not _is_diagram_src(src):
            continue

        width_match = IMG_WIDTH_RE.search(alt)

        # --- Check 1: missing width on diagram ---
        if not width_match:
            issues.append(LintIssue(
                slide=slide.number,
                severity="WARNING",
                code="DIAGRAM_MISSING_WIDTH",
                message=(
                    f"Diagram '{src_path.name}' is embedded without a width constraint "
                    f"(e.g. width:900px). Without it the diagram may expand to full slide "
                    f"width and push other content off the slide. "
                    f"Recommended max for '{layout_key}' layout: {max_width}px."
                ),
            ))
        else:
            # --- Check 2: width exceeds layout max ---
            width = int(width_match.group(1))
            if width > max_width:
                issues.append(LintIssue(
                    slide=slide.number,
                    severity="ERROR",
                    code="DIAGRAM_OVERFLOW_WIDTH",
                    message=(
                        f"Diagram '{src_path.name}' width:{width}px exceeds the safe maximum "
                        f"for '{layout_key}' layout ({max_width}px). "
                        f"This will cause horizontal overflow or push content off the slide. "
                        f"Reduce to width:{max_width}px or less."
                    ),
                ))

        # --- Check 3: diagram on a title / single-message layout ---
        unsuitable = slide.classes.intersection(LIST_UNSUITABLE_CLASSES)
        if unsuitable:
            issues.append(LintIssue(
                slide=slide.number,
                severity="WARNING",
                code="DIAGRAM_ON_CENTERED_LAYOUT",
                message=(
                    f"Diagram '{src_path.name}' is placed on a title or single-message "
                    f"layout (class: '{', '.join(sorted(unsuitable))}'). A diagram needs "
                    f"a content slide with room to breathe; here it will be cramped or "
                    f"misaligned. Use a standard content slide, or a cols-2 layout with "
                    f"the diagram in one column."
                ),
            ))

    return issues


# ==========================================
# 2. Content & Readability Checks (Severity: WARNING)
# ==========================================

# Max bullets per layout profile (3 per column, 4 for a single column).
# Keyed by the same layout profile used for diagram widths, so the two checks
# can never disagree about what counts as a 2- or 3-column slide.
BULLET_MAX_PER_LAYOUT: dict[str, int] = {
    "full": 4,
    "col2": 6,
    "asym": 6,   # 65/35 split still has two text columns
    "col3": 9,
}


def lint_bullet_hell(slide: SlideInfo) -> list[LintIssue]:
    """Check for bullet point overload (Magic Number 3 violation)."""
    issues: list[LintIssue] = []
    # On checklists / steps / timelines / TOCs many items are the structure.
    if slide.classes.intersection(LIST_EXEMPT_CLASSES):
        return issues

    count = len(slide.list_items)
    max_allowed = BULLET_MAX_PER_LAYOUT[_slide_layout_key(slide)]

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
        # If not labeled and text length is substantial
        if not is_labeled and len(item) > MIN_LABELLED_CHARS:
            unlabeled_long_items += 1

    if unlabeled_long_items >= UNLABELLED_LIST_MIN:
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
                f"Slide body has ~{slide.plain_text_len} plain characters "
                f"(recommended {int(MAX_RECOMMENDED_CHARS * 0.5)}-{int(MAX_RECOMMENDED_CHARS * 0.875)} max). "
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
    issues.extend(lint_diagram_embedding(slide))

    # Readability checks (Warnings)
    if not structural_only:
        issues.extend(lint_bullet_hell(slide))
        issues.extend(lint_weak_title(slide))
        issues.extend(lint_unlabeled_list(slide))
        issues.extend(lint_dense_content(slide))

    return issues


def main() -> int:
    # Windows consoles default to cp932; emit UTF-8 so Japanese text/paths don't crash.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass  # stream replaced by a test harness or not reconfigurable
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
