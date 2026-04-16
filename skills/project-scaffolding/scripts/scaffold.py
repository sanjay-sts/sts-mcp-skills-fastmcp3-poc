# /// script
# dependencies = []
# requires-python = ">=3.10"
# ///

"""Project scaffolding script — generates directory structure from templates."""

import argparse
import json
import sys
from pathlib import Path


def load_templates(script_dir: Path) -> dict:
    """Load template definitions from assets/project-template.json."""
    template_file = script_dir.parent / "assets" / "project-template.json"
    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}", file=sys.stderr)
        print("Hint: Run this script from the skill directory", file=sys.stderr)
        sys.exit(2)
    with open(template_file) as f:
        return json.load(f)


def scaffold(template_name: str, project_name: str, output_dir: Path, templates: dict) -> dict:
    """Generate project structure from template. Returns manifest of created files."""
    if template_name not in templates:
        available = ", ".join(templates.keys())
        print(f"Error: Unknown template '{template_name}'", file=sys.stderr)
        print(f"Available templates: {available}", file=sys.stderr)
        sys.exit(3)

    template = templates[template_name]
    project_dir = output_dir / project_name
    created_files = []

    for file_def in template["files"]:
        file_path = project_dir / file_def["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        content = file_def.get("content", "").replace("{{project_name}}", project_name)
        file_path.write_text(content)
        created_files.append(str(file_path.relative_to(output_dir)))

    return {
        "template": template_name,
        "project_name": project_name,
        "output_dir": str(output_dir),
        "files_created": created_files,
        "description": template.get("description", ""),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate project structure from templates",
        epilog="Templates are defined in assets/project-template.json",
    )
    parser.add_argument("--template", help="Template name (e.g., python-package, fastapi-service)")
    parser.add_argument("--name", help="Project name (used for directory and package)")
    parser.add_argument("--output", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing")
    parser.add_argument("--list", action="store_true", help="List available templates")

    args = parser.parse_args()
    script_dir = Path(__file__).parent
    templates = load_templates(script_dir)

    if args.list:
        for name, tmpl in templates.items():
            print(f"  {name}: {tmpl.get('description', 'No description')}")
        return

    if not args.template or not args.name:
        parser.error("--template and --name are required (unless using --list)")

    if args.dry_run:
        template = templates.get(args.template)
        if not template:
            print(f"Error: Unknown template '{args.template}'", file=sys.stderr)
            sys.exit(3)
        print(json.dumps({
            "dry_run": True,
            "template": args.template,
            "project_name": args.name,
            "files": [f["path"].replace("{{project_name}}", args.name) for f in template["files"]],
        }, indent=2))
        return

    result = scaffold(args.template, args.name, Path(args.output), templates)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
