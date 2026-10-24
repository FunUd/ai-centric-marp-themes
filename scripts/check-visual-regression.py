#!/usr/bin/env python3
"""Compare rendered sample-slide screenshots with the checked-in previews."""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops


@dataclass(frozen=True)
class Comparison:
    filename: str
    changed_percent: float | None
    status: str
    note: str = ""


def _png_files(directory: Path) -> dict[str, Path]:
    if not directory.is_dir():
        raise ValueError(f"Screenshot directory does not exist: {directory}")
    return {path.name: path for path in directory.glob("*.png") if path.is_file()}


def _compare_images(baseline_path: Path, actual_path: Path, pixel_threshold: int) -> tuple[float, Image.Image]:
    with Image.open(baseline_path) as baseline_image, Image.open(actual_path) as actual_image:
        baseline = baseline_image.convert("RGB")
        actual = actual_image.convert("RGB")

    if baseline.size != actual.size:
        raise ValueError(f"image dimensions differ: baseline={baseline.size}, actual={actual.size}")

    channel_diffs = ImageChops.difference(baseline, actual).split()
    max_channel_diff = ImageChops.lighter(ImageChops.lighter(channel_diffs[0], channel_diffs[1]), channel_diffs[2])
    changed_mask = max_channel_diff.point(lambda value: 255 if value > pixel_threshold else 0)
    changed_pixels = changed_mask.histogram()[255]
    total_pixels = baseline.width * baseline.height
    changed_percent = changed_pixels * 100 / total_pixels

    if changed_pixels:
        blended = Image.blend(baseline, actual, 0.5)
        red = Image.new("RGB", baseline.size, (255, 0, 0))
        diff_image = Image.composite(red, blended, changed_mask)
    else:
        diff_image = baseline

    return changed_percent, diff_image


def compare_directories(
    baseline_dir: Path,
    actual_dir: Path,
    diff_dir: Path,
    threshold_percent: float,
    pixel_threshold: int,
) -> list[Comparison]:
    baselines = _png_files(baseline_dir)
    actuals = _png_files(actual_dir)
    if not baselines:
        raise ValueError(f"No PNG baselines found in {baseline_dir}")
    if not actuals:
        raise ValueError(f"No rendered PNG screenshots found in {actual_dir}")

    diff_dir.mkdir(parents=True, exist_ok=True)
    results: list[Comparison] = []
    for filename in sorted(baselines.keys() | actuals.keys()):
        if filename not in baselines:
            results.append(Comparison(filename, None, "error", "no baseline image"))
            continue
        if filename not in actuals:
            results.append(Comparison(filename, None, "error", "rendered image is missing"))
            continue

        try:
            changed_percent, diff_image = _compare_images(baselines[filename], actuals[filename], pixel_threshold)
        except (OSError, ValueError) as error:
            results.append(Comparison(filename, None, "error", str(error)))
            continue

        if changed_percent > threshold_percent:
            diff_image.save(diff_dir / filename)
            results.append(Comparison(filename, changed_percent, "changed"))
        else:
            results.append(Comparison(filename, changed_percent, "match"))

    return results


def write_report(
    report_path: Path,
    results: list[Comparison],
    threshold_percent: float,
    pixel_threshold: int,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Visual regression report",
        "",
        f"Allowed changed pixels per image: **{threshold_percent:.3f}%** "
        f"(per-channel tolerance: **{pixel_threshold}**).",
        "",
        "| Screenshot | Changed pixels | Result | Details |",
        "|---|---:|---|---|",
    ]
    for result in results:
        percent = f"{result.changed_percent:.3f}%" if result.changed_percent is not None else "n/a"
        lines.append(f"| `{result.filename}` | {percent} | {result.status} | {result.note} |")

    counts = {status: sum(result.status == status for result in results) for status in ("match", "changed", "error")}
    lines.extend(
        [
            "",
            f"**Summary:** {counts['match']} matched, {counts['changed']} changed, {counts['error']} errors.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-dir", type=Path, required=True, help="Directory containing checked-in baseline PNGs"
    )
    parser.add_argument("--actual-dir", type=Path, required=True, help="Directory containing freshly rendered PNGs")
    parser.add_argument("--diff-dir", type=Path, required=True, help="Directory for generated difference images")
    parser.add_argument("--report", type=Path, required=True, help="Markdown report output path")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Maximum changed-pixel percentage per image (default: 0.5)",
    )
    parser.add_argument(
        "--pixel-threshold",
        type=int,
        default=24,
        help="Ignore per-channel color differences up to this value (default: 24)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Report visual changes without failing; missing or invalid images still fail",
    )
    args = parser.parse_args()
    if not math.isfinite(args.threshold) or not 0 <= args.threshold <= 100:
        parser.error("--threshold must be between 0 and 100")
    if not 0 <= args.pixel_threshold <= 255:
        parser.error("--pixel-threshold must be between 0 and 255")
    return args


def main() -> int:
    args = parse_args()
    try:
        results = compare_directories(
            args.baseline_dir,
            args.actual_dir,
            args.diff_dir,
            args.threshold,
            args.pixel_threshold,
        )
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    write_report(args.report, results, args.threshold, args.pixel_threshold)
    for result in results:
        percent = f"{result.changed_percent:.3f}%" if result.changed_percent is not None else "n/a"
        print(f"{result.status.upper()}: {result.filename}: {percent} changed pixels {result.note}".rstrip())

    errors = any(result.status == "error" for result in results)
    changes = any(result.status == "changed" for result in results)
    if errors:
        return 1
    if changes and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
