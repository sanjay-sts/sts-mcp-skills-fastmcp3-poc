"""SkillHub — FastMCP3 skill provider over streamable HTTP."""

import json
import os
import re
from pathlib import Path

import yaml

from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from starlette.responses import JSONResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
AGENTS_SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"
HOST = os.environ.get("SKILLHUB_HOST", "0.0.0.0")
PORT = int(os.environ.get("SKILLHUB_PORT", "8000"))
RELOAD = os.environ.get("SKILLHUB_RELOAD", "1") not in ("0", "false", "False", "")

# Build list of skill roots (project-local + cross-agent standard)
skill_roots = [SKILLS_DIR]
if AGENTS_SKILLS_DIR.exists():
    skill_roots.append(AGENTS_SKILLS_DIR)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("SkillHub")

# Provider: exposes skills directories as skill:// resources
mcp.add_provider(
    SkillsDirectoryProvider(
        roots=skill_roots,
        supporting_files="resources",  # all files as individual resources
        reload=RELOAD,  # SKILLHUB_RELOAD=1 dev; set 0 in production (per FastMCP docs)
    )
)


# ---------------------------------------------------------------------------
# Health endpoint (not MCP — plain HTTP)
# ---------------------------------------------------------------------------

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    skill_dirs = []
    for skills_dir in skill_roots:
        if skills_dir.exists():
            skill_dirs.extend(
                d.name for d in skills_dir.iterdir()
                if d.is_dir() and (d / "SKILL.md").exists()
            )
    return JSONResponse({"status": "healthy", "skills_count": len(skill_dirs), "skills": skill_dirs})


# ---------------------------------------------------------------------------
# Custom tools: search and metadata
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from SKILL.md content as a dict."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def _load_skills_index() -> list[dict]:
    """Scan skills directories and build an index of name + description + files."""
    index = []
    for skills_dir in skill_roots:
        if not skills_dir.exists():
            continue
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_dir.is_dir() or not skill_md.exists():
                continue
            frontmatter = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            files = []
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    files.append({
                        "path": str(f.relative_to(skill_dir)),
                        "size": f.stat().st_size,
                    })
            index.append({
                "name": frontmatter.get("name", skill_dir.name),
                "description": frontmatter.get("description", ""),
                "directory": skill_dir.name,
                "frontmatter": frontmatter,
                "files": files,
                "total_size": sum(f["size"] for f in files),
            })
    return index


@mcp.tool
def search_skills(query: str) -> str:
    """Search skills by keyword across names and descriptions.

    Args:
        query: Search term (case-insensitive, matched against name and description)

    Returns:
        JSON array of matching skills with name, description, and file count.
    """
    query_lower = query.lower()
    results = []
    for skill in _load_skills_index():
        name = skill["name"].lower()
        desc = skill["description"].lower()
        if query_lower in name or query_lower in desc:
            results.append({
                "name": skill["name"],
                "description": skill["description"],
                "file_count": len(skill["files"]),
            })
    return json.dumps(results, indent=2)


@mcp.tool
def get_skill_metadata(skill_name: str) -> str:
    """Get detailed metadata for a specific skill.

    Args:
        skill_name: The skill directory name (e.g., 'code-review', 'project-scaffolding')

    Returns:
        JSON object with frontmatter fields, file listing, and total size.
    """
    for skill in _load_skills_index():
        if skill["directory"] == skill_name or skill["name"] == skill_name:
            return json.dumps(skill, indent=2)
    return json.dumps({"error": f"Skill '{skill_name}' not found"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print(f"Starting SkillHub on {HOST}:{PORT}")
    print(f"Skills roots: {[str(r) for r in skill_roots]}")
    print(f"Reload mode:  {RELOAD} (set SKILLHUB_RELOAD=0 for production)")
    print(f"MCP endpoint: http://{HOST}:{PORT}/mcp")
    print(f"Health check:  http://{HOST}:{PORT}/health")
    mcp.run(transport="http", host=HOST, port=PORT)


if __name__ == "__main__":
    main()
