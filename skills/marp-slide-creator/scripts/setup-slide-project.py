"""setup-slide-project.py

Cross-platform utility for scaffolding a Marp slide project from the starter template.

Usage:
    python skills/marp-slide-creator/scripts/setup-slide-project.py <project-name> [--theme <theme>]

Examples:
    python skills/marp-slide-creator/scripts/setup-slide-project.py my-presentation
    python skills/marp-slide-creator/scripts/setup-slide-project.py my-presentation --theme prism-edge

Run from the repository root. Generated layout:

    slides/<project-name>/
    ├── <project-name>.md       # deck copied from slides/starter-template.md
    ├── themes/<theme>.css      # theme copy (keeps `themeSet` self-contained)
    └── assets/
        ├── fonts/              # only the fonts the theme references (empty for azure/crimson)
        └── diagrams/.gitkeep
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Console encoding SSoT lives in scripts/diagrams/compat.py; this file is
# copied standalone into agent directories, so import the sibling when shipped
# as a directory and fall back to the same lines as a single-file copy.
try:
    from compat import ensure_utf8_stdio
except ImportError:  # pragma: no cover - single-file copy without compat.py

    def ensure_utf8_stdio() -> None:
        """Force UTF-8 on stdout/stderr; skip streams that cannot be reconfigured."""
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError):
                pass


ensure_utf8_stdio()

THEMES: tuple[str, ...] = (
    "azure-clarity",
    "crimson-clarity",
    "prism-edge",
    "nebula-glass",
    "warm-sunnyday",
    "slate-minimal",
)
DEFAULT_THEME = "azure-clarity"

# Same pattern as scripts/diagrams/tests/test_fonts_manifest.py::FONT_REF_RE:
# the theme CSS stays the authority on which font files a deck needs.
FONT_REF_RE = re.compile(r"url\(['\"]?\.\./assets/fonts/([A-Za-z0-9_.-]+\.ttf)['\"]?\)")
THEME_LINE_RE = re.compile(r"^theme:.*$", re.MULTILINE)


def required_fonts(theme_css: Path) -> list[str]:
    """Font files the theme references, in first-seen order (deduplicated)."""
    return list(dict.fromkeys(FONT_REF_RE.findall(theme_css.read_text(encoding="utf-8"))))


def create_project(project_name: str, theme: str) -> int:
    """Scaffold the slide project directory structure. Returns a process exit code."""
    root = Path.cwd()
    theme_src = root / "themes" / f"{theme}.css"
    starter_src = root / "slides" / "starter-template.md"
    fonts_src_dir = root / "assets" / "fonts"

    missing = [p for p in (theme_src, starter_src) if not p.is_file()]
    if missing:
        print(
            f"Error: required source not found: {', '.join(str(p) for p in missing)}\n"
            "       Run this script from the repository root.",
            file=sys.stderr,
        )
        return 1

    project_dir = root / "slides" / project_name
    deck_path = project_dir / f"{project_name}.md"
    if deck_path.exists():
        print(
            f"Error: {deck_path} already exists; refusing to overwrite.\n"
            "       Delete it first or pick another project name.",
            file=sys.stderr,
        )
        return 1

    theme_dst = project_dir / "themes" / f"{theme}.css"
    fonts_dst_dir = project_dir / "assets" / "fonts"
    diagrams_dir = project_dir / "assets" / "diagrams"

    # 1. Deck from the starter template with the chosen theme.
    starter = starter_src.read_text(encoding="utf-8")
    deck, replaced = THEME_LINE_RE.subn(f"theme: {theme}", starter, count=1)
    if replaced != 1:  # pragma: no cover - starter template always has a theme line
        print(f"Error: no `theme:` line found in {starter_src}.", file=sys.stderr)
        return 1
    if not deck.endswith("\n"):
        deck += "\n"
    project_dir.mkdir(parents=True, exist_ok=True)
    deck_path.write_text(deck, encoding="utf-8")
    print(f"Created: {deck_path}")

    # 2. Self-contained theme copy (same relative layout as this repo, so
    # `../assets/fonts/…` keeps resolving from <project>/themes/).
    theme_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(theme_src, theme_dst)
    print(f"Created: {theme_dst}")

    # 3. Only the fonts the theme actually references (azure/crimson need none).
    fonts_dst_dir.mkdir(parents=True, exist_ok=True)
    fonts = required_fonts(theme_src)
    copied = 0
    for name in fonts:
        src = fonts_src_dir / name
        if not src.is_file():
            print(f"Warning: theme references missing font file: {src}", file=sys.stderr)
            continue
        shutil.copyfile(src, fonts_dst_dir / name)
        copied += 1
    if fonts:
        print(f"Created: {fonts_dst_dir}/ ({copied}/{len(fonts)} fonts)")
    else:
        print(f"Created: {fonts_dst_dir}/ (no bundled fonts needed for {theme})")

    # 4. Diagram output directory placeholder.
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    (diagrams_dir / ".gitkeep").touch()
    print(f"Created: {diagrams_dir}/")

    print("\nProject structure created successfully!")
    print(f"To lint, use: python skills/marp-slide-creator/scripts/marp-lint.py {deck_path}")
    print(f"To copy icons, use: python skills/marp-svg-icon-placer/scripts/copy-icons.py {project_name} <icon-names>")
    print("(Generate screenshots only via marp-cli --images png; never mix two image pipelines.)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Marp slide project from the starter template.")
    parser.add_argument("project_name", help="Name of the slide project (used as folder name)")
    parser.add_argument(
        "--theme",
        choices=THEMES,
        default=DEFAULT_THEME,
        help=f"Theme to scaffold with (default: {DEFAULT_THEME})",
    )
    args = parser.parse_args(argv)
    return create_project(args.project_name, args.theme)


if __name__ == "__main__":
    raise SystemExit(main())
