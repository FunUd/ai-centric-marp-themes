#!/usr/bin/env python3
"""
run-all-sync.py
Single entry point to run or check all repository synchronization scripts:
1. themes/_base.css -> themes/*.css (sync-theme-base.py)
2. themes/*.css -> theme-styles/*.json (sync-tokens-from-css.py)
3. theme_classes.py -> theme-classes.json (sync-theme-classes.py)
4. scripts/diagrams/ -> skills/marp-diagram-creator/vendor/ (sync-skill-vendor.py)
5. skills/ -> agent skills (.github/skills, .agent/skills, etc.) (sync-skills.py)
6. Template catalog sync (check-catalog-sync.py)
7. Class documentation sync (check-class-docs.py)

Usage:
  python scripts/run-all-sync.py          # Propagate all SSoT changes
  python scripts/run-all-sync.py --check  # Verify everything is in sync (CI / pre-commit)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# SSoT Windows encoding guard
sys.path.insert(0, str(ROOT_DIR / "scripts/diagrams"))
try:
    from compat import ensure_utf8_stdio

    ensure_utf8_stdio()
except ImportError:
    pass


def run_step(cmd: list[str], desc: str) -> bool:
    print(f"==> {desc}...")
    res = subprocess.run([sys.executable, *cmd], cwd=ROOT_DIR)
    if res.returncode != 0:
        print(f"[FAIL] {desc} (exit {res.returncode})\n")
        return False
    print(f"[OK] {desc}\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or check all repository sync scripts.")
    parser.add_argument("--check", action="store_true", help="Only check synchronization without modifying files")
    args = parser.parse_args()

    check_flag = ["--check"] if args.check else []

    steps = [
        # SSoT propagation order:
        # 1. Base CSS -> Theme CSS files
        (["scripts/sync-theme-base.py"] + check_flag, "Theme Base CSS Sync"),
        # 2. Theme CSS -> Design tokens JSON
        (["scripts/diagrams/sync-tokens-from-css.py"] + check_flag, "Theme Tokens Sync"),
        # 3. Theme classes manifest
        (["scripts/diagrams/sync-theme-classes.py"] + check_flag, "Theme Classes Sync"),
        # 4. Diagram engine -> Skill vendor
        (["scripts/sync-skill-vendor.py"] + check_flag, "Diagram Runtime Vendoring"),
        # 5. Skills -> Agent directories
        (["scripts/sync-skills.py"] + check_flag, "Agent Skills Sync"),
    ]

    # Verification-only checks (run only with --check or always check afterwards)
    verify_steps = [
        (["scripts/diagrams/check-catalog-sync.py"], "Template Catalog Sync Check"),
        (["scripts/diagrams/check-class-docs.py"], "Class Documentation Sync Check"),
    ]

    failed = False
    for cmd, desc in steps:
        if not run_step(cmd, desc):
            failed = True
            if args.check:
                # In check mode, report failure immediately or continue to show all
                pass

    for cmd, desc in verify_steps:
        if not run_step(cmd, desc):
            failed = True

    if failed:
        print("[FAIL] One or more synchronization steps failed.")
        return 1

    action_word = "checked" if args.check else "synchronized"
    print(f"[OK] All repository components successfully {action_word}!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
