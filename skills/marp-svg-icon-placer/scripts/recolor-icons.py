"""recolor-icons.py

Cross-platform utility for changing SVG icon colors in a Marp slide project's assets directory.

Usage:
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py <project-name> <color> <icon1.svg> [icon2.svg ...]
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py <project-name> <color> all
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py --list-assets <project-name>

Examples:
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#2563eb" lightbulb.svg gear.svg
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py my-presentation "#ffffff" all
    python skills/marp-svg-icon-placer/scripts/recolor-icons.py --list-assets my-presentation

Color formats accepted:
    #rrggbb   e.g. #2563eb
    #rgb      e.g. #fff
    currentColor  (resets to theme-driven color)
    Any valid SVG color keyword  e.g. white, red
"""

import argparse
import re
import sys
from pathlib import Path

SLIDES_BASE_DIR = Path("slides")

# Attributes / properties that carry color values we want to replace
_COLOR_ATTRS = re.compile(
    r'(fill|stroke)\s*=\s*"(?!none)[^"]*"', re.IGNORECASE
)
_COLOR_STYLE = re.compile(
    r'(fill|stroke)\s*:\s*(?!none)[^;}"\']+', re.IGNORECASE
)


def _recolor_svg(content: str, color: str) -> str:
    """Replace fill/stroke color values inside SVG content."""
    # Replace attribute-style  fill="..." / stroke="..."
    content = _COLOR_ATTRS.sub(lambda m: f'{m.group(1)}="{color}"', content)
    # Replace inline-style     fill:... / stroke:...
    content = _COLOR_STYLE.sub(lambda m: f"{m.group(1)}: {color}", content)
    return content


def list_assets(project_name: str) -> None:
    """List SVG icons currently in the project's assets directory."""
    assets_dir = SLIDES_BASE_DIR / project_name / "assets"
    if not assets_dir.exists():
        print(f"Error: assets directory not found: {assets_dir}", file=sys.stderr)
        sys.exit(1)
    icons = sorted(assets_dir.glob("*.svg"))
    if not icons:
        print(f"No SVG icons found in {assets_dir}/")
        return
    print(f"SVG icons in {assets_dir}/ ({len(icons)}):")
    for icon in icons:
        print(f"  {icon.name}")


def recolor_icons(project_name: str, color: str, icon_names: list[str]) -> None:
    """Recolor SVG icons in the project's assets directory."""
    assets_dir = SLIDES_BASE_DIR / project_name / "assets"
    if not assets_dir.exists():
        print(f"Error: assets directory not found: {assets_dir}", file=sys.stderr)
        print(
            f"Copy icons first: "
            f"python skills/marp-svg-icon-placer/scripts/copy-icons.py {project_name} <icons>"
        )
        sys.exit(1)

    if icon_names == ["all"]:
        icon_files = list(assets_dir.glob("*.svg"))
        if not icon_files:
            print(f"No SVG icons found in {assets_dir}/")
            return
    else:
        icon_files = []
        for name in icon_names:
            if not name.endswith(".svg"):
                name += ".svg"
            path = assets_dir / name
            if not path.exists():
                print(f"Warning: icon not found in assets: {path}", file=sys.stderr)
                continue
            icon_files.append(path)

    updated = 0
    for icon_path in icon_files:
        original = icon_path.read_text(encoding="utf-8")
        recolored = _recolor_svg(original, color)
        if recolored == original:
            print(f"Skipped (no color attrs found): {icon_path.name}")
            continue
        icon_path.write_text(recolored, encoding="utf-8")
        print(f"Recolored: {icon_path.name}  ->  {color}")
        updated += 1

    print(f"\nUpdated {updated}/{len(icon_files)} icons in {assets_dir}/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Change SVG icon colors in a Marp slide project's assets directory."
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the slide project (folder name under slides/)",
    )
    parser.add_argument(
        "color",
        nargs="?",
        help='Target color value (e.g. "#2563eb", "white", "currentColor")',
    )
    parser.add_argument(
        "icons",
        nargs="*",
        metavar="ICON",
        help="SVG icon filenames to recolor (use 'all' to recolor every icon in assets/)",
    )
    parser.add_argument(
        "--list-assets",
        metavar="PROJECT_NAME",
        help="List SVG icons in the project's assets directory and exit",
    )
    args = parser.parse_args()

    if args.list_assets:
        list_assets(args.list_assets)
        return

    if not args.project_name:
        parser.error("project_name is required unless --list-assets is specified")
    if not args.color:
        parser.error("color is required")
    if not args.icons:
        parser.error("at least one icon name (or 'all') is required")

    recolor_icons(args.project_name, args.color, args.icons)


if __name__ == "__main__":
    main()
