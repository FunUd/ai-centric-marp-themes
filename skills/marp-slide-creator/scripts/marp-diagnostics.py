#!/usr/bin/env python3
"""Marp diagnostics helper.

Export a Marp Markdown deck to HTML with the Marp CLI, then run the DOM
extractor to surface overflow, broken-image, and density risks.

This is a command-line companion to Marp for VS Code's experimental
slide-content-overflow diagnostic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
EXTRACTOR_SCRIPT = SCRIPT_DIR / "marp-dom-extractor.py"
DEFAULT_MARP_FALLBACK = ["npx", "-y", "@marp-team/marp-cli"]


def resolve_default_outputs(markdown_path: Path) -> tuple[Path, Path]:
    assets_dir = markdown_path.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir / "preview.html", assets_dir / "dom-metrics.json"


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def export_html(markdown_path: Path, html_path: Path, marp_bin: str) -> list[str]:
    primary = [marp_bin, "--no-stdin", str(markdown_path), "-o", str(html_path)]
    try:
        run_command(primary)
        return primary
    except FileNotFoundError:
        fallback = [*DEFAULT_MARP_FALLBACK, "--no-stdin", str(markdown_path), "-o", str(html_path)]
        run_command(fallback)
        return fallback


def extract_metrics(html_path: Path, json_path: Path) -> None:
    extractor = [sys.executable, str(EXTRACTOR_SCRIPT), str(html_path), "-o", str(json_path)]
    run_command(extractor)


def load_metrics(json_path: Path) -> list[dict[str, Any]]:
    return json.loads(json_path.read_text(encoding="utf-8"))


def print_summary(metrics: list[dict[str, Any]], html_path: Path, json_path: Path) -> int:
    print(f"HTML written: {html_path}")
    print(f"Metrics written: {json_path}")

    risk_entries: list[tuple[int, list[str]]] = []
    for slide in metrics:
        flags = slide.get("risk_flags") or []
        if flags:
            risk_entries.append((int(slide.get("slide", 0)), list(flags)))

    if not risk_entries:
        print("No overflow, density, or image risks detected.")
        return 0

    print("Risk summary:")
    for slide_number, flags in risk_entries:
        print(f"- Slide {slide_number}: {', '.join(flags)}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a Marp deck to HTML and run DOM-based diagnostics."
    )
    parser.add_argument("markdown_file", help="Path to the Marp Markdown deck")
    parser.add_argument(
        "--html-out",
        help="Path to the rendered HTML file (default: <deck>/assets/preview.html)",
    )
    parser.add_argument(
        "--json-out",
        help="Path to the DOM metrics JSON file (default: <deck>/assets/dom-metrics.json)",
    )
    parser.add_argument(
        "--marp-bin",
        default="marp",
        help="Marp CLI executable to try first (fallback: npx @marp-team/marp-cli)",
    )
    parser.add_argument(
        "--fail-on-risk",
        action="store_true",
        help="Exit with a non-zero status when any slide has risk flags",
    )
    args = parser.parse_args()

    markdown_path = Path(args.markdown_file)
    if not markdown_path.exists():
        print(f"Error: file not found: {markdown_path}", file=sys.stderr)
        return 1

    if args.html_out:
        html_path = Path(args.html_out)
        html_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        html_path, default_json_path = resolve_default_outputs(markdown_path)

    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not args.html_out:
            json_path = default_json_path
        else:
            json_path = html_path.parent / "dom-metrics.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        command_used = export_html(markdown_path.resolve(), html_path.resolve(), args.marp_bin)
        print(f"Marp command: {' '.join(command_used)}")
        extract_metrics(html_path.resolve(), json_path.resolve())
        metrics = load_metrics(json_path.resolve())
        status = print_summary(metrics, html_path.resolve(), json_path.resolve())
    except subprocess.CalledProcessError as exc:
        print(f"Error: command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.fail_on_risk and status != 0:
        return status

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
