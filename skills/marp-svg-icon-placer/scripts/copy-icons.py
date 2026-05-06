"""copy-icons.py

Cross-platform utility for copying SVG icons to Marp slide project assets.

Usage:
    python skills/marp-svg-icon-placer/scripts/copy-icons.py <project-name> <icon1.svg> [icon2.svg ...]
    python skills/marp-svg-icon-placer/scripts/copy-icons.py <project-name> all
    python skills/marp-svg-icon-placer/scripts/copy-icons.py --list

Examples:
    python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation lightbulb.svg gear.svg
    python skills/marp-svg-icon-placer/scripts/copy-icons.py my-presentation all
    python skills/marp-svg-icon-placer/scripts/copy-icons.py --list
"""

import argparse
import shutil
import sys
from pathlib import Path

ICONS_SOURCE_DIR = Path("skills/marp-svg-icon-placer/references/icons")
SLIDES_BASE_DIR = Path("slides")


def list_icons() -> None:
    """List all available icons."""
    if not ICONS_SOURCE_DIR.exists():
        print(f"Icons directory not found: {ICONS_SOURCE_DIR}", file=sys.stderr)
        sys.exit(1)
    icons = sorted(ICONS_SOURCE_DIR.glob("*.svg"))
    print(f"Available icons ({len(icons)}):")
    for icon in icons:
        print(f"  {icon.name}")


def search_icons(query: str) -> None:
    """Search available icons by name substring (case-insensitive)."""
    if not ICONS_SOURCE_DIR.exists():
        print(f"Icons directory not found: {ICONS_SOURCE_DIR}", file=sys.stderr)
        sys.exit(1)
    icons = sorted(ICONS_SOURCE_DIR.glob("*.svg"))
    matches = [icon for icon in icons if query.lower() in icon.name.lower()]
    if matches:
        print(f"Icons matching '{query}' ({len(matches)}):")
        for icon in matches:
            print(f"  {icon.name}")
    else:
        print(f"No icons matching '{query}' found.")
        print("Tip: run --list to see all available icons.")


def copy_icons(project_name: str, icon_names: list[str]) -> None:
    """Copy SVG icons from the icon catalog to the project's assets directory."""
    assets_dir = SLIDES_BASE_DIR / project_name / "assets"

    if not assets_dir.exists():
        print(f"Error: assets directory not found: {assets_dir}", file=sys.stderr)
        print(f"Create the project first: python skills/marp-slide-creator/scripts/setup-slide-project.py {project_name}")
        sys.exit(1)

    if icon_names == ["all"]:
        if not ICONS_SOURCE_DIR.exists():
            print(f"Error: icons source directory not found: {ICONS_SOURCE_DIR}", file=sys.stderr)
            sys.exit(1)
        icon_files = list(ICONS_SOURCE_DIR.glob("*.svg"))
        if not icon_files:
            print("No SVG icons found in source directory.")
            return
        for icon_file in icon_files:
            dest = assets_dir / icon_file.name
            shutil.copy2(icon_file, dest)
            print(f"Copied: {icon_file.name} -> {dest}")
        print(f"\nCopied {len(icon_files)} icons to {assets_dir}/")
    else:
        copied = 0
        for icon_name in icon_names:
            # Allow specifying with or without .svg extension
            if not icon_name.endswith(".svg"):
                icon_name += ".svg"
            src = ICONS_SOURCE_DIR / icon_name
            if not src.exists():
                print(f"Warning: icon not found: {src}", file=sys.stderr)
                continue
            dest = assets_dir / icon_name
            shutil.copy2(src, dest)
            print(f"Copied: {icon_name} -> {dest}")
            copied += 1
        print(f"\nCopied {copied}/{len(icon_names)} icons to {assets_dir}/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy SVG icons to a Marp slide project's assets directory."
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the slide project (folder name under slides/)",
    )
    parser.add_argument(
        "icons",
        nargs="*",
        metavar="ICON",
        help="SVG icon filenames to copy (use 'all' to copy every icon)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available icons and exit",
    )
    parser.add_argument(
        "--search",
        metavar="QUERY",
        help="Search available icons by name substring and exit",
    )
    args = parser.parse_args()

    if args.list:
        list_icons()
        return

    if args.search:
        search_icons(args.search)
        return

    if not args.project_name:
        parser.error("project_name is required unless --list or --search is specified")

    if not args.icons:
        parser.error("at least one icon name (or 'all') is required")

    copy_icons(args.project_name, args.icons)


if __name__ == "__main__":
    main()
