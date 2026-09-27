"""Tests for the shared theme base (`themes/_base.css` + `sync-theme-base.py`).

Layout containers, grids, callouts, badges, alignment and display controls
are structurally identical across themes modulo the `--xx-` token prefix.
`themes/_base.css` (azure dialect) is the single source of truth; each listed
theme carries its prefix-substituted copy between `<base:name>` markers, and
`sync-theme-base.py --check` is the CI gate. These tests pin the contract:

- every base section is hygiene-clean (multi-theme, ac-only, comment-free);
- every listed theme carries exactly the markers it should — no stale, none
  missing — with content equal to the substituted base (i.e. `--check` passes);
- nebula-glass / slate-minimal intentionally stay fully local.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROOT_DIR = SCRIPT_DIR.parent.parent
THEMES_DIR = ROOT_DIR / "themes"
SYNC_SCRIPT = SCRIPT_DIR.parent / "sync-theme-base.py"


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_theme_base", SYNC_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_theme_base"] = module
    spec.loader.exec_module(module)
    return module


sync = load_sync()


def test_base_file_parses_into_sections() -> None:
    sections = sync.parse_base()
    assert len(sections) == 21
    assert set(sections) == {
        "pagination", "display-control",
        "cols-2", "cols-3", "col-card", "col-h3", "split-2", "split-3",
        "grid-quadrant", "grid-cells-core", "grid-cells-side",
        "grid-axes", "grid-sharp",
        "callout-base", "callout-blue", "callout-alerts", "badge-base",
        "align-h", "align-v",
        "reduced-motion", "focus-visible",
    }


def test_base_hygiene_passes() -> None:
    assert sync.check_base_hygiene(sync.parse_base()) == []


def test_sync_check_passes() -> None:
    """Every marker region equals its substituted base section."""
    problems: list[str] = []
    sections = sync.parse_base()
    for theme in sorted(sync.PREFIX):
        problems.extend(sync.sync_theme(theme, sections, check=True))
    assert problems == []


def test_divergent_themes_stay_local() -> None:
    """nebula-glass / slate-minimal diverge structurally (glassmorphism,
    `!important` utilities) and carry no layout sections — only the
    accessibility `focus-visible` ring, whose body is prefix-mechanical."""
    for theme in ("nebula-glass", "slate-minimal"):
        text = (THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8")
        markers = set(re.findall(r"<base:([\w-]+)>", text))
        assert markers == {"focus-visible"}, f"{theme}: {sorted(markers)}"


def test_marker_regions_preserve_rule_order() -> None:
    """Markers wrap content in place: stripping marker comments must yield
    CSS whose rule sequence is unchanged (cascade-equivalence by construction
    holds only if nothing moved)."""
    for theme in sorted(sync.PREFIX):
        text = (THEMES_DIR / f"{theme}.css").read_text(encoding="utf-8")
        stripped = re.sub(r"/\* </?base:[\w-]+>.*?\*/\n?", "", text)
        # Every shared body still occurs exactly once, in base order.
        positions = []
        for name in sync.parse_base():
            themes, body = sync.parse_base()[name]
            if theme not in themes:
                continue
            want = body.replace("--ac-", f"--{sync.PREFIX[theme]}-")
            positions.append(stripped.find(want))
            assert positions[-1] != -1, f"{theme}/{name} body missing"
        assert positions == sorted(positions), f"{theme}: shared bodies out of order"


def test_base_covers_the_documented_section_count() -> None:
    sections = sync.parse_base()
    total_regions = sum(len(themes) for themes, _body in sections.values())
    assert total_regions == 80
