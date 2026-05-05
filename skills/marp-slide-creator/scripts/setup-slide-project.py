"""setup-slide-project.py

Cross-platform utility for creating Marp slide project directory structure.

Usage:
    python skills/marp-slide-creator/scripts/setup-slide-project.py <project-name>

Examples:
    python skills/marp-slide-creator/scripts/setup-slide-project.py my-presentation
"""

import argparse
from pathlib import Path

SLIDES_BASE_DIR = Path("slides")


def create_project(project_name: str) -> Path:
    """Create the slide project directory structure."""
    project_dir = SLIDES_BASE_DIR / project_name
    assets_dir = project_dir / "assets"

    assets_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {project_dir}/")
    print(f"Created: {assets_dir}/")
    return project_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up a Marp slide project directory structure."
    )
    parser.add_argument("project_name", help="Name of the slide project (used as folder name)")
    args = parser.parse_args()

    create_project(args.project_name)
    print(f"\nProject structure created successfully!")
    print(f"To copy icons, use: python skills/marp-svg-icon-placer/scripts/copy-icons.py {args.project_name} <icon-names>")
    print(f"To check overflow, use: python skills/marp-slide-creator/scripts/marp-diagnostics.py slides/{args.project_name}/{args.project_name}.md (writes slides/{args.project_name}/preview.html and slides/{args.project_name}/assets/dom-metrics.json)")


if __name__ == "__main__":
    main()
