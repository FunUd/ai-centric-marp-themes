#!/usr/bin/env python3
"""check-templates.py — Validate every on-disk diagram template.

Replaces the previous CI shell loop, which echoed Mermaid filenames without
validating them and only checked draw.io at one layout. This gate is the real
thing:

1. Every template on disk must be declared in ``ALLOWED_LAYOUTS`` below, so a
   newly added template cannot slip past validation unnoticed.
2. Each template is rendered through the real ``render-slide-diagram.py`` CLI at
   every layout it claims to support; a non-zero exit (which includes the
   built-in layout validation) fails the check.

``ALLOWED_LAYOUTS`` is derived from ``VALIDATOR_LIMITS`` in ``layout_spec.py``:
it records which layouts each template actually fits, not which ones it could
theoretically be squeezed into. A template that fails a listed layout is a
regression, not a documentation nit — fix the template or move the layout out
of the list deliberately.

Usage:
    python scripts/diagrams/check-templates.py
    python scripts/diagrams/check-templates.py --skip-mermaid   # offline / no npx
    python scripts/diagrams/check-templates.py --engine json
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
RENDERER = SCRIPT_DIR / "render-slide-diagram.py"

from compat import ensure_utf8_stdio

# Canonical layout keys (scripts/diagrams/layout_spec.py::LAYOUTS).
FULL, COL2, ASYM, COL3 = "full", "col2", "asym", "col3"

# template path (relative to templates/) -> layouts it must render + validate at
# SSoT: this map is the authority for supported layouts. docs/diagrams.md's
# Supported Template Layouts table and template-catalog.md Verified Layouts
# are mirrors — update them together (checked by check-templates.py +
# check-catalog-sync.py, but layout lists are only enforced here).
ALLOWED_LAYOUTS: dict[str, tuple[str, ...]] = {
    # Mermaid (rendered through @mermaid-js/mermaid-cli; needs npx)
    "mermaid/flowchart-linear.mmd": (FULL,),
    "mermaid/flowchart-col2.mmd": (FULL, COL2, ASYM),
    "mermaid/sequence-api.mmd": (FULL,),
    "mermaid/sequence-api-asym.mmd": (FULL, ASYM),
    "mermaid/architecture-3tier.mmd": (FULL,),
    "mermaid/architecture-3tier-col2.mmd": (FULL, COL2, ASYM, COL3),
    "mermaid/state-machine.mmd": (FULL,),
    "mermaid/state-machine-col2.mmd": (FULL, COL2, ASYM, COL3),
    "mermaid/gantt-milestone.mmd": (FULL,),
    "mermaid/er-simple.mmd": (FULL,),
    "mermaid/c4-context-compact.mmd": (FULL, ASYM),
    "mermaid/mindmap-compact.mmd": (FULL, ASYM),
    # draw.io (pure stdlib mxGraph -> SVG)
    "drawio/system-architecture.drawio": (FULL,),
    "drawio/cloud-infrastructure.drawio": (FULL,),
    # JSON SVG (pure stdlib)
    "charts/revenue-pie.json": (FULL, COL2, ASYM, COL3),
    "charts/revenue-donut.json": (FULL, COL2, ASYM, COL3),
    "charts/sales-bar.json": (FULL, COL2, ASYM, COL3),
    "charts/quarterly-line.json": (FULL, COL2, ASYM, COL3),
    "charts/channel-stacked-bar.json": (FULL, COL2, ASYM, COL3),
    "charts/task-hbar.json": (FULL, COL2, ASYM, COL3),
    "charts/channel-100-bar.json": (FULL, COL2, ASYM, COL3),
    "concepts/team-pyramid.json": (FULL, COL2, ASYM, COL3),
    "concepts/improvement-cycle.json": (FULL, COL2, ASYM, COL3),
    "concepts/team-radial.json": (FULL,),
    "concepts/team-radial-compact.json": (FULL, COL2, ASYM, COL3),
    "concepts/sales-funnel.json": (FULL, COL2, ASYM, COL3),
    "concepts/tech-selection-matrix.json": (FULL, COL2, ASYM, COL3),
    "organization/team-org-chart.json": (FULL, COL2, ASYM, COL3),
}

# Recommended (max) full-slide embed width per Mermaid/draw.io template.
# Mermaid/draw.io SVGs keep their native viewBox ratio, so embedding a
# narrow-native SVG at the 1050px JSON default overflows vertically
# (e.g. mindmap 618x388 -> 660px tall at 1050px). The width here keeps the
# scaled height within the 460px slide canvas at `full`; narrower layouts
# only scale further down. Verified by _check_embed_height() below.
RECOMMENDED_EMBED_WIDTH: dict[str, int] = {
    "mermaid/flowchart-linear.mmd": 1050,
    "mermaid/flowchart-col2.mmd": 570,
    "mermaid/sequence-api.mmd": 950,
    "mermaid/sequence-api-asym.mmd": 770,
    "mermaid/architecture-3tier.mmd": 1050,
    "mermaid/architecture-3tier-col2.mmd": 210,
    "mermaid/state-machine.mmd": 1050,
    "mermaid/state-machine-col2.mmd": 460,
    "mermaid/gantt-milestone.mmd": 1050,
    "mermaid/er-simple.mmd": 1050,
    "mermaid/c4-context-compact.mmd": 900,
    "mermaid/mindmap-compact.mmd": 680,
    "drawio/system-architecture.drawio": 1050,
    "drawio/cloud-infrastructure.drawio": 1050,
}

# Slide canvas height budget for a diagram at `full` (layout_spec.CANVAS_MAX).
EMBED_HEIGHT_BUDGET = 460.0

GLOBS = ("mermaid/*.mmd", "drawio/*.drawio", "charts/*.json", "concepts/*.json", "organization/*.json")

# Engine per glob, used by --engine / --skip-mermaid.
def _engine_of(rel: str) -> str:
    return rel.split("/", 1)[0]


def templates_on_disk() -> set[str]:
    found: set[str] = set()
    for pattern in GLOBS:
        for path in TEMPLATES_DIR.glob(pattern):
            found.add(path.relative_to(TEMPLATES_DIR).as_posix())
    return found


def undeclared(on_disk: set[str]) -> list[str]:
    return sorted(on_disk - set(ALLOWED_LAYOUTS))


def stale_entries(on_disk: set[str]) -> list[str]:
    return sorted(set(ALLOWED_LAYOUTS) - on_disk)


def render_and_validate(source: Path, layout: str, out_dir: Path) -> tuple[bool, str]:
    """Render one template at one layout via the real CLI.

    Returns (ok, output). The CLI already runs validate-slide-diagram.py and
    exits non-zero on failure, so a zero return code means the template both
    rendered and passed layout validation.
    """
    out_path = out_dir / f"{source.stem}-{layout}.svg"
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(RENDERER),
                "-i",
                str(source),
                "-o",
                str(out_path),
                "--theme",
                "azure-clarity",
                "--layout",
                layout,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return False, "[ERROR] renderer timed out after 300s"
    except OSError as error:
        return False, f"[ERROR] failed to launch renderer: {error}"
    return result.returncode == 0, (result.stdout + result.stderr)


def _relevant_lines(output: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if "[ERROR]" in line or "[WARN]" in line
    ][:6]


def _viewbox_size(svg_path: Path) -> tuple[float, float] | None:
    """Native viewBox (w, h) of a rendered SVG, or None if unreadable."""
    try:
        text = svg_path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r'viewBox="([^"]+)"', text)
    if not match:
        return None
    parts = [p for p in re.split(r"[,\s]+", match.group(1).strip()) if p]
    try:
        numbers = [float(p) for p in parts]
    except ValueError:
        return None
    if len(numbers) != 4 or numbers[2] <= 0 or numbers[3] <= 0:
        return None
    return numbers[2], numbers[3]


def check_embed_height(rel: str, svg_path: Path) -> str | None:
    """Fail message when `rel` exceeds the canvas at its recommended embed width.

    Returns None when the template fits (or has no map entry / unreadable
    viewBox — those are covered by the manifest tests, not this gate).
    """
    if _engine_of(rel) not in ("mermaid", "drawio"):
        return None
    width = RECOMMENDED_EMBED_WIDTH.get(rel)
    if width is None:
        return f"[EMBED-MAP] {rel} has no RECOMMENDED_EMBED_WIDTH entry"
    size = _viewbox_size(svg_path)
    if size is None:
        return f"[EMBED-VIEWBOX] {rel}: cannot parse viewBox from rendered SVG"
    vb_w, vb_h = size
    scaled_h = vb_h / vb_w * width
    if scaled_h > EMBED_HEIGHT_BUDGET:
        return (
            f"[EMBED-HEIGHT] {rel}: {scaled_h:.0f}px tall at width:{width}px "
            f"(budget {EMBED_HEIGHT_BUDGET:.0f}px). Lower RECOMMENDED_EMBED_WIDTH "
            f"or shrink the template."
        )
    return None


def main() -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Validate all diagram templates at their supported layouts.")
    parser.add_argument(
        "--skip-mermaid",
        action="store_true",
        help="Skip Mermaid templates (they need npx + @mermaid-js/mermaid-cli).",
    )
    parser.add_argument(
        "--engine",
        choices=["mermaid", "drawio", "charts", "concepts", "organization"],
        help="Only validate templates of this engine.",
    )
    args = parser.parse_args()

    on_disk = templates_on_disk()

    # 1. Manifest completeness — the gate must never have blind spots.
    problems: list[str] = []
    try:
        from layout_spec import LAYOUTS as _LAYOUTS
    except (ImportError, OSError):
        _LAYOUTS = ("full", "col2", "asym", "col3")
    for name, layouts in ALLOWED_LAYOUTS.items():
        for layout in layouts:
            if layout not in _LAYOUTS:
                problems.append(
                    f"[LAYOUT] ALLOWED_LAYOUTS[{name!r}] has unknown layout {layout!r} "
                    f"(expected one of {list(_LAYOUTS)})."
                )
    for name in undeclared(on_disk):
        problems.append(
            f"[UNDECLARED] templates/{name} is not in check-templates.py::ALLOWED_LAYOUTS — "
            f"it would never be validated. Add it with the layouts it fits."
        )
    for name in stale_entries(on_disk):
        problems.append(
            f"[STALE] ALLOWED_LAYOUTS lists templates/{name} but the file does not exist."
        )
    for name in sorted(on_disk):
        if _engine_of(name) in ("mermaid", "drawio") and name not in RECOMMENDED_EMBED_WIDTH:
            problems.append(
                f"[EMBED-MAP] templates/{name} has no RECOMMENDED_EMBED_WIDTH entry — "
                f"its slide embed height would never be checked. Add a fitting width."
            )
    for name, width in RECOMMENDED_EMBED_WIDTH.items():
        if name not in on_disk:
            problems.append(f"[EMBED-MAP] RECOMMENDED_EMBED_WIDTH lists {name!r} but the file does not exist.")
        elif not 0 < width <= 1120:
            problems.append(f"[EMBED-MAP] RECOMMENDED_EMBED_WIDTH[{name!r}] = {width}: expected 0 < width <= 1120.")
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print(f"FAILED: {len(problems)} manifest problem(s)", file=sys.stderr)
        return 1

    targets = sorted(on_disk)
    if args.engine:
        targets = [t for t in targets if _engine_of(t) == args.engine]
    if args.skip_mermaid:
        targets = [t for t in targets if _engine_of(t) != "mermaid"]

    if not targets:
        print("[SKIP] no templates selected.")
        return 0

    failures: list[str] = []
    checked = 0
    skipped_note = " (mermaid skipped: --skip-mermaid)" if args.skip_mermaid else ""

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        for rel in targets:
            source = TEMPLATES_DIR / rel
            for layout in ALLOWED_LAYOUTS[rel]:
                ok, output = render_and_validate(source, layout, out_dir)
                checked += 1
                if ok:
                    print(f"[OK] {rel} @ {layout}")
                    if layout == FULL and _engine_of(rel) in ("mermaid", "drawio"):
                        out_path = out_dir / f"{source.stem}-{layout}.svg"
                        problem = check_embed_height(rel, out_path)
                        if problem:
                            print(f"[FAIL] {problem}")
                            failures.append(f"{rel} @ embed-width")
                else:
                    print(f"[FAIL] {rel} @ {layout}")
                    for line in _relevant_lines(output):
                        print(f"       {line}")
                    failures.append(f"{rel} @ {layout}")

    if failures:
        print(
            f"FAILED: {len(failures)} template/layout combination(s) did not render or validate: "
            f"{', '.join(failures)}\n"
            f"       Either shrink the template so it fits, or move that layout out of "
            f"check-templates.py::ALLOWED_LAYOUTS and document the restriction.",
            file=sys.stderr,
        )
        return 1

    unit = "template/layout" if checked != len(targets) else "template"
    print(f"[OK] {len(targets)} templates, {checked} {unit} combinations validated{skipped_note}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
