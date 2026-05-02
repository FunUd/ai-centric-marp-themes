"""setup-slide-project.py

Cross-platform utility for Marp slide project setup.
Handles directory creation and asset copying without relying on shell-specific commands.

Usage:
    python skills/scripts/setup-slide-project.py <project-name>
    python skills/scripts/setup-slide-project.py <project-name> --copy-icons icon1.svg icon2.svg
    python skills/scripts/setup-slide-project.py <project-name> --copy-icons all

Examples:
    python skills/scripts/setup-slide-project.py my-presentation
    python skills/scripts/setup-slide-project.py my-presentation --copy-icons lightbulb.svg gear.svg
    python skills/scripts/setup-slide-project.py my-presentation --copy-icons all
"""

import argparse
import shutil
import sys
from pathlib import Path

ICONS_SOURCE_DIR = Path("skills/marp-svg-icon-placer/references/icons")
SLIDES_BASE_DIR = Path("slides")


def create_project(project_name: str) -> Path:
    """Create the slide project directory structure."""
    project_dir = SLIDES_BASE_DIR / project_name
    assets_dir = project_dir / "assets"

    assets_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {project_dir}/")
    print(f"Created: {assets_dir}/")
    return project_dir


def copy_icons(project_name: str, icon_names: list[str]) -> None:
    """Copy SVG icons from the icon catalog to the project's assets directory."""
    assets_dir = SLIDES_BASE_DIR / project_name / "assets"

    if not assets_dir.exists():
        print(f"Error: assets directory not found: {assets_dir}", file=sys.stderr)
        print("Run without --copy-icons first to create the project structure.")
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
        description="Set up a Marp slide project directory structure."
    )
    parser.add_argument("project_name", help="Name of the slide project (used as folder name)")
    parser.add_argument(
        "--copy-icons",
        nargs="+",
        metavar="ICON",
        help="SVG icon filenames to copy into assets/ (use 'all' to copy every icon)",
    )
    parser.add_argument(
        "--list-icons",
        action="store_true",
        help="List all available icons and exit",
    )
    args = parser.parse_args()

    if args.list_icons:
        if not ICONS_SOURCE_DIR.exists():
            print(f"Icons directory not found: {ICONS_SOURCE_DIR}", file=sys.stderr)
            sys.exit(1)
        icons = sorted(ICONS_SOURCE_DIR.glob("*.svg"))
        print(f"Available icons ({len(icons)}):")
        for icon in icons:
            print(f"  {icon.name}")
        return

    create_project(args.project_name)

    if args.copy_icons:
        copy_icons(args.project_name, args.copy_icons)


if __name__ == "__main__":
    main()
