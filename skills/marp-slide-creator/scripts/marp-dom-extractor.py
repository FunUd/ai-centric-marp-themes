"""Marp DOM Extractor

Extract per-slide DOM metrics from Marp-generated HTML files.
This enables text-only AI models to detect layout risks (overflow, element positioning,
hidden content) without requiring image parsing.

Requires: playwright (pip install playwright)
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: playwright is not installed.")
    print("Install it with: pip install playwright")
    print("Then install browsers: playwright install chromium")
    sys.exit(1)


def extract_slide_metrics(html_path: Path) -> list[dict[str, Any]]:
    """Load a Marp HTML file and extract per-slide metrics using Playwright."""
    absolute_path = html_path.resolve().as_posix()
    file_url = f"file:///{absolute_path}"

    results: list[dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(500)  # Extra buffer for CSS/layout

        # Marp CLI exports sections inside <div class="marpit"> or <body>
        # Each section has inline style with width/height
        slides = page.locator("body > div.marpit > section, body > section").all()
        if not slides:
            slides = page.locator("section").all()

        for idx, slide in enumerate(slides, start=1):
            # Ensure slide is in viewport for accurate sizing
            slide.scroll_into_view_if_needed()

            # Bounding box of the slide itself
            box = slide.bounding_box()
            slide_w = box["width"] if box else 1280
            slide_h = box["height"] if box else 720

            # Extract text statistics
            text_content = slide.inner_text()
            char_count = len(text_content)
            line_count = text_content.count("\n") + 1 if text_content.strip() else 0

            # Extract child elements with metrics
            elements: list[dict[str, Any]] = []
            children = slide.locator("> *").all()
            for child in children:
                child_box = child.bounding_box()
                if not child_box:
                    continue
                tag = child.evaluate("el => el.tagName.toLowerCase()")
                el_data: dict[str, Any] = {
                    "tag": tag,
                    "text_preview": (child.inner_text() or "")[:60],
                    "top": math.ceil(child_box["y"]),
                    "left": math.ceil(child_box["x"]),
                    "width": math.ceil(child_box["width"]),
                    "height": math.ceil(child_box["height"]),
                }

                # Detect hidden / overflow-hidden elements
                overflow = child.evaluate(
                    "el => window.getComputedStyle(el).overflow"
                )
                clip = child.evaluate(
                    "el => { const s = window.getComputedStyle(el); return s.clipPath !== 'none' || s.clip !== 'auto'; }"
                )
                el_data["overflow_style"] = overflow
                el_data["clipped"] = clip
                elements.append(el_data)

            # Compute risk flags
            flags: list[str] = []

            # Slide overflow: total content height exceeds slide height
            if elements:
                max_bottom = max(el["top"] + el["height"] for el in elements)
                if max_bottom > slide_h + 5:  # 5px tolerance
                    flags.append(
                        f"CONTENT_OVERFLOW: content bottom at {max_bottom}px exceeds slide height {slide_h}px"
                    )

            # Dense text risk
            if char_count > 600:
                flags.append(f"DENSE_TEXT: {char_count} chars may overflow")
            if line_count > 20:
                flags.append(f"MANY_LINES: {line_count} lines may overflow")

            # Image missing / broken
            imgs = slide.locator("img").all()
            for img in imgs:
                src = img.get_attribute("src") or ""
                if not src:
                    flags.append(f"IMAGE_NO_SRC: <img> without src")
                else:
                    natural_w = img.evaluate("el => el.naturalWidth")
                    if natural_w == 0:
                        flags.append(f"IMAGE_BROKEN: {src[:40]}")

            results.append(
                {
                    "slide": idx,
                    "slide_size": {"width": slide_w, "height": slide_h},
                    "metrics": {
                        "char_count": char_count,
                        "line_count": line_count,
                        "element_count": len(elements),
                        "image_count": len(imgs),
                    },
                    "elements": elements,
                    "risk_flags": flags,
                }
            )

        browser.close()

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract DOM metrics from Marp HTML files for text-only review."
    )
    parser.add_argument("html_file", help="Path to the Marp-generated HTML file")
    parser.add_argument(
        "-o", "--output", default="-", help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact JSON output (default: pretty-printed)",
    )
    args = parser.parse_args()

    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    data = extract_slide_metrics(html_path)

    indent = None if args.compact else 2
    json_text = json.dumps(data, indent=indent, ensure_ascii=False)

    if args.output == "-":
        print(json_text)
    else:
        Path(args.output).write_text(json_text, encoding="utf-8")
        print(f"Written: {args.output}")


if __name__ == "__main__":
    main()
