from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

pytest.importorskip("PIL")
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[2] / "check-visual-regression.py"
SPEC = importlib.util.spec_from_file_location("check_visual_regression", SCRIPT)
assert SPEC and SPEC.loader
visual_regression = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = visual_regression
SPEC.loader.exec_module(visual_regression)


def _write_image(path: Path, color: tuple[int, int, int], size: tuple[int, int] = (10, 10)) -> None:
    Image.new("RGB", size, color).save(path)


def test_identical_images_match_without_diff_output(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    diff = tmp_path / "diff"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "slide.png", (255, 255, 255))
    _write_image(actual / "slide.png", (255, 255, 255))

    results = visual_regression.compare_directories(baseline, actual, diff, 0.5, 24)

    assert [(result.status, result.changed_percent) for result in results] == [("match", 0)]
    assert not list(diff.glob("*.png"))


def test_small_pixel_difference_is_within_tolerance(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    diff = tmp_path / "diff"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "slide.png", (255, 255, 255))
    _write_image(actual / "slide.png", (255, 255, 255))
    with Image.open(actual / "slide.png") as image:
        image.putpixel((0, 0), (240, 255, 255))
        image.save(actual / "slide.png")

    results = visual_regression.compare_directories(baseline, actual, diff, 0.5, 24)

    assert results[0].status == "match"
    assert results[0].changed_percent == 0


def test_significant_difference_creates_diff_image(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    diff = tmp_path / "diff"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "slide.png", (255, 255, 255))
    _write_image(actual / "slide.png", (0, 0, 0))

    results = visual_regression.compare_directories(baseline, actual, diff, 0.5, 24)

    assert results[0].status == "changed"
    assert results[0].changed_percent == 100
    assert (diff / "slide.png").is_file()


def test_missing_and_extra_images_are_reported_as_errors(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "missing.png", (0, 0, 0))
    _write_image(actual / "extra.png", (0, 0, 0))

    results = visual_regression.compare_directories(baseline, actual, tmp_path / "diff", 0.5, 24)

    assert [(result.filename, result.status) for result in results] == [
        ("extra.png", "error"),
        ("missing.png", "error"),
    ]


def test_dimension_mismatch_is_reported_as_error(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "slide.png", (0, 0, 0), (10, 10))
    _write_image(actual / "slide.png", (0, 0, 0), (11, 10))

    results = visual_regression.compare_directories(baseline, actual, tmp_path / "diff", 0.5, 24)

    assert results[0].status == "error"
    assert "dimensions differ" in results[0].note


def test_warn_only_changes_exit_status_but_not_missing_image_errors(tmp_path: Path, monkeypatch) -> None:
    baseline = tmp_path / "baseline"
    actual = tmp_path / "actual"
    baseline.mkdir()
    actual.mkdir()
    _write_image(baseline / "slide.png", (255, 255, 255))
    _write_image(actual / "slide.png", (0, 0, 0))
    args = [
        "--baseline-dir",
        str(baseline),
        "--actual-dir",
        str(actual),
        "--diff-dir",
        str(tmp_path / "diff"),
        "--report",
        str(tmp_path / "report.md"),
    ]

    monkeypatch.setattr(sys, "argv", ["check-visual-regression.py", *args])
    assert visual_regression.main() == 1

    monkeypatch.setattr(sys, "argv", ["check-visual-regression.py", *args, "--warn-only"])
    assert visual_regression.main() == 0

    (actual / "slide.png").unlink()
    monkeypatch.setattr(sys, "argv", ["check-visual-regression.py", *args, "--warn-only"])
    assert visual_regression.main() == 1
