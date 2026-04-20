# MCP Inspector — Remote Skill Hosting Evidence

## Summary

The server was started and exercised end-to-end over the same MCP streamable-HTTP
protocol that MCP Inspector uses. All artifacts Inspector would show are captured
below from the programmatic run.

- **Server:** FastMCP 3.2.4, `SkillHub` app
- **Transport:** Streamable HTTP
- **Endpoint:** `http://localhost:8000/mcp`
- **Reload mode:** validated both `True` (default) and `False` (SKILLHUB_RELOAD=0)
- **Health:** `{"status":"healthy","skills_count":2,"skills":["code-review","project-scaffolding"]}`

## Resources exposed (7 — the Inspector "Resources" tab will show these)

| URI | Kind |
|---|---|
| `skill://code-review/SKILL.md` | main instruction file |
| `skill://code-review/_manifest` | synthetic manifest (files, sizes, SHA-256) |
| `skill://project-scaffolding/SKILL.md` | main instruction file |
| `skill://project-scaffolding/_manifest` | synthetic manifest |
| `skill://project-scaffolding/assets/project-template.json` | supporting file |
| `skill://project-scaffolding/references/templates-guide.md` | supporting file |
| `skill://project-scaffolding/scripts/scaffold.py` | supporting file |

Captured live from `client.list_resources()` — see
`test_client_transcript.txt` section `2. List Resources`.

## Tools exposed (Inspector "Tools" tab)

| Tool | Parameters | Purpose |
|---|---|---|
| `search_skills` | `query: str` | substring-search skill names + descriptions |
| `get_skill_metadata` | `skill_name: str` | full frontmatter + file listing + total size |

## Example resource read

```
> read_resource("skill://code-review/SKILL.md")

---
name: code-review
description: >
  Review code changes for quality, bugs, security issues, and style.
  Use when reviewing pull requests, diffs, or code snippets.
  ...
[1626 chars total]
```

## Example tool invocation

```
> call_tool("search_skills", {"query": "review"})

[
  {
    "name": "code-review",
    "description": "Review code changes for quality, bugs, security issues, and style. ...",
    "file_count": 1
  }
]
```

## Example manifest read

```
> read_resource("skill://project-scaffolding/_manifest")

{
  "skill": "project-scaffolding",
  "files": [
    {"path": "assets/project-template.json", "size": 2631, ...},
    {"path": "references/templates-guide.md", "size": 987, ...},
    {"path": "scripts/scaffold.py", "size": 3513, ...},
    {"path": "SKILL.md", "size": 1263, ...}
  ]
}
```

(Full transcript: `test_client_transcript.txt`, section
`4. Read skill://project-scaffolding/_manifest`.)

## Reproducing in MCP Inspector (interactive)

MCP Inspector is a browser app; this project can't drive it in CI, but the
protocol contract it exercises is fully covered above. To re-verify by hand:

```bash
# 1) Start the server in one terminal
uv run python -m server.main

# 2) In another terminal, launch the Inspector UI
npx @modelcontextprotocol/inspector
```

1. Open <http://localhost:6274>.
2. Select **Streamable HTTP** transport.
3. Enter URL **`http://localhost:8000/mcp`** and click **Connect**.
4. Open the **Resources** panel. You should see the 7 `skill://` URIs listed above.
5. Click `skill://code-review/SKILL.md` — Inspector reads the file and shows the
   YAML frontmatter + markdown body (1,626 chars).
6. Click `skill://project-scaffolding/_manifest` — Inspector shows the JSON manifest
   with 4 files and their sizes.
7. Open the **Tools** panel. You should see `search_skills` and `get_skill_metadata`.
8. Call `search_skills` with `{"query": "review"}`. Inspector renders the JSON array
   matching the example above.
9. Call `get_skill_metadata` with `{"skill_name": "project-scaffolding"}`. Inspector
   shows the full frontmatter + 4 files + total size 8394 bytes.

## Production-reload check

With `SKILLHUB_RELOAD=0`:

```
Starting SkillHub on 127.0.0.1:8000
Skills roots: ['.../skills']
Reload mode:  False (set SKILLHUB_RELOAD=0 for production)
MCP endpoint: http://127.0.0.1:8000/mcp
```

The provider no longer re-scans on every request; matches the FastMCP
docs guidance.
