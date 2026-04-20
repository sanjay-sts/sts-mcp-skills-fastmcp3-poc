# CLAUDE.md — Agent Guide

This file is consumed by AI coding assistants (Claude Code, Cursor, etc.) at session
start. It gives a fast, agent-friendly orientation to the repo.

## What this project is

A proof of concept that hosts **Agent Skills** (agentskills.io open standard) over a
**remote FastMCP 3.2 server** using the streamable-HTTP transport. Any MCP client —
the bundled Python client, MCP Inspector, Claude Code, ADK, etc. — can discover and
fetch skills by URI (`skill://{name}/SKILL.md`, `skill://{name}/_manifest`, and
supporting files). The client can also sync the full catalog to disk and use skills
offline.

## Repo layout (annotated)

```
pyproject.toml                     Build config; depends only on fastmcp>=3.2
README.md                          Human-facing setup + usage
TESTING.md                         End-to-end test walkthrough (client, offline, Inspector)
CLAUDE.md                          This file (agent-facing)
.gitignore                         Ignores .claude/, reference/, cache/, *.egg-info/, etc.

server/
  main.py                          FastMCP("SkillHub") — SkillsDirectoryProvider + 2
                                   custom @mcp.tool functions + /health route
                                   Env vars: SKILLHUB_HOST, SKILLHUB_PORT, SKILLHUB_RELOAD

client/
  test_client.py                   Exercises 8 scenarios: list_skills, list_resources,
                                   read SKILL.md, read _manifest, search_skills,
                                   get_skill_metadata, download_skill, sync_skills
  offline_demo.py                  Syncs to ./cache/skills/, then reads from disk only.
                                   Use --offline to skip sync (server-down scenario).

skills/
  code-review/                     Simple skill — SKILL.md only (L1+L2 disclosure)
  project-scaffolding/             Complex skill — SKILL.md + scripts/ + references/ +
                                   assets/ (L3 disclosure)

.agents/skills/                    Optional cross-agent standard root. Scanned only if
                                   present. Empty by default in this repo.

cache/skills/                      Runtime-generated, gitignored. Populated by
                                   offline_demo.py.

scratchpad/
  01_cc_initial_build/             Original design + plan + task list for the PoC
  02_cc_review/                    Second-pass review: validation, offline demo,
                                   inspector evidence, CLAUDE.md
```

## How to run things

```bash
# Install (editable)
pip install -e .

# Start the server (dev defaults)
python -m server.main

# Start the server in production-ish mode
SKILLHUB_HOST=127.0.0.1 SKILLHUB_RELOAD=0 python -m server.main

# Exercise all 8 tests (needs server up)
python client/test_client.py

# Sync skills to cache and read them back
python client/offline_demo.py

# Read from cache only (server can be down)
python client/offline_demo.py --offline

# MCP Inspector
npx @modelcontextprotocol/inspector
# → Streamable HTTP → http://localhost:8000/mcp
```

## Key technical facts to know

- Resource URIs:
  - `skill://{name}/SKILL.md` — main instruction file
  - `skill://{name}/_manifest` — synthetic manifest (files, sizes, SHA-256)
  - `skill://{name}/<supporting-file>` — individual supporting files (we use
    `supporting_files="resources"` mode; `"template"` would hide these)
- `SkillsDirectoryProvider` takes a list of `roots` with first-match precedence.
- `reload=True` (our default via `SKILLHUB_RELOAD=1`) re-scans on every request.
  FastMCP docs recommend disabling in production.
- `CallToolResult.content[0].text` is the return type of `client.call_tool(...)` in
  FastMCP 3.2 — not a list.
- Frontmatter parsing uses `yaml.safe_load` (PyYAML is a transitive dep of fastmcp).
- `compatibility` is a **top-level** frontmatter field per the agentskills.io spec,
  not nested under `metadata`.

## Security posture

- **No authentication.** This is a PoC.
- Default bind is `0.0.0.0`. For local-only use, set `SKILLHUB_HOST=127.0.0.1`.
- Do not expose this server on the public internet as-is.

## Where to read more

- `TESTING.md` — end-to-end test walkthrough for Python client, offline demo, and
  MCP Inspector, with expected outputs.
- `scratchpad/01_cc_initial_build/` — initial design, requirements, task list, and
  implementation notes. Start with `plan.md`.
- `scratchpad/02_cc_review/` — validation against FastMCP 3.2 docs and agentskills.io
  spec, plus the offline-workflow and Inspector evidence. Start with `plan.md`.
- `README.md` — human quick-start and config reference.
