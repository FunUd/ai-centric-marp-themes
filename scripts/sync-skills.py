#!/usr/bin/env python3
"""
sync-skills.py
Sync contents of `skills/` (source of truth) to various AI agent directories.
Removes existing directories in targets before copying.
"""

import argparse
import shutil
import sys
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

# Prefixes/names owned by this repo. Only these are removed as stale so
# unrelated or system-provided skills are never deleted.
STALE_NAMES = ("theme-expert-", "slide-expert-", "marp-", "theme-creator", "slide-content-designer")


def _is_within_root(path: Path, root: Path) -> bool:
    """Return True when path resolves inside root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def _dirs_differ(src: Path, dst: Path) -> str | None:
    """Return a reason when dst is missing or differs from src, else None."""
    if not dst.exists():
        return "missing"

    def _relevant(root: Path) -> set[Path]:
        out: set[Path] = set()
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if "__pycache__" in rel.parts or p.suffix == ".pyc":
                continue
            out.add(rel)
        return out

    src_files = _relevant(src)
    dst_files = _relevant(dst)
    if src_files != dst_files:
        return "file list differs"
    for rel in src_files:
        try:
            if (src / rel).read_bytes() != (dst / rel).read_bytes():
                return f"content differs: {rel}"
        except OSError:
            return f"unreadable: {rel}"
    return None


def sync_skills(check: bool = False) -> int:
    if not SOURCE_DIR.exists():
        print(f"[ERROR] Source directory '{SOURCE_DIR}' not found.")
        return 1

    skill_dirs = [d for d in SOURCE_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    if not skill_dirs:
        print("[INFO] No skill directories found in 'skills/'.")
        return 1

    print(f"Found {len(skill_dirs)} skill(s): {[d.name for d in skill_dirs]}\n")

    failures: list[str] = []
    for target_root in TARGET_ROOTS:
        if not target_root.exists():
            # Targets are gitignored agent dirs; a fresh checkout/CI has none.
            # Missing is not drift — only existing dirs are verified.
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
                    if target_item.name.startswith(STALE_NAMES):
                        if check:
                            print(f"  [DRIFT] stale {target_item} would be removed")
                            failures.append(f"stale: {target_item}")
                            continue
                        try:
                            shutil.rmtree(target_item)
                        except OSError as error:
                            print(f"  [ERROR] cannot remove {target_item}: {error}")
                            failures.append(f"rmtree failed: {target_item}")
                            continue
                        print(f"  [DEL STALE] {target_item}")

        for skill_dir in skill_dirs:
            dest = target_root / skill_dir.name
            if not _is_within_root(dest, target_root):
                raise RuntimeError(f"Refusing to write outside target root: {dest}")

            if check:
                reason = _dirs_differ(skill_dir, dest)
                if reason:
                    print(f"  [DRIFT] {dest}: {reason}")
                    failures.append(f"drift: {dest}: {reason}")
                continue

            try:
                if dest.exists():
                    shutil.rmtree(dest)
                    print(f"  [DEL]  {dest}")

                shutil.copytree(skill_dir, dest)
            except OSError as error:
                print(f"  [ERROR] cannot sync {skill_dir} -> {dest}: {error}")
                failures.append(f"copy failed: {dest}")
                continue
            print(f"  [COPY] {skill_dir} -> {dest}")

        print()

    if failures:
        print(f"FAILED: {len(failures)} problem(s).")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("Done.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync skills/ to agent directories.")
    parser.add_argument("--check", action="store_true", help="Fail if any target is missing or stale, without writing.")
    args = parser.parse_args()
    raise SystemExit(sync_skills(check=args.check))
