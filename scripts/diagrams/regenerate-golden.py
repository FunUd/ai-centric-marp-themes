#!/usr/bin/env python3
"""Regenerate the diagram golden fixtures (6 themes x 3 engines).

Outputs scripts/diagrams/tests/fixtures/diagram-golden/<theme>-<kind>.svg
where kind is flowchart (Mermaid), architecture (draw.io), pie (JSON).

Use --check in CI to fail on drift without overwriting fixtures.
"""
from __future__ import annotations

import argparse
import filecmp
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "diagrams"
OUT = SCRIPTS / "tests" / "fixtures" / "diagram-golden"

THEMES = [
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
]

SOURCES = {
    "flowchart": SCRIPTS / "templates" / "mermaid" / "flowchart-linear.mmd",
    "architecture": SCRIPTS / "templates" / "drawio" / "system-architecture.drawio",
    "pie": SCRIPTS / "templates" / "charts" / "revenue-pie.json",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate diagram golden fixtures.")
    parser.add_argument("--check", action="store_true", help="Fail on drift without overwriting fixtures.")
    # argv=None (direct call, e.g. tests) means "no flags", not sys.argv:
    # pytest's own argv must never leak into this parser.
    args = parser.parse_args([] if argv is None else argv)

    OUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    drift: list[str] = []
    for theme in THEMES:
        for kind, src in SOURCES.items():
            dest = OUT / f"{theme}-{kind}.svg"
            if args.check:
                with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                try:
                    ok = _render(theme, kind, src, tmp_path)
                    if not ok:
                        failures += 1
                    elif not dest.is_file() or not filecmp.cmp(tmp_path, dest, shallow=False):
                        drift.append(f"{theme}-{kind}")
                        print(f"[DRIFT] {dest.relative_to(ROOT)} differs; run regenerate-golden.py to update")
                finally:
                    tmp_path.unlink(missing_ok=True)
                continue
            ok = _render(theme, kind, src, dest)
            if not ok:
                failures += 1
    if args.check and drift:
        print(f"FAILED: {len(drift)} golden fixture(s) drifted: {', '.join(drift)}", file=sys.stderr)
        return 1
    return 1 if failures else 0


def _render(theme: str, kind: str, src: Path, dest: Path) -> bool:
    cmd = [
        sys.executable, str(SCRIPTS / "render-slide-diagram.py"),
        "-i", str(src), "-o", str(dest), "--theme", theme, "--layout", "full",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {theme}/{kind}\nrenderer timed out after 300s")
        return False
    except OSError as error:
        print(f"[FAIL] {theme}/{kind}\nfailed to launch renderer: {error}")
        return False
    status = "OK" if res.returncode == 0 else "FAIL"
    if res.returncode != 0:
        print(f"[{status}] {theme}/{kind}\n{res.stderr[-2000:]}")
        return False
    print(f"[{status}] {theme}/{kind} ({dest.stat().st_size}B)")
    return True


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
