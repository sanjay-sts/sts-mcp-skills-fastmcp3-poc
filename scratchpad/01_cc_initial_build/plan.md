# FastMCP3 Remote Skill Provider PoC — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastMCP3-based skill provider that serves Agent Skills over a remote streamable HTTP MCP server, testable with MCP Inspector and a Python client.

**Architecture:** A `FastMCP("SkillHub")` server combines a `SkillsDirectoryProvider` (exposes `skills/` directory as `skill://` resources) with custom `@mcp.tool` functions for search and metadata. The server runs on streamable HTTP transport (port 8000, no auth). A Python client script exercises all capabilities: list, search, download, sync skills.

**Tech Stack:** Python 3.10+, FastMCP 3.2+, uvicorn (via FastMCP), starlette (via FastMCP)

**Plan location:** `scratchpad/01_cc_initial_build/plan.md` (copied during Task 1)

---

## File Structure

```
sts-mcp-skills-fastmcp3-poc/
├── pyproject.toml                              # Project config, fastmcp dependency
├── README.md                                   # Setup, usage, MCP Inspector instructions
│
├── scratchpad/01_cc_initial_build/             # Documentation for this build
│   ├── plan.md                                 # This plan
│   ├── requirements.md                         # Functional/non-functional requirements
│   ├── design.md                               # Architecture and key decisions
│   ├── task-list.md                            # Ordered checklist with status
│   └── implementation.md                       # Implementation notes
│
├── skills/                                     # Skills catalog (served by provider)
│   ├── code-review/                            # Simple skill — SKILL.md only
│   │   └── SKILL.md
│   └── project-scaffolding/                    # Complex skill — full structure
│       ├── SKILL.md
│       ├── scripts/scaffold.py                 # PEP 723 self-contained script
│       ├── references/templates-guide.md       # On-demand reference doc
│       └── assets/project-template.json        # Template asset
│
├── server/                                     # FastMCP3 server package
│   ├── __init__.py
│   └── main.py                                 # Server: providers + tools + HTTP transport
│
└── client/                                     # Test client
    └── test_client.py                          # Exercises all skill operations
```

---

## Task 0: Scratchpad Documentation

**Files:**
- Create: `scratchpad/01_cc_initial_build/plan.md`
- Create: `scratchpad/01_cc_initial_build/requirements.md`
- Create: `scratchpad/01_cc_initial_build/design.md`
- Create: `scratchpad/01_cc_initial_build/task-list.md`
- Create: `scratchpad/01_cc_initial_build/implementation.md`

- [ ] **Step 1: Create scratchpad directory**

```bash
mkdir -p scratchpad/01_cc_initial_build
```

- [ ] **Step 2: Write requirements.md**

```markdown
# Requirements — FastMCP3 Remote Skill Provider PoC

## Functional Requirements

1. **Skill Serving**: Serve Agent Skills (SKILL.md + supporting files) over MCP protocol
2. **Simple Skill**: At least one skill with SKILL.md only (Level 1+2 disclosure)
3. **Complex Skill**: At least one skill with scripts/, references/, assets/ (Level 3 disclosure)
4. **Remote Transport**: Server accessible via streamable HTTP (not just stdio)
5. **Skill Discovery**: Clients can list all available skills via `skill://` resource URIs
6. **Skill Manifests**: Clients can read `skill://{name}/_manifest` for file listings with sizes/hashes
7. **Skill Download**: Clients can download individual skills or sync all skills
8. **Search Tool**: MCP tool to search skills by keyword across names/descriptions
9. **Metadata Tool**: MCP tool to get detailed metadata for a specific skill
10. **Health Endpoint**: HTTP GET `/health` returns server status

## Non-Functional Requirements

1. **No Authentication**: No auth required — pure capability testing
2. **Hot Reload**: Server re-scans skills directory on each request (dev mode)
3. **MCP Inspector Compatible**: Testable via `npx @modelcontextprotocol/inspector`
4. **Python Client Compatible**: Testable via FastMCP Client + utilities
5. **Cross-Agent Skill Format**: Skills use universal Agent Skills frontmatter fields
```

- [ ] **Step 3: Write design.md**

```markdown
# Design — FastMCP3 Remote Skill Provider PoC

## Architecture

```
┌─────────────────────────────────────────────────┐
│              FastMCP("SkillHub")                 │
│                                                  │
│  ┌──────────────────────┐  ┌──────────────────┐ │
│  │ SkillsDirectoryProvider│  │ @mcp.tool        │ │
│  │  roots=./skills/      │  │  search_skills() │ │
│  │  supporting_files=    │  │  get_skill_meta()│ │
│  │    "resources"        │  │                  │ │
│  │  reload=True          │  │                  │ │
│  └──────────────────────┘  └──────────────────┘ │
│                                                  │
│  @mcp.custom_route("/health")                    │
│                                                  │
│  Transport: Streamable HTTP (0.0.0.0:8000)       │
└──────────────────────────────────────────────────┘
         │
         │ JSON-RPC 2.0 over HTTP
         ▼
┌────────────────────┐    ┌──────────────────────┐
│ Python test client │    │ MCP Inspector (npx)  │
│ FastMCP Client +   │    │ Streamable HTTP      │
│ utilities.skills   │    │ http://localhost:8000 │
└────────────────────┘    └──────────────────────┘
```

## Key Decisions

1. **No custom Provider subclass**: Use `SkillsDirectoryProvider` for skill resources + `@mcp.tool` decorators for search/metadata. Simpler than building a custom Provider class. FastMCP's LocalProvider handles the decorated tools automatically.

2. **`supporting_files="resources"`**: All supporting files appear as individual `skill://` resources in `list_resources()`. Better for testing/inspection than "template" mode where you'd need to read the manifest first.

3. **`reload=True`**: Re-scans skills directory on every request. Appropriate for dev/PoC — add skills at runtime without restart.

4. **Single `server/main.py`**: No separate provider.py needed. The server is small enough (~60 lines) to live in one file. The tools read SKILL.md files directly from disk for search/metadata.

5. **Universal frontmatter only for core fields**: Skills use `name`, `description`, `metadata` (author, version, tags). Claude-specific fields (`allowed-tools`, `effort`) added as additive enhancements.

## Data Flow

1. Server starts → SkillsDirectoryProvider scans `./skills/` → finds `code-review/` and `project-scaffolding/`
2. Client calls `list_resources()` → gets `skill://code-review/SKILL.md`, `skill://code-review/_manifest`, `skill://project-scaffolding/SKILL.md`, etc.
3. Client calls `read_resource("skill://code-review/SKILL.md")` → gets SKILL.md content
4. Client calls tool `search_skills(query="review")` → returns matching skills
5. Client calls tool `get_skill_metadata(skill_name="project-scaffolding")` → returns frontmatter + file listing
```

- [ ] **Step 4: Write task-list.md**

```markdown
# Task List — FastMCP3 Remote Skill Provider PoC

- [ ] Task 0: Scratchpad documentation
- [ ] Task 1: Project setup (pyproject.toml)
- [ ] Task 2: Simple skill (code-review)
- [ ] Task 3: Complex skill (project-scaffolding)
- [ ] Task 4: Server (main.py with provider + tools + HTTP)
- [ ] Task 5: Test client (test_client.py)
- [ ] Task 6: Verify with server + client
- [ ] Task 7: Update README.md
- [ ] Task 8: Commit
```

- [ ] **Step 5: Write implementation.md** (empty template, filled during build)

```markdown
# Implementation Notes — FastMCP3 Remote Skill Provider PoC

## Notes

(Filled during implementation)
```

- [ ] **Step 6: Copy plan to scratchpad**

Copy the plan file to `scratchpad/01_cc_initial_build/plan.md`.

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "sts-mcp-skills-fastmcp3-poc"
version = "0.1.0"
description = "PoC: FastMCP3-based skill provider over remote streamable HTTP MCP server"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=3.2.0",
]

[project.scripts]
skillhub = "server.main:main"
```

- [ ] **Step 2: Create server/__init__.py**

```python
```

(Empty file — makes `server` a package.)

- [ ] **Step 3: Install dependencies**

```bash
pip install -e .
```

Expected: Installs fastmcp and transitive deps (uvicorn, starlette, httpx, etc.)

- [ ] **Step 4: Verify fastmcp installed**

```bash
python -c "import fastmcp; print(fastmcp.__version__)"
```

Expected: `3.2.x` or higher

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml server/__init__.py
git commit -m "chore: project setup with fastmcp dependency"
```

---

## Task 2: Simple Skill — code-review

**Files:**
- Create: `skills/code-review/SKILL.md`

- [ ] **Step 1: Create skills directory**

```bash
mkdir -p skills/code-review
```

- [ ] **Step 2: Write SKILL.md**

```markdown
---
name: code-review
description: >
  Review code changes for quality, bugs, security issues, and style.
  Use when reviewing pull requests, diffs, or code snippets.
  Checks for: error handling, naming, complexity, test coverage,
  security vulnerabilities, and adherence to project conventions.
  NOT for generating new code or refactoring.
metadata:
  author: sanjay-sts
  version: "1.0"
  tags: "code-review,quality,security,style"
---

# Code Review

## Instructions

When reviewing code, follow this structured approach:

### 1. First Pass — Correctness
- Does the code do what it claims?
- Are there off-by-one errors, null dereferences, or race conditions?
- Are error paths handled?

### 2. Second Pass — Security
- Input validation on all external data
- No hardcoded secrets or credentials
- SQL injection, XSS, command injection checks
- Proper authentication/authorization checks

### 3. Third Pass — Quality
- Clear naming (variables, functions, classes)
- Functions under 30 lines where practical
- No dead code or commented-out blocks
- DRY — but don't over-abstract for single use cases

### 4. Fourth Pass — Tests
- Are critical paths tested?
- Do tests cover edge cases (empty input, boundary values, errors)?
- Are tests independent and deterministic?

### 5. Output Format

Provide findings as:

| Severity | File:Line | Issue | Suggestion |
|----------|-----------|-------|------------|
| HIGH     | path:42   | ...   | ...        |
| MEDIUM   | path:15   | ...   | ...        |
| LOW      | path:88   | ...   | ...        |

End with a summary: APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION.
```

- [ ] **Step 3: Verify file exists**

```bash
cat skills/code-review/SKILL.md | head -5
```

Expected: Shows the YAML frontmatter header.

- [ ] **Step 4: Commit**

```bash
git add skills/code-review/SKILL.md
git commit -m "feat: add simple code-review skill"
```

---

## Task 3: Complex Skill — project-scaffolding

**Files:**
- Create: `skills/project-scaffolding/SKILL.md`
- Create: `skills/project-scaffolding/scripts/scaffold.py`
- Create: `skills/project-scaffolding/references/templates-guide.md`
- Create: `skills/project-scaffolding/assets/project-template.json`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p skills/project-scaffolding/scripts
mkdir -p skills/project-scaffolding/references
mkdir -p skills/project-scaffolding/assets
```

- [ ] **Step 2: Write SKILL.md**

```markdown
---
name: project-scaffolding
description: >
  Scaffold new projects from templates with proper structure, config,
  and boilerplate. Use when creating new Python packages, FastAPI services,
  CLI tools, or MCP servers. Generates directory structure, config files,
  and starter code. NOT for modifying existing projects.
metadata:
  author: sanjay-sts
  version: "1.0"
  tags: "scaffolding,project,template,generator"
  compatibility: "python3"
---

# Project Scaffolding

## Instructions

### Available Templates
Read `references/templates-guide.md` for the full list of templates and when to use each.

### Workflow

1. Ask the user which template they want (or infer from context)
2. Read `references/templates-guide.md` for template details
3. Run the scaffold script to generate the project:
   ```bash
   uv run scripts/scaffold.py --template <template-name> --name <project-name> --output <directory>
   ```
4. Review the generated structure with the user
5. Customize generated files based on user requirements

### Template Data
The template definitions are in `assets/project-template.json`. The scaffold script reads this file to determine what files and directories to create.

### Script Help
```bash
uv run scripts/scaffold.py --help
```
```

- [ ] **Step 3: Write scripts/scaffold.py**

```python
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
    parser.add_argument("--template", required=True, help="Template name (e.g., python-package, fastapi-service)")
    parser.add_argument("--name", required=True, help="Project name (used for directory and package)")
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
```

- [ ] **Step 4: Write references/templates-guide.md**

```markdown
# Project Templates Guide

## Available Templates

### python-package
A standard Python package with pyproject.toml, src layout, and tests.
**Use when:** Creating reusable Python libraries, CLI tools, or utilities.
**Includes:** pyproject.toml, src/ layout, tests/, README.md, .gitignore

### fastapi-service
A FastAPI web service with routes, models, and Docker support.
**Use when:** Building REST APIs, microservices, or web backends.
**Includes:** main.py, routes/, models/, Dockerfile, requirements.txt, tests/

### mcp-server
A FastMCP3 server with tool and resource examples.
**Use when:** Building MCP servers for AI agent integration.
**Includes:** server.py, tools/, resources/, pyproject.toml, README.md

## Choosing a Template

| Need | Template | Why |
|------|----------|-----|
| Library/CLI tool | python-package | Standard packaging, src layout |
| REST API | fastapi-service | Production-ready FastAPI scaffold |
| AI agent tools | mcp-server | FastMCP3 with examples |
```

- [ ] **Step 5: Write assets/project-template.json**

```json
{
  "python-package": {
    "description": "Standard Python package with src layout and tests",
    "files": [
      {
        "path": "pyproject.toml",
        "content": "[project]\nname = \"{{project_name}}\"\nversion = \"0.1.0\"\nrequires-python = \">=3.10\"\n\n[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.backends\"\n"
      },
      {
        "path": "src/{{project_name}}/__init__.py",
        "content": "\"\"\"{{project_name}} package.\"\"\"\n\n__version__ = \"0.1.0\"\n"
      },
      {
        "path": "tests/__init__.py",
        "content": ""
      },
      {
        "path": "tests/test_{{project_name}}.py",
        "content": "from {{project_name}} import __version__\n\n\ndef test_version():\n    assert __version__ == \"0.1.0\"\n"
      },
      {
        "path": "README.md",
        "content": "# {{project_name}}\n"
      },
      {
        "path": ".gitignore",
        "content": "__pycache__/\n*.egg-info/\ndist/\n.venv/\n"
      }
    ]
  },
  "fastapi-service": {
    "description": "FastAPI web service with routes and Docker support",
    "files": [
      {
        "path": "main.py",
        "content": "from fastapi import FastAPI\n\napp = FastAPI(title=\"{{project_name}}\")\n\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}\n"
      },
      {
        "path": "requirements.txt",
        "content": "fastapi>=0.110\nuvicorn>=0.29\n"
      },
      {
        "path": "Dockerfile",
        "content": "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
      },
      {
        "path": "README.md",
        "content": "# {{project_name}}\n\nFastAPI service.\n\n```bash\nuvicorn main:app --reload\n```\n"
      }
    ]
  },
  "mcp-server": {
    "description": "FastMCP3 server with tool and resource examples",
    "files": [
      {
        "path": "server.py",
        "content": "from fastmcp import FastMCP\n\nmcp = FastMCP(\"{{project_name}}\")\n\n\n@mcp.tool\ndef hello(name: str) -> str:\n    \"\"\"Say hello.\"\"\"\n    return f\"Hello, {name}!\"\n\n\nif __name__ == \"__main__\":\n    mcp.run()\n"
      },
      {
        "path": "pyproject.toml",
        "content": "[project]\nname = \"{{project_name}}\"\nversion = \"0.1.0\"\nrequires-python = \">=3.10\"\ndependencies = [\"fastmcp>=3.2.0\"]\n"
      },
      {
        "path": "README.md",
        "content": "# {{project_name}}\n\nMCP server built with FastMCP3.\n\n```bash\nfastmcp run server.py --transport http\n```\n"
      }
    ]
  }
}
```

- [ ] **Step 6: Test scaffold script**

```bash
python skills/project-scaffolding/scripts/scaffold.py --help
```

Expected: Shows usage with `--template`, `--name`, `--output`, `--dry-run`, `--list`.

```bash
python skills/project-scaffolding/scripts/scaffold.py --list
```

Expected: Lists python-package, fastapi-service, mcp-server.

- [ ] **Step 7: Commit**

```bash
git add skills/project-scaffolding/
git commit -m "feat: add complex project-scaffolding skill with scripts, references, assets"
```

---

## Task 4: FastMCP Server

**Files:**
- Create: `server/main.py`

- [ ] **Step 1: Write server/main.py**

```python
"""SkillHub — FastMCP3 skill provider over streamable HTTP."""

import json
import os
import re
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from starlette.responses import JSONResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
HOST = os.environ.get("SKILLHUB_HOST", "0.0.0.0")
PORT = int(os.environ.get("SKILLHUB_PORT", "8000"))

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("SkillHub")

# Provider: exposes skills/ directory as skill:// resources
mcp.add_provider(
    SkillsDirectoryProvider(
        roots=SKILLS_DIR,
        supporting_files="resources",  # all files as individual resources
        reload=True,  # re-scan on every request (dev mode)
    )
)


# ---------------------------------------------------------------------------
# Health endpoint (not MCP — plain HTTP)
# ---------------------------------------------------------------------------

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    skill_dirs = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    return JSONResponse({"status": "healthy", "skills_count": len(skill_dirs), "skills": skill_dirs})


# ---------------------------------------------------------------------------
# Custom tools: search and metadata
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from SKILL.md content as a dict."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).split("\n"):
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _load_skills_index() -> list[dict]:
    """Scan skills directory and build an index of name + description + files."""
    index = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
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
    print(f"Skills directory: {SKILLS_DIR}")
    print(f"MCP endpoint: http://{HOST}:{PORT}/mcp")
    print(f"Health check:  http://{HOST}:{PORT}/health")
    mcp.run(transport="http", host=HOST, port=PORT)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify server starts**

```bash
python -m server.main
```

Expected: Prints startup info and starts listening on port 8000. Ctrl+C to stop.

- [ ] **Step 3: Verify health endpoint** (in a second terminal)

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","skills_count":2,"skills":["code-review","project-scaffolding"]}`

- [ ] **Step 4: Commit**

```bash
git add server/
git commit -m "feat: SkillHub server with skills provider, search/metadata tools, HTTP transport"
```

---

## Task 5: Test Client

**Files:**
- Create: `client/test_client.py`

- [ ] **Step 1: Create client directory**

```bash
mkdir -p client
```

- [ ] **Step 2: Write test_client.py**

```python
"""Test client for SkillHub — exercises all skill provider capabilities."""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

from fastmcp import Client
from fastmcp.utilities.skills import download_skill, list_skills, sync_skills


SERVER_URL = "http://localhost:8000/mcp"


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_list_skills(client: Client):
    """Test 1: Discover available skills."""
    section("1. List Skills")
    skills = await list_skills(client)
    for skill in skills:
        print(f"  - {skill.name}: {skill.description[:80]}...")
    print(f"\n  Total: {len(skills)} skill(s)")
    return skills


async def test_list_resources(client: Client):
    """Test 2: List all skill:// resources."""
    section("2. List Resources")
    resources = await client.list_resources()
    for r in resources:
        print(f"  {r.uri}")
    print(f"\n  Total: {len(resources)} resource(s)")


async def test_read_skill(client: Client, skill_name: str):
    """Test 3: Read a skill's SKILL.md content."""
    section(f"3. Read skill://{skill_name}/SKILL.md")
    content = await client.read_resource(f"skill://{skill_name}/SKILL.md")
    text = content[0].text if hasattr(content[0], "text") else str(content[0])
    preview = text[:300]
    print(f"  {preview}...")
    print(f"\n  Total length: {len(text)} chars")


async def test_read_manifest(client: Client, skill_name: str):
    """Test 4: Read a skill's manifest."""
    section(f"4. Read skill://{skill_name}/_manifest")
    content = await client.read_resource(f"skill://{skill_name}/_manifest")
    text = content[0].text if hasattr(content[0], "text") else str(content[0])
    manifest = json.loads(text)
    print(f"  Skill: {manifest.get('skill', 'N/A')}")
    for f in manifest.get("files", []):
        print(f"    {f['path']} ({f.get('size', '?')} bytes)")


async def test_search_skills(client: Client):
    """Test 5: Call search_skills tool."""
    section("5. Search Skills (query='review')")
    result = await client.call_tool("search_skills", {"query": "review"})
    text = result[0].text if hasattr(result[0], "text") else str(result[0])
    print(f"  {text}")

    section("5b. Search Skills (query='scaffold')")
    result = await client.call_tool("search_skills", {"query": "scaffold"})
    text = result[0].text if hasattr(result[0], "text") else str(result[0])
    print(f"  {text}")


async def test_get_metadata(client: Client):
    """Test 6: Call get_skill_metadata tool."""
    section("6. Get Skill Metadata (project-scaffolding)")
    result = await client.call_tool("get_skill_metadata", {"skill_name": "project-scaffolding"})
    text = result[0].text if hasattr(result[0], "text") else str(result[0])
    data = json.loads(text)
    print(f"  Name: {data.get('name')}")
    print(f"  Files: {len(data.get('files', []))}")
    print(f"  Total size: {data.get('total_size', 0)} bytes")
    for f in data.get("files", []):
        print(f"    {f['path']} ({f['size']} bytes)")


async def test_download_skill(client: Client):
    """Test 7: Download a single skill to a temp directory."""
    section("7. Download Skill (code-review)")
    with tempfile.TemporaryDirectory() as tmp:
        path = await download_skill(client, "code-review", Path(tmp))
        print(f"  Downloaded to: {path}")
        for f in Path(tmp).rglob("*"):
            if f.is_file():
                print(f"    {f.relative_to(tmp)}")


async def test_sync_skills(client: Client):
    """Test 8: Sync all skills to a temp directory."""
    section("8. Sync All Skills")
    with tempfile.TemporaryDirectory() as tmp:
        paths = await sync_skills(client, Path(tmp))
        print(f"  Synced {len(paths)} skill(s) to: {tmp}")
        for f in sorted(Path(tmp).rglob("*")):
            if f.is_file():
                print(f"    {f.relative_to(tmp)}")


async def run_all():
    print(f"Connecting to SkillHub at {SERVER_URL}...")
    async with Client(SERVER_URL) as client:
        await test_list_skills(client)
        await test_list_resources(client)
        await test_read_skill(client, "code-review")
        await test_read_manifest(client, "project-scaffolding")
        await test_search_skills(client)
        await test_get_metadata(client)
        await test_download_skill(client)
        await test_sync_skills(client)

    section("ALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(run_all())
```

- [ ] **Step 3: Commit**

```bash
git add client/
git commit -m "feat: test client for skill provider verification"
```

---

## Task 6: End-to-End Verification

- [ ] **Step 1: Start the server**

```bash
python -m server.main
```

Expected: Server starts, prints endpoint URLs.

- [ ] **Step 2: Run test client** (in another terminal)

```bash
python client/test_client.py
```

Expected output covers all 8 tests:
1. Lists 2 skills (code-review, project-scaffolding)
2. Lists all `skill://` resource URIs
3. Reads SKILL.md content for code-review
4. Reads manifest for project-scaffolding (shows files + sizes)
5. Search returns code-review for "review", project-scaffolding for "scaffold"
6. Metadata shows project-scaffolding with 4 files
7. Downloads code-review skill to temp dir
8. Syncs all skills to temp dir

- [ ] **Step 3: Test with MCP Inspector**

```bash
npx @modelcontextprotocol/inspector
```

1. Open `http://localhost:6274` in browser
2. Select **Streamable HTTP** transport
3. Enter URL: `http://localhost:8000/mcp`
4. Click **Connect**
5. **Resources tab**: Verify `skill://code-review/SKILL.md`, `skill://project-scaffolding/SKILL.md`, manifests, and supporting files appear
6. **Tools tab**: Verify `search_skills` and `get_skill_metadata` tools appear with parameter schemas
7. Test calling `search_skills` with query "review"
8. Test calling `get_skill_metadata` with skill_name "project-scaffolding"

- [ ] **Step 4: Verify health check**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","skills_count":2,"skills":["code-review","project-scaffolding"]}`

---

## Task 7: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# FastMCP3 Remote Skill Provider PoC

A proof-of-concept demonstrating FastMCP3's `SkillsDirectoryProvider` serving Agent Skills over a remote streamable HTTP MCP server. Skills are discoverable, searchable, and downloadable by any MCP client.

## Prerequisites

- Python 3.10+
- pip or uv

## Quick Start

```bash
# Install
pip install -e .

# Start the server
python -m server.main

# In another terminal — run the test client
python client/test_client.py
```

## Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

1. Open http://localhost:6274
2. Select **Streamable HTTP** transport
3. Enter URL: `http://localhost:8000/mcp`
4. Explore **Resources** (skill:// URIs) and **Tools** (search_skills, get_skill_metadata)

## Project Structure

```
skills/                     Skills catalog
  code-review/              Simple skill (SKILL.md only)
  project-scaffolding/      Complex skill (scripts, references, assets)
server/                     FastMCP3 server (streamable HTTP on :8000)
client/                     Python test client
```

## What This Demonstrates

- **SkillsDirectoryProvider**: Serves skills as `skill://` MCP resources
- **Streamable HTTP transport**: Remote access without auth (PoC)
- **Custom MCP tools**: `search_skills` and `get_skill_metadata`
- **Skill structure**: Simple (SKILL.md) and complex (with scripts, references, assets)
- **Client utilities**: `list_skills`, `download_skill`, `sync_skills` from FastMCP
- **Health endpoint**: `/health` for operational checks

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `http://localhost:8000/mcp` | MCP streamable HTTP endpoint |
| `http://localhost:8000/health` | Health check (plain HTTP GET) |
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with setup, usage, and MCP Inspector instructions"
```

---

## Task 8: Final Commit

- [ ] **Step 1: Stage and commit any remaining files**

```bash
git add scratchpad/
git commit -m "docs: add scratchpad with plan, requirements, design, and task list"
```

---

## Verification Summary

| Check | Command | Expected |
|-------|---------|----------|
| Server starts | `python -m server.main` | Prints endpoints, listens on :8000 |
| Health check | `curl localhost:8000/health` | JSON with status, 2 skills |
| Client tests | `python client/test_client.py` | 8 sections, "ALL TESTS PASSED" |
| MCP Inspector | `npx @modelcontextprotocol/inspector` | Resources + Tools visible |
| Scaffold script | `python skills/project-scaffolding/scripts/scaffold.py --list` | 3 templates listed |
