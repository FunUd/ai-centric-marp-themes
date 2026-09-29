"""README inventory counts must match the diagram engine on disk.

Regression: the README tree said "17 templates" and the vendor paragraph
"34 files" long after the registry grew to 28 templates / 46 vendored
files. Counts in prose rot silently, so this gate derives both numbers
from disk and requires the documented values to agree.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "README.md"
ENGINE_TEMPLATES = ROOT / "scripts/diagrams/templates"
VENDOR_DIR = ROOT / "skills/marp-diagram-creator/vendor"


def templates_on_disk() -> int:
    return sum(1 for p in ENGINE_TEMPLATES.rglob("*") if p.is_file())


def vendored_files() -> int:
    return sum(1 for p in VENDOR_DIR.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def test_readme_template_count_matches_disk() -> None:
    text = README.read_text(encoding="utf-8")
    match = re.search(r"templates/\s+# (\d+) templates", text)
    assert match, "README tree no longer states a template count"
    assert int(match.group(1)) == templates_on_disk(), (
        f"README says {match.group(1)} templates, disk has {templates_on_disk()}"
    )


def test_readme_vendor_file_count_matches_disk() -> None:
    text = README.read_text(encoding="utf-8")
    match = re.search(r"(\d+) templates, 6 theme palettes — (\d+) files", text)
    assert match, "README vendor paragraph no longer states inventory counts"
    assert int(match.group(1)) == templates_on_disk(), (
        f"README says {match.group(1)} templates, disk has {templates_on_disk()}"
    )
    assert int(match.group(2)) == vendored_files(), (
        f"README says {match.group(2)} vendored files, disk has {vendored_files()}"
    )
