#!/usr/bin/env python3
"""
sync-skills.py
Sync contents of `skills/` (source of truth) to various AI agent directories.
Removes existing directories in targets before copying.
"""

import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT_DIR / "skills"
TARGET_ROOTS = [
    ROOT_DIR / ".kiro/skills",
    ROOT_DIR / ".agent/skills",
    ROOT_DIR / ".agents/skills",
    ROOT_DIR / ".windsurf/skills",
    ROOT_DIR / ".codex/skills",
    ROOT_DIR / ".github/skills",
    ROOT_DIR / ".claude/skills",
]


def _is_within_root(path: Path, root: Path) -> bool:
    """Return True when path resolves inside root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def sync_skills():
    if not SOURCE_DIR.exists():
        print(f"[ERROR] Source directory '{SOURCE_DIR}' not found.")
        return

    skill_dirs = [d for d in SOURCE_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    if not skill_dirs:
        print("[INFO] No skill directories found in 'skills/'.")
        return

    print(f"Found {len(skill_dirs)} skill(s): {[d.name for d in skill_dirs]}\n")

    for target_root in TARGET_ROOTS:
        if not target_root.exists():
            print(f"[SKIP] '{target_root}' does not exist, skipping.")
            continue

        print(f"--- Syncing to '{target_root}' ---")
        # Remove stale skill directories in target before syncing
        source_skill_names = {d.name for d in skill_dirs}
        if target_root.exists():
            for target_item in target_root.iterdir():
                if target_item.is_dir() and target_item.name not in source_skill_names:
                    # Only remove directories with project-specific prefixes to avoid 
                    # deleting unrelated or system-provided skills.
                    if target_item.name.startswith(("theme-expert-", "slide-expert-", "marp-")):
                        shutil.rmtree(target_item)
                        print(f"  [DEL STALE] {target_item}")

        for skill_dir in skill_dirs:
            dest = target_root / skill_dir.name
            if not _is_within_root(dest, target_root):
                raise RuntimeError(f"Refusing to write outside target root: {dest}")

            if dest.exists():
                shutil.rmtree(dest)
                print(f"  [DEL]  {dest}")

            shutil.copytree(skill_dir, dest)
            print(f"  [COPY] {skill_dir} -> {dest}")

        print()

    print("Done.")

if __name__ == "__main__":
    sync_skills()
