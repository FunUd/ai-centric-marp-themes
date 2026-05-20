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
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
EXTRACTOR_SCRIPT = SCRIPT_DIR / "marp-dom-extractor.py"


def resolve_executable(name: str) -> str | None:
    """Resolve a runnable executable path for the current platform."""
    candidates = [name]
    if os.name == "nt" and not Path(name).suffix:
        candidates.extend([f"{name}.cmd", f"{name}.exe", f"{name}.bat"])

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    path = Path(name)
    if path.exists():
        return str(path)

    return None


def resolve_default_outputs(markdown_path: Path) -> tuple[Path, Path]:
    assets_dir = markdown_path.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return markdown_path.parent / "preview.html", assets_dir / "dom-metrics.json"


def run_command(command: list[str], env: dict[str, str] | None = None) -> None:
    subprocess.run(command, check=True, env=env)


def npm_cache_env() -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        cache_dir = Path(r"C:\tmp\npm-cache")
    else:
        cache_dir = Path(tempfile.gettempdir()) / "npm-cache"

    cache_dir.mkdir(parents=True, exist_ok=True)
    env["npm_config_cache"] = str(cache_dir)
    return env


def export_html(markdown_path: Path, html_path: Path, marp_bin: str, theme: str | None = None) -> list[str]:
    primary_bin = resolve_executable(marp_bin) or marp_bin
    primary = [primary_bin, "--no-stdin", "--allow-local-files", str(markdown_path), "-o", str(html_path)]
    if theme:
        primary.extend(["--theme", theme])

    try:
        primary_env = npm_cache_env() if Path(primary_bin).name.lower().startswith("npx") else None
        run_command(primary, env=primary_env)
        return primary
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback to npx if primary failed
        fallback_bin = resolve_executable("npx") or "npx"
        fallback = [fallback_bin, "-y", "@marp-team/marp-cli", "--no-stdin", "--allow-local-files", str(markdown_path), "-o", str(html_path)]
        if theme:
            fallback.extend(["--theme", theme])
        run_command(fallback, env=npm_cache_env())
        return fallback


def extract_metrics(html_path: Path, json_path: Path, screenshot_dir: Path | None = None) -> None:
    extractor = [sys.executable, str(EXTRACTOR_SCRIPT), str(html_path), "-o", str(json_path)]
    if screenshot_dir:
        extractor.extend(["--screenshot-dir", str(screenshot_dir)])
    run_command(extractor)


def load_metrics(json_path: Path) -> list[dict[str, Any]]:
    return json.loads(json_path.read_text(encoding="utf-8"))


def print_summary(metrics: list[dict[str, Any]], html_path: Path, json_path: Path) -> int:
    print(f"HTML written: {html_path}")
    print(f"Metrics written: {json_path}")

    if metrics:
        analysis_mode = str(metrics[0].get("analysis_mode") or "browser")
        if analysis_mode == "heuristic":
            print("Analysis mode: heuristic (Playwright unavailable).")
            print("- Overflow checks are approximate (based on character density).")
            print("- Image checks only verify local file existence.")

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
        help="Path to the rendered HTML file (default: <deck>/preview.html)",
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
        "--theme",
        help="Path to a custom Marp theme CSS file",
    )
    parser.add_argument(
        "--screenshot-dir",
        help="Directory to save slide screenshots during DOM extraction",
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
        command_used = export_html(
            markdown_path.resolve(),
            html_path.resolve(),
            args.marp_bin,
            theme=args.theme,
        )
        print(f"Marp command: {' '.join(command_used)}")
        
        screenshot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None
        extract_metrics(html_path.resolve(), json_path.resolve(), screenshot_dir)
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
