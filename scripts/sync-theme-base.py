#!/usr/bin/env python3
"""sync-theme-base.py — Propagate shared structural CSS into themes.

`themes/_base.css` is the single source of truth for layout containers,
grids, callouts, badges, alignment utilities and display controls whose
structure is identical across themes modulo the `--xx-` token prefix. Each
listed theme carries the section between `<base:name>` markers; this script
rewrites those regions from the base with the prefix substituted.

Usage:
    python scripts/sync-theme-base.py           # rewrite theme regions
    python scripts/sync-theme-base.py --check   # fail on drift (CI gate)

Rules (enforced in both modes):
- base bodies use ONLY `--ac-` variables and contain no `/* */` comments,
  so substitution is purely mechanical;
- every section is used by at least two themes;
- a theme lists a section iff its markers exist, and vice versa.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
THEMES_DIR = ROOT_DIR / "themes"
BASE_PATH = THEMES_DIR / "_base.css"

sys.path.insert(0, str(SCRIPT_DIR / "diagrams"))
from compat import ensure_utf8_stdio  # noqa: E402

# Theme -> token prefix used inside shared bodies.
PREFIX = {
    "azure-clarity": "ac",
    "crimson-clarity": "cc",
    "warm-sunnyday": "ws",
    "prism-edge": "pe",
    "nebula-glass": "ng",
    "slate-minimal": "sm",
}

SECTION_RE = re.compile(r"/\*\s*==\s*([\w-]+)\s*==\s*\*/")
THEMES_RE = re.compile(r"/\*\s*themes:\s*([^*]+?)\s*\*/")
OPEN_RE = re.compile(r"/\*\s*<base:([\w-]+)>\s*.*?\*/")
CLOSE_RE = re.compile(r"/\*\s*</base:([\w-]+)>\s*\*/")
OTHER_PREFIX_RE = re.compile(r"--(" + "|".join(sorted(set(PREFIX.values()) - {"ac"})) + r")-")


def parse_base() -> dict[str, tuple[list[str], str]]:
    """name -> (themes, body)."""
    text = BASE_PATH.read_text(encoding="utf-8")
    parts = SECTION_RE.split(text)
    sections: dict[str, tuple[list[str], str]] = {}
    for i in range(1, len(parts), 2):
        name, rest = parts[i], parts[i + 1]
        match = THEMES_RE.search(rest)
        if not match:
            raise RuntimeError(f"_base.css section '{name}' declares no themes")
        themes = [t.strip() for t in match.group(1).split(",")]
        body = rest[match.end() :].strip("\n")
        # A following section header would have split already; cut stray text.
        body = body.split("/* ==")[0].rstrip("\n")
        if name in sections:
            raise RuntimeError(f"_base.css section '{name}' is duplicated")
        sections[name] = (themes, body)
    return sections


def check_base_hygiene(sections: dict[str, tuple[list[str], str]]) -> list[str]:
    problems: list[str] = []
    for name, (themes, body) in sections.items():
        if len(themes) < 2:
            problems.append(f"[LONELY] section '{name}' is used by a single theme")
        for theme in themes:
            if theme not in PREFIX:
                problems.append(f"[THEME] section '{name}' lists unknown theme '{theme}'")
        if "/*" in body or "*/" in body:
            problems.append(f"[COMMENT] section '{name}' contains a comment")
        if OTHER_PREFIX_RE.search(body):
            problems.append(f"[PREFIX] section '{name}' uses a non-ac token prefix")
    return problems


def theme_markers(text: str) -> dict[str, tuple[int, int]]:
    """name -> (content start, content end) offsets of the marker region."""
    regions: dict[str, tuple[int, int]] = {}
    for open_match in OPEN_RE.finditer(text):
        name = open_match.group(1)
        close_match = CLOSE_RE.search(text, open_match.end())
        if not close_match or close_match.group(1) != name:
            raise RuntimeError(f"unclosed <base:{name}> marker region")
        if name in regions:
            raise RuntimeError(f"duplicated <base:{name}> marker region")
        regions[name] = (open_match.end(), close_match.start())
    return regions


def sync_theme(theme: str, sections: dict[str, tuple[list[str], str]], check: bool) -> list[str]:
    path = THEMES_DIR / f"{theme}.css"
    text = path.read_text(encoding="utf-8")
    regions = theme_markers(text)
    expected = {
        name for name, (themes, _body) in sections.items() if theme in themes
    }
    problems: list[str] = []
    for name in sorted(set(regions) - expected):
        problems.append(f"[STALE] {theme}.css carries <base:{name}> but _base.css does not list {theme}")
    for name in sorted(expected - set(regions)):
        problems.append(f"[MISSING] {theme}.css lacks <base:{name}> markers")
    if problems:
        return problems
    rebuilt = text
    drift: list[str] = []
    # Replace from the end so offsets stay valid.
    for name in sorted(regions, key=lambda n: regions[n][0], reverse=True):
        _, body = sections[name]
        want = body.replace("--ac-", f"--{PREFIX[theme]}-")
        start, end = regions[name]
        current = text[start:end].strip("\n")
        if current != want:
            drift.append(f"[DRIFT] {theme}.css <base:{name}> differs from _base.css")
            rebuilt = rebuilt[:start] + "\n" + want + "\n" + rebuilt[end:]
    if drift and not check:
        import tempfile

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=str(path.parent), delete=False
            ) as tmp:
                tmp.write(rebuilt)
                tmp_path = Path(tmp.name)
            tmp_path.replace(path)
        except OSError as error:
            raise RuntimeError(f"cannot write {path}: {error}") from error
    return drift


def main() -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Sync shared theme CSS from themes/_base.css.")
    parser.add_argument("--check", action="store_true", help="Fail on drift.")
    args = parser.parse_args()
    try:
        sections = parse_base()
    except (OSError, RuntimeError) as error:
        print(f"[ERROR] cannot parse _base.css: {error}", file=sys.stderr)
        return 1
    problems = check_base_hygiene(sections)
    for theme in sorted(PREFIX):
        try:
            problems.extend(sync_theme(theme, sections, args.check))
        except (OSError, RuntimeError) as error:
            problems.append(f"[ERROR] {theme}: {error}")
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print(
            f"FAILED: {len(problems)} theme-base problem(s).\n"
            f"       run: python scripts/sync-theme-base.py",
            file=sys.stderr,
        )
        return 1
    mode = "in sync" if args.check else "synced"
    print(f"[OK] {len(sections)} base sections {mode} across {len(PREFIX)} themes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
