#!/usr/bin/env python3
"""Regenerate the diagram golden fixtures (6 themes x 3 engines).

Outputs scripts/diagrams/tests/fixtures/diagram-golden/<theme>-<kind>.svg
where kind is flowchart (Mermaid), architecture (draw.io), pie (JSON).
"""
from __future__ import annotations

import subprocess
import sys
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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    for theme in THEMES:
        for kind, src in SOURCES.items():
            dest = OUT / f"{theme}-{kind}.svg"
            cmd = [
                sys.executable, str(SCRIPTS / "render-slide-diagram.py"),
                "-i", str(src), "-o", str(dest), "--theme", theme, "--layout", "full",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            status = "OK" if res.returncode == 0 else "FAIL"
            if res.returncode != 0:
                failures += 1
                print(f"[{status}] {theme}/{kind}\n{res.stderr[-2000:]}")
            else:
                print(f"[{status}] {dest.relative_to(ROOT)} ({dest.stat().st_size}B)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
