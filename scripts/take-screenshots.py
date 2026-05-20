#!/usr/bin/env python3
"""
Marp Theme Screenshot Script
Generates HTML with Marp CLI and captures each slide with Playwright.

Usage:
  # Capture all screenshots for a theme
  python scripts/take-screenshots.py nebula-glass
  python scripts/take-screenshots.py prism-edge
  python scripts/take-screenshots.py azure-clarity
  python scripts/take-screenshots.py crimson-clarity
  python scripts/take-screenshots.py all

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
import subprocess
import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

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
# Each entry: (output filename, slide index, 0-based)
THEME_CONFIG = {
    "nebula-glass": {
        "slide": WORKSPACE / "slides/sample-slide/nebula-glass-sample.md",
        "screenshots": [
            ("nebula-glass-cover.png",    0),   # cover-nebula
            ("nebula-glass-toc.png",      7),   # toc
            ("nebula-glass-cols.png",     11),  # cols-2
            ("nebula-glass-grid.png",     13),  # grid-quadrant
            ("nebula-glass-timeline.png", 9),   # timeline
            ("nebula-glass-callout.png",  17),  # callout
            ("nebula-glass-step.png",     4),   # steps
        ],
    },
    "prism-edge": {
        "slide": WORKSPACE / "slides/sample-slide/prism-edge-sample.md",
        "screenshots": [
            ("prism-edge-cover-wave.png",     0),   # cover-wave
            ("prism-edge-cover-diagonal.png", 1),   # cover-diagonal
            ("prism-edge-cover-noir.png",     2),   # cover-noir
            ("prism-edge-title-elegant.png",  8),   # title-elegant
            ("prism-edge-cols.png",           15),  # cols-2
            ("prism-edge-grid.png",           17),  # grid-sharp
            ("prism-edge-callout.png",        21),  # callout (with-header dense)
            ("prism-edge-gradnum.png",        22),  # hero / gradient-text
            ("prism-edge-statnum.png",        11),  # split-2 / stat-number
        ],
    },
    "azure-clarity": {
        "slide": WORKSPACE / "slides/sample-slide/azure-clarity-sample.md",
        "screenshots": [
            ("azure-clarity-cover.png",    0),   # cover
            ("azure-clarity-toc.png",      1),   # toc
            ("azure-clarity-toc-focus.png",2),   # toc-focus
            ("azure-clarity-bullets.png",  3),   # with-header bullet list
            ("azure-clarity-table.png",    4),   # table
            ("azure-clarity-cols2.png",    5),   # cols-2
            ("azure-clarity-cols3.png",    6),   # cols-3
            ("azure-clarity-steps.png",    14),  # steps
            ("azure-clarity-timeline.png", 15),  # timeline
            ("azure-clarity-checklist.png",16),  # checklist
            ("azure-clarity-callout.png",  17),  # callout (dense)
            ("azure-clarity-keymsg.png",   18),  # key-message
            ("azure-clarity-grid.png",     11),  # grid-quadrant
            ("azure-clarity-profile.png",  29),  # profile
        ],
    },
    "crimson-clarity": {
        "slide": WORKSPACE / "slides/sample-slide/crimson-clarity-sample.md",
        "screenshots": [
            ("crimson-clarity-cover.png",    0),   # cover
            ("crimson-clarity-toc.png",      1),   # toc
            ("crimson-clarity-toc-focus.png",2),   # toc-focus
            ("crimson-clarity-bullets.png",  3),   # with-header bullet list
            ("crimson-clarity-table.png",    4),   # table
            ("crimson-clarity-cols2.png",    5),   # cols-2
            ("crimson-clarity-cols3.png",    6),   # cols-3
            ("crimson-clarity-steps.png",    14),  # steps
            ("crimson-clarity-timeline.png", 15),  # timeline
            ("crimson-clarity-checklist.png",16),  # checklist
            ("crimson-clarity-callout.png",  17),  # callout (dense)
            ("crimson-clarity-keymsg.png",   18),  # key-message
            ("crimson-clarity-grid.png",     11),  # grid-quadrant
            ("crimson-clarity-profile.png",  29),  # profile
        ],
    },
}


def build_html(slide_md: Path, output_html: Path):
    """Generate HTML from a Marp Markdown file using Marp CLI."""
    print(f"  📄 Generating HTML: {slide_md.name} ...")
    cmd = (
        f'npx @marp-team/marp-cli "{slide_md}" '
        f'--output "{output_html}" '
        f'--html --theme-set "{THEME_DIR}" --allow-local-files'
    )
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE), shell=True)
    if result.returncode != 0:
        print(f"  ❌ Marp CLI error:\n{result.stderr}")
        sys.exit(1)
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

    with sync_playwright() as p:
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

        browser.close()


def list_slide_count(slide_md: Path):
    """Print the total number of slides in a Marp Markdown file."""
    slide_md = WORKSPACE / slide_md if not slide_md.is_absolute() else slide_md
    if not slide_md.exists():
        print(f"❌ File not found: {slide_md}")
        sys.exit(1)

    temp_html = WORKSPACE / "_list_temp.html"
    try:
        build_html(slide_md, temp_html)
        with sync_playwright() as p:
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
        print(f"❌ File not found: {slide_md}")
        sys.exit(1)

    temp_html = WORKSPACE / "_adhoc_temp.html"
    print(f"\n{'='*50}")
    print(f"  File: {slide_md.name}")
    print(f"{'='*50}")

    try:
        build_html(slide_md, temp_html)

        # Detect total slide count first
        with sync_playwright() as p:
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
        print(f"❌ Unknown theme: {theme_name}")
        print(f"   Available: {', '.join(THEME_CONFIG.keys())}")
        sys.exit(1)

    config = THEME_CONFIG[theme_name]
    temp_html = WORKSPACE / f"_{theme_name}_temp.html"

    print(f"\n{'='*50}")
    print(f"  Theme: {theme_name}")
    print(f"{'='*50}")

    try:
        build_html(config["slide"], temp_html)
        take_screenshots(theme_name, temp_html, config["screenshots"], output_dir)
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
        help="Theme name (nebula-glass / prism-edge / azure-clarity / crimson-clarity / all)",
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

    return parser, parser.parse_args()


if __name__ == "__main__":
    parser, args = parse_args()

    # Resolve output directory (relative paths are relative to workspace root)
    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    if args.output and not output_dir.is_absolute():
        output_dir = WORKSPACE / output_dir

    # --list mode: print slide count and exit
    if args.list:
        list_slide_count(Path(args.list))
        sys.exit(0)

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
        for theme in THEME_CONFIG:
            process_theme(theme, output_dir)
    else:
        process_theme(target, output_dir)

    print("\n✅ Done!")
