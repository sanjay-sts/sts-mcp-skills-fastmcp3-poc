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
