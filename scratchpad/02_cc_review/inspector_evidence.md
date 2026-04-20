# MCP Inspector — Remote Skill Hosting Evidence

## Summary

The server was started and exercised end-to-end over the same MCP streamable-HTTP
protocol that MCP Inspector uses. All artifacts Inspector would show are captured
below from the programmatic run, and the "Post-fix Inspector capture" section at
the end contains the actual JSON Inspector returned against the live server.

- **Server:** FastMCP 3.2.4, `SkillHub` app
- **Transport:** Streamable HTTP
- **Endpoint:** `http://localhost:10001/skillmcp`
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
3. Enter URL **`http://localhost:10001/skillmcp`** and click **Connect**.
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
Starting SkillHub on 127.0.0.1:10001
Skills roots: ['.../skills']
Reload mode:  False (set SKILLHUB_RELOAD=0 for production)
MCP endpoint: http://127.0.0.1:10001/skillmcp
```

The provider no longer re-scans on every request; matches the FastMCP
docs guidance.

---

## Post-fix Inspector capture (live)

After commit `3a860b4` (single-line SKILL.md descriptions to dodge FastMCP's
naive frontmatter parser), MCP Inspector's `listResources` returned the JSON
below. Every resource now has a resolved `description`, correct `mimeType`, and
the expected `_meta.fastmcp.skill` grouping with `is_manifest` flags.

```json
{
  "resources": [
    {
      "name": "code-review/SKILL.md",
      "uri": "skill://code-review/SKILL.md",
      "description": "Review code changes for quality, bugs, security issues, and style. Use when reviewing pull requests, diffs, or code snippets. Checks for error handling, naming, complexity, test coverage, security vulnerabilities, and adherence to project conventions. NOT for generating new code or refactoring.",
      "mimeType": "text/markdown",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "code-review",
            "is_manifest": false
          }
        }
      }
    },
    {
      "name": "code-review/_manifest",
      "uri": "skill://code-review/_manifest",
      "description": "File listing for code-review",
      "mimeType": "application/json",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "code-review",
            "is_manifest": true
          }
        }
      }
    },
    {
      "name": "project-scaffolding/SKILL.md",
      "uri": "skill://project-scaffolding/SKILL.md",
      "description": "Scaffold new projects from templates with proper structure, config, and boilerplate. Use when creating new Python packages, FastAPI services, CLI tools, or MCP servers. Generates directory structure, config files, and starter code. NOT for modifying existing projects.",
      "mimeType": "text/markdown",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "project-scaffolding",
            "is_manifest": false
          }
        }
      }
    },
    {
      "name": "project-scaffolding/_manifest",
      "uri": "skill://project-scaffolding/_manifest",
      "description": "File listing for project-scaffolding",
      "mimeType": "application/json",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "project-scaffolding",
            "is_manifest": true
          }
        }
      }
    },
    {
      "name": "project-scaffolding/assets/project-template.json",
      "uri": "skill://project-scaffolding/assets/project-template.json",
      "description": "File from project-scaffolding skill",
      "mimeType": "application/json",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "project-scaffolding"
          }
        }
      }
    },
    {
      "name": "project-scaffolding/references/templates-guide.md",
      "uri": "skill://project-scaffolding/references/templates-guide.md",
      "description": "File from project-scaffolding skill",
      "mimeType": "text/markdown",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "project-scaffolding"
          }
        }
      }
    },
    {
      "name": "project-scaffolding/scripts/scaffold.py",
      "uri": "skill://project-scaffolding/scripts/scaffold.py",
      "description": "File from project-scaffolding skill",
      "mimeType": "text/x-python",
      "_meta": {
        "fastmcp": {
          "tags": [],
          "skill": {
            "name": "project-scaffolding"
          }
        }
      }
    }
  ]
}
```

This confirms the full remote-hosting contract end-to-end through the official
MCP Inspector: 7 resources, correct mime types, resolved descriptions,
SkillsDirectoryProvider `_meta` grouping intact.
