#!/usr/bin/env python3
"""
Marp Theme Screenshot Script
Generates HTML with Marp CLI and captures each slide with Playwright.

Usage:
  # Capture every configured screenshot for one theme
  python scripts/take-screenshots.py nebula-glass
  python scripts/take-screenshots.py prism-edge
  python scripts/take-screenshots.py azure-clarity
  python scripts/take-screenshots.py crimson-clarity
  python scripts/take-screenshots.py slate-minimal
  python scripts/take-screenshots.py warm-sunnyday
  python scripts/take-screenshots.py all

  # List which themes have configured screenshots
  python scripts/take-screenshots.py --list-themes

  # Specify a slide file and slide numbers directly (1-based)
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md 1
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md 1 5 10
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md all

  # Specify output directory
  python scripts/take-screenshots.py --slide slides/foo.md 1 --output assets/my-shots

  # Check slide count only
  python scripts/take-screenshots.py --list slides/sample-slide/nebula-glass-sample.md
"""

import argparse
import re
import subprocess
import sys
import os
import tempfile
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:  # --list-themes / --list need no browser
    sync_playwright = None  # type: ignore[assignment]


def _require_playwright():
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium "
            "(offline modes --list-themes work without it)."
        )
    return sync_playwright

# The pinned Node tool versions live with the diagram engine.
sys.path.insert(0, str(Path(__file__).resolve().parent / "diagrams"))
from tool_versions import npx_command  # noqa: E402
from compat import ensure_utf8_stdio  # noqa: E402

MARP_CLI = "@marp-team/marp-cli"

ensure_utf8_stdio()

WORKSPACE = Path(__file__).parent.parent
THEME_DIR = WORKSPACE / "themes"
OUTPUT_DIR = WORKSPACE / "assets/screenshots"

# CSS to hide slide control UI elements injected by Marp bespoke.js
# Targets: navigation bar, progress bar, presenter overlay
HIDE_CONTROLS_CSS = """
  /* bespoke navigation bar */
  .bespoke-marp-osc,
  /* progress bar */
  .bespoke-progress-parent,
  /* presenter notes overlay */
  .bespoke-marp-presenter-view,
  /* any fixed/absolute UI injected by bespoke */
  [class*="bespoke-marp-osc"],
  [class*="bespoke-progress"] {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
  }
"""

# Per-theme screenshot configuration
# Each entry: (output filename, screenshot id).
# The id resolves through a `<!-- screenshot: <id> -->` marker placed as the
# first line of its slide in the sample deck — the deck is the SSoT for *which*
# slide is captured, this table only decides the output filename. Inserting a
# slide shifts no indices because there are no indices here.
THEME_CONFIG = {
    "nebula-glass": {
        "slide": WORKSPACE / "slides/sample-slide/nebula-glass-sample.md",
        "screenshots": [
            ("nebula-glass-cover.png",    "cover"),   # cover-nebula
            ("nebula-glass-toc.png",      "toc"),     # toc
            ("nebula-glass-cols.png",     "cols"),    # cols-2
            ("nebula-glass-grid.png",     "grid"),    # grid-quadrant
            ("nebula-glass-timeline.png", "timeline"),# timeline
            ("nebula-glass-callout.png",  "callout"), # callout
            ("nebula-glass-step.png",     "step"),    # steps
        ],
    },
    "prism-edge": {
        "slide": WORKSPACE / "slides/sample-slide/prism-edge-sample.md",
        "screenshots": [
            ("prism-edge-cover-wave.png",     "cover-wave"),      # cover-wave
            ("prism-edge-cover-diagonal.png", "cover-diagonal"),  # cover-diagonal
            ("prism-edge-cover-noir.png",     "cover-noir"),      # cover-noir
            ("prism-edge-cover-aurora.png",   "cover-aurora"),    # cover-aurora
            ("prism-edge-title-elegant.png",  "title-elegant"),   # title-elegant
            ("prism-edge-accent.png",         "accent"),          # accent-left
            ("prism-edge-cols.png",           "cols"),            # cols-2
            ("prism-edge-grid.png",           "grid"),            # grid-sharp
            ("prism-edge-callout.png",        "callout"),         # callout (with-header dense)
            ("prism-edge-gradnum.png",        "gradnum"),         # hero / gradient-text
            ("prism-edge-statnum.png",        "statnum"),         # split-2 / stat-number
            ("prism-edge-cover-aurora-end.png", "cover-aurora-end"),  # cover-aurora closing
        ],
    },
    "azure-clarity": {
        "slide": WORKSPACE / "slides/sample-slide/azure-clarity-sample.md",
        "screenshots": [
            ("azure-clarity-cover.png",    "cover"),     # cover
            ("azure-clarity-toc.png",      "toc"),       # toc
            ("azure-clarity-toc-focus.png","toc-focus"), # toc-focus
            ("azure-clarity-bullets.png",  "bullets"),   # with-header bullet list
            ("azure-clarity-table.png",    "table"),     # table
            ("azure-clarity-cols2.png",    "cols2"),     # cols-2
            ("azure-clarity-cols3.png",    "cols3"),     # cols-3
            ("azure-clarity-steps.png",    "steps"),     # steps
            ("azure-clarity-timeline.png", "timeline"),  # timeline
            ("azure-clarity-checklist.png","checklist"), # checklist
            ("azure-clarity-callout.png",  "callout"),   # callout (dense)
            ("azure-clarity-keymsg.png",   "keymsg"),    # key-message
            ("azure-clarity-grid.png",     "grid"),      # grid-quadrant
            ("azure-clarity-profile.png",  "profile"),   # profile
        ],
    },
    "crimson-clarity": {
        "slide": WORKSPACE / "slides/sample-slide/crimson-clarity-sample.md",
        "screenshots": [
            ("crimson-clarity-cover.png",    "cover"),     # cover
            ("crimson-clarity-toc.png",      "toc"),       # toc
            ("crimson-clarity-toc-focus.png","toc-focus"), # toc-focus
            ("crimson-clarity-bullets.png",  "bullets"),   # with-header bullet list
            ("crimson-clarity-table.png",    "table"),     # table
            ("crimson-clarity-cols2.png",    "cols2"),     # cols-2
            ("crimson-clarity-cols3.png",    "cols3"),     # cols-3
            ("crimson-clarity-steps.png",    "steps"),     # steps
            ("crimson-clarity-timeline.png", "timeline"),  # timeline
            ("crimson-clarity-checklist.png","checklist"), # checklist
            ("crimson-clarity-callout.png",  "callout"),   # callout (dense)
            ("crimson-clarity-keymsg.png",   "keymsg"),    # key-message
            ("crimson-clarity-grid.png",     "grid"),      # grid-quadrant
            ("crimson-clarity-profile.png",  "profile"),   # profile
        ],
    },
    "slate-minimal": {
        "slide": WORKSPACE / "slides/sample-slide/slate-minimal-sample.md",
        "screenshots": [
            ("slate-minimal-cover.png",       "cover"),       # cover
            ("slate-minimal-agenda.png",      "agenda"),      # toc-focus
            ("slate-minimal-profile.png",     "profile"),     # profile
            ("slate-minimal-grid.png",        "grid"),        # grid-sharp
            ("slate-minimal-cols.png",        "cols"),        # split-2
            ("slate-minimal-callout.png",     "callout"),     # cols-3 + callouts
            ("slate-minimal-timeline.png",    "timeline"),    # timeline
            ("slate-minimal-key-message.png", "key-message"), # key-message
        ],
    },
    "warm-sunnyday": {
        "slide": WORKSPACE / "slides/sample-slide/warm-sunnyday-sample.md",
        "screenshots": [
            ("warm-sunnyday-cover.png",    "cover"),    # cover
            ("warm-sunnyday-profile.png",  "profile"),  # profile
            ("warm-sunnyday-cols.png",     "cols"),     # cols-2
            ("warm-sunnyday-steps.png",    "steps"),    # steps
            ("warm-sunnyday-callouts.png", "callouts"), # callout (dense)
        ],
    },
}


SCREENSHOT_MARKER_RE = re.compile(r"<!--\s*screenshot:\s*([\w-]+)\s*-->")


def slide_marker_indices(slide_md: Path) -> dict[str, int]:
    """Map screenshot id -> 0-based slide index for a deck.

    Slide N is the content after the Nth post-frontmatter ``---`` separator
    (slide 0 sits between the frontmatter close and the first separator), so
    markers travel with their slide when slides are inserted or removed.
    Fenced code blocks are ignored. Duplicate ids raise RuntimeError.
    """
    lines = slide_md.read_text(encoding="utf-8").splitlines()
    idx = [i for i, line in enumerate(lines) if line.strip() == "---"]
    first = idx[1] + 1 if len(idx) > 1 and idx[0] == 0 else 0
    markers: dict[str, int] = {}
    current = 0
    in_fence = False
    for line in lines[first:]:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == "---":
            current += 1
            continue
        match = SCREENSHOT_MARKER_RE.search(line)
        if match:
            marker_id = match.group(1)
            if marker_id in markers:
                raise RuntimeError(
                    f"Duplicate screenshot id '{marker_id}' in {slide_md.name}"
                )
            markers[marker_id] = current
    return markers


def resolve_screenshots(
    slide_md: Path, entries: list[tuple[str, str]]
) -> list[tuple[str, int]]:
    """Resolve (filename, screenshot id) entries to (filename, 0-based index).

    Raises RuntimeError naming the missing id — a renamed or deleted marker
    fails loudly instead of capturing the wrong slide.
    """
    markers = slide_marker_indices(slide_md)
    resolved: list[tuple[str, int]] = []
    for filename, marker_id in entries:
        if marker_id not in markers:
            raise RuntimeError(
                f"Screenshot id '{marker_id}' for {filename} not found in "
                f"{slide_md.name}: the marker was renamed or deleted"
            )
        resolved.append((filename, markers[marker_id]))
    return resolved


def build_html(slide_md: Path, output_html: Path):
    """Generate HTML from a Marp Markdown file using Marp CLI."""
    print(f"  📄 Generating HTML: {slide_md.name} ...")
    # argv list, not a shell string: deck paths legitimately contain spaces and
    # brackets, and a shell would also re-interpret any metacharacter in them.
    cmd = [
        *npx_command(MARP_CLI, str(slide_md)),
        "--output", str(output_html),
        "--html",
        "--theme-set", str(THEME_DIR),
        "--allow-local-files",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            cwd=str(WORKSPACE),
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Marp CLI timed out after 300s") from error
    except OSError as error:
        raise RuntimeError(f"Failed to launch Marp CLI: {error}") from error
    if result.returncode != 0:
        raise RuntimeError(f"Marp CLI error:\n{result.stderr}")
    print(f"  ✅ HTML generated")


def hide_controls(page):
    """Hide the bespoke navigation bar, progress bar, and any hover UI.
    Re-applied after each slide transition to prevent re-appearance.
    """
    page.add_style_tag(content=HIDE_CONTROLS_CSS)
    # Move mouse off-screen to dismiss any hover-triggered UI
    page.mouse.move(-100, -100)
    page.wait_for_timeout(300)


def take_screenshots(theme_name: str, html_path: Path, screenshots: list, output_dir: Path = None):
    """Capture screenshots for the given slides using Playwright.

    Marp bespoke presentation mode uses keyboard navigation, so we advance
    slides with ArrowRight key presses rather than direct DOM manipulation.
    """
    out_dir = output_dir or OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sort by slide index so we always move forward (no back-navigation needed)
    sorted_shots = sorted(screenshots, key=lambda x: x[1])

    playwright = _require_playwright()
    with playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            url = html_path.resolve().as_uri()
            page.goto(url, wait_until="load")
            page.wait_for_timeout(1200)  # Wait for bespoke.js initialization

            # Detect total slide count (prefer <section id=...> over <svg>)
            slide_count = page.evaluate(
                "() => { "
                "  const sections = document.querySelectorAll('section[id]'); "
                "  if (sections.length > 0) return sections.length; "
                "  return document.querySelectorAll('svg').length; "
                "}"
            )
            print(f"  📊 Total slides: {slide_count}")

            # Click body to ensure keyboard focus
            page.click("body")
            page.wait_for_timeout(200)

            # Hide control UI before starting
            hide_controls(page)

            current_index = 0

            for filename, slide_index in sorted_shots:
                if slide_index >= slide_count:
                    print(f"  ⚠️  Slide {slide_index + 1} does not exist (total: {slide_count})")
                    continue

                # Advance from current position to target slide using ArrowRight
                steps = slide_index - current_index
                for _ in range(steps):
                    page.keyboard.press("ArrowRight")
                    page.wait_for_timeout(150)

                current_index = slide_index

                # Re-apply control hiding after transition (bespoke may re-inject UI)
                hide_controls(page)

                out_path = out_dir / filename
                page.screenshot(path=str(out_path))
                print(f"  📸 {filename} (slide {slide_index + 1}/{slide_count})")
        finally:
            if browser is not None:
                browser.close()


def count_markdown_slides(slide_md: Path) -> int:
    """Count slides from the Markdown source (no browser required).

    Marp splits on a line containing only ``---``. With frontmatter the first
    two separators are the frontmatter fences, so slide count == separators - 1.
    Fenced code blocks and ``...`` frontmatter closes are ignored.
    """
    text = slide_md.read_text(encoding="utf-8")
    separators = 0
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == "---":
            separators += 1
    if separators == 0:
        return 1
    # A leading frontmatter block consumes the first separator pair.
    has_frontmatter = text.lstrip().startswith("---")
    return max(separators - (1 if has_frontmatter else 0), 1)


def report_theme_registry() -> list[str]:
    """Print the screenshot registry and validate every screenshot id.

    Beyond the old range check this now catches the failure modes markers
    exist to prevent: a renamed/deleted marker, a duplicate id, and a marker
    with no registry entry (which would silently stop being captured).
    Returns a list of problems.
    """
    problems: list[str] = []
    total = 0

    for theme in sorted(THEME_CONFIG):
        config = THEME_CONFIG[theme]
        slide_md = Path(config["slide"])
        if not slide_md.is_file():
            problems.append(f"{theme}: sample deck not found: {slide_md}")
            print(f"❌ {theme}: sample deck not found: {slide_md}")
            continue

        try:
            markers = slide_marker_indices(slide_md)
        except (OSError, RuntimeError) as error:
            problems.append(f"{theme}: cannot read markers: {error}")
            print(f"❌ {theme}: cannot read markers: {error}")
            continue

        slide_count = count_markdown_slides(slide_md)
        referenced = {marker_id for _, marker_id in config["screenshots"]}
        for marker_id in sorted(set(markers) - referenced):
            problems.append(
                f"{theme}: marker '{marker_id}' in {slide_md.name} "
                f"(slide {markers[marker_id] + 1}) has no registry entry"
            )
        print(f"\n{theme}  ({slide_md.name}: {slide_count} slides, {len(config['screenshots'])} screenshots)")
        try:
            resolved = resolve_screenshots(slide_md, config["screenshots"])
        except RuntimeError as error:
            problems.append(f"{theme}: {error}")
            print(f"  ❌ {error}")
            continue
        for (filename, marker_id), (_, index) in zip(config["screenshots"], resolved):
            total += 1
            in_range = 0 <= index < slide_count
            if not in_range:
                problems.append(
                    f"{theme}: {filename} (id '{marker_id}') resolves to slide index {index} "
                    f"but the deck has {slide_count} slides"
                )
            marker = "  " if in_range else "❌"
            print(f"  {marker} {filename:38} id '{marker_id}' -> slide {index + 1} of {slide_count}")

    print(f"\n{total} screenshots across {len(THEME_CONFIG)} themes")
    if problems:
        print("\n❌ Problems:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("✅ All screenshot ids resolve to slides in range")
    return problems


def list_slide_count(slide_md: Path):
    """Print the total number of slides in a Marp Markdown file."""
    slide_md = WORKSPACE / slide_md if not slide_md.is_absolute() else slide_md
    if not slide_md.exists():
        raise RuntimeError(f"File not found: {slide_md}")

    playwright = _require_playwright()
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_html = Path(tmp.name)
    try:
        build_html(slide_md, temp_html)
        with playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                page.goto(temp_html.resolve().as_uri(), wait_until="load")
                page.wait_for_timeout(1200)
                slide_count = page.evaluate(
                    "() => { "
                    "  const sections = document.querySelectorAll('section[id]'); "
                    "  if (sections.length > 0) return sections.length; "
                    "  return document.querySelectorAll('svg').length; "
                    "}"
                )
            finally:
                if browser is not None:
                    browser.close()
        print(f"📊 {slide_md.name}: {slide_count} slides")
    finally:
        if temp_html.exists():
            temp_html.unlink()


def take_ad_hoc_screenshots(slide_md: Path, slide_numbers, output_dir: Path):
    """Capture screenshots by specifying a slide file and slide numbers directly.

    slide_numbers: list of 1-based integers, or the string "all".
    Output filenames are auto-generated as <stem>-slide-<NNN>.png.
    """
    slide_md = WORKSPACE / slide_md if not slide_md.is_absolute() else slide_md
    if not slide_md.exists():
        raise RuntimeError(f"File not found: {slide_md}")

    playwright = _require_playwright()
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_html = Path(tmp.name)
    print(f"\n{'='*50}")
    print(f"  File: {slide_md.name}")
    print(f"{'='*50}")

    try:
        build_html(slide_md, temp_html)

        # Detect total slide count first
        with playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                page.goto(temp_html.resolve().as_uri(), wait_until="load")
                page.wait_for_timeout(1200)
                slide_count = page.evaluate(
                    "() => { "
                    "  const sections = document.querySelectorAll('section[id]'); "
                    "  if (sections.length > 0) return sections.length; "
                    "  return document.querySelectorAll('svg').length; "
                    "}"
                )
            finally:
                if browser is not None:
                    browser.close()

        # Build list of 0-based indices
        if slide_numbers == "all":
            indices = list(range(slide_count))
        else:
            indices = []
            for n in slide_numbers:
                idx = n - 1  # Convert 1-based to 0-based
                if idx < 0 or idx >= slide_count:
                    print(f"  ⚠️  Slide {n} is out of range (total: {slide_count}). Skipping.")
                else:
                    indices.append(idx)

        if not indices:
            print("  ⚠️  No valid slides to capture.")
            return

        stem = slide_md.stem
        screenshots = [(f"{stem}-slide-{idx + 1:03d}.png", idx) for idx in indices]

        take_screenshots(stem, temp_html, screenshots, output_dir)

    finally:
        if temp_html.exists():
            temp_html.unlink()
            print(f"  🧹 Removed temp file: {temp_html.name}")


def process_theme(theme_name: str, output_dir: Path = None):
    """Capture all configured screenshots for a single theme."""
    if theme_name not in THEME_CONFIG:
        raise RuntimeError(
            f"Unknown theme: {theme_name}. Available: {', '.join(THEME_CONFIG.keys())}"
        )

    config = THEME_CONFIG[theme_name]
    try:
        screenshots = resolve_screenshots(Path(config["slide"]), config["screenshots"])
    except (OSError, RuntimeError) as error:
        raise RuntimeError(str(error)) from error
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        temp_html = Path(tmp.name)

    print(f"\n{'='*50}")
    print(f"  Theme: {theme_name}")
    print(f"{'='*50}")

    try:
        build_html(config["slide"], temp_html)
        take_screenshots(theme_name, temp_html, screenshots, output_dir)
    finally:
        if temp_html.exists():
            temp_html.unlink()
            print(f"  🧹 Removed temp file: {temp_html.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Capture screenshots of Marp slides",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture all screenshots for a theme
  python scripts/take-screenshots.py nebula-glass
  python scripts/take-screenshots.py all

  # Specify slide file and slide numbers (1-based)
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md 1
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md 1 5 10
  python scripts/take-screenshots.py --slide slides/sample-slide/nebula-glass-sample.md all

  # Specify output directory
  python scripts/take-screenshots.py --slide slides/foo.md 1 --output assets/my-shots

  # Check slide count only
  python scripts/take-screenshots.py --list slides/sample-slide/nebula-glass-sample.md
        """,
    )

    parser.add_argument(
        "theme",
        nargs="?",
        help=f"Theme name ({' / '.join(sorted(THEME_CONFIG))} / all)",
    )
    parser.add_argument(
        "--slide",
        metavar="FILE",
        help="Path to a Marp Markdown file (relative to workspace root or absolute)",
    )
    parser.add_argument(
        "slide_numbers",
        nargs="*",
        help="Slide numbers to capture (1-based). Use 'all' for every slide. Only valid with --slide.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="DIR",
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--list", "-l",
        metavar="FILE",
        help="Print the total slide count for a file and exit",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="Print the screenshot registry (theme, slide count, entries) and "
             "verify every screenshot id resolves. Exits 1 if any entry is invalid.",
    )

    args = parser.parse_args()

    # argparse fills the leading optional `theme` positional before
    # `slide_numbers`, so with --slide the first trailing token would be
    # swallowed (e.g. `--slide deck.md all` -> theme="all", numbers=[]).
    # In slide mode theme is meaningless: pull that token back.
    if args.slide and args.theme is not None:
        args.slide_numbers.insert(0, args.theme)
        args.theme = None

    return parser, args


if __name__ == "__main__":
    parser, args = parse_args()

    # Resolve output directory (relative paths are relative to workspace root)
    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    if args.output and not output_dir.is_absolute():
        output_dir = WORKSPACE / output_dir

    try:
        # --list mode: print slide count and exit
        if args.list:
            list_slide_count(Path(args.list))
            sys.exit(0)

        # --list-themes mode: report the screenshot registry and its integrity
        if args.list_themes:
            missing = report_theme_registry()
            sys.exit(1 if missing else 0)

        # --slide mode: ad-hoc capture by file + slide numbers
        if args.slide:
            raw_numbers = args.slide_numbers
            if not raw_numbers:
                print("❌ Specify slide numbers (1-based) or 'all' when using --slide.")
                print("   e.g. python scripts/take-screenshots.py --slide slides/foo.md 1 3 5")
                print("   e.g. python scripts/take-screenshots.py --slide slides/foo.md all")
                sys.exit(1)

            if len(raw_numbers) == 1 and raw_numbers[0].lower() == "all":
                slide_numbers = "all"
            else:
                try:
                    slide_numbers = [int(n) for n in raw_numbers]
                except ValueError:
                    print(f"❌ Slide numbers must be integers or 'all': {raw_numbers}")
                    sys.exit(1)

            take_ad_hoc_screenshots(Path(args.slide), slide_numbers, output_dir)
            print("\n✅ Done!")
            sys.exit(0)

        # Theme mode: capture all configured screenshots for a theme
        target = args.theme
        if not target:
            parser.print_help()
            sys.exit(1)

        if target == "all":
            failed: list[str] = []
            for theme in THEME_CONFIG:
                try:
                    process_theme(theme, output_dir)
                except RuntimeError as error:
                    print(f"❌ {theme}: {error}")
                    failed.append(theme)
            if failed:
                print(f"\n❌ Failed themes: {', '.join(failed)}")
                sys.exit(1)
        elif target in THEME_CONFIG:
            process_theme(target, output_dir)
        else:
            print(f"❌ Unknown theme: {target}")
            print(f"   Available: {', '.join(sorted(THEME_CONFIG))}, all")
            sys.exit(1)

        print("\n✅ Done!")
    except RuntimeError as error:
        print(f"❌ {error}")
        sys.exit(1)
