"""Marp DOM Extractor

Extract per-slide DOM metrics from Marp-generated HTML files.
This enables text-only AI models to detect layout risks (overflow, element positioning,
hidden content) without requiring image parsing.

When Playwright is available, the extractor uses browser layout metrics for
accurate overflow detection. Otherwise it falls back to a heuristic parser that
still catches density and image risks.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


SECTION_RE = re.compile(r"<section\b([^>]*)>(.*?)</section>", re.S | re.I)
IMG_RE = re.compile(r"<img\b([^>]*)>", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
BLOCK_BREAK_RE = re.compile(
    r"</(?:p|div|li|ul|ol|table|thead|tbody|tr|th|td|h[1-6]|header|footer|blockquote|pre|figure|section)>",
    re.I,
)
BR_RE = re.compile(r"<br\s*/?>", re.I)
ATTR_RE = re.compile(r"""([^\s=/>]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?""")


def parse_attrs(raw: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in ATTR_RE.finditer(raw):
        key = match.group(1).lower()
        value = next((group for group in match.groups()[1:] if group is not None), "")
        attrs[key] = value
    return attrs


def text_from_html(fragment: str) -> str:
    fragment = SCRIPT_STYLE_RE.sub("", fragment)
    fragment = BR_RE.sub("\n", fragment)
    fragment = BLOCK_BREAK_RE.sub("\n", fragment)
    fragment = TAG_RE.sub("", fragment)
    fragment = html.unescape(fragment)

    lines: list[str] = []
    for line in fragment.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


def parse_slide_size(attrs: dict[str, str]) -> tuple[int, int]:
    style = attrs.get("style", "")
    width_match = re.search(r"width\s*:\s*(\d+)px", style)
    height_match = re.search(r"height\s*:\s*(\d+)px", style)
    width = int(width_match.group(1)) if width_match else 1280
    height = int(height_match.group(1)) if height_match else 720
    return width, height


def is_remote_src(src: str) -> bool:
    return src.startswith(("http://", "https://", "data:"))


def local_image_exists(html_path: Path, src: str) -> bool:
    candidate = Path(src)
    if candidate.is_absolute():
        return candidate.exists()
    return (html_path.parent / src).exists()


def extract_slide_metrics_browser(html_path: Path) -> list[dict[str, Any]]:
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
            # Skip if the slide itself clips overflow (Marp themes typically do this)
            slide_overflow = slide.evaluate(
                "el => window.getComputedStyle(el).overflow"
            )
            slide_clips = slide_overflow in ("hidden", "clip", "scroll", "auto")
            if elements and not slide_clips:
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
                    "analysis_mode": "browser",
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


def extract_slide_metrics_heuristic(html_path: Path) -> list[dict[str, Any]]:
    """Extract per-slide metrics without Playwright using text heuristics."""
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    results: list[dict[str, Any]] = []

    for idx, match in enumerate(SECTION_RE.finditer(html_text), start=1):
        attrs = parse_attrs(match.group(1))
        inner_html = match.group(2)
        slide_w, slide_h = parse_slide_size(attrs)

        text_content = text_from_html(inner_html)
        char_count = len(text_content)
        line_count = text_content.count("\n") + 1 if text_content.strip() else 0

        flags: list[str] = []
        elements: list[dict[str, Any]] = []
        image_count = 0

        for img_match in IMG_RE.finditer(inner_html):
            image_count += 1
            img_attrs = parse_attrs(img_match.group(1))
            src = img_attrs.get("src", "")
            if not src:
                flags.append("IMAGE_NO_SRC: <img> without src")
            elif not is_remote_src(src) and not local_image_exists(html_path, src):
                flags.append(f"IMAGE_BROKEN: {src[:40]}")

        if char_count > 600:
            flags.append(f"DENSE_TEXT: {char_count} chars may overflow")
        if line_count > 20:
            flags.append(f"MANY_LINES: {line_count} lines may overflow")
        if char_count > 900 or line_count > 24:
            flags.append("CONTENT_OVERFLOW: heuristic density suggests overflow risk")

        results.append(
            {
                "slide": idx,
                "analysis_mode": "heuristic",
                "slide_size": {"width": slide_w, "height": slide_h},
                "metrics": {
                    "char_count": char_count,
                    "line_count": line_count,
                    "element_count": len(elements),
                    "image_count": image_count,
                },
                "elements": elements,
                "risk_flags": flags,
            }
        )

    return results


def extract_slide_metrics(html_path: Path) -> list[dict[str, Any]]:
    """Extract per-slide metrics, using browser metrics when available."""
    if sync_playwright is None:
        return extract_slide_metrics_heuristic(html_path)

    return extract_slide_metrics_browser(html_path)


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
