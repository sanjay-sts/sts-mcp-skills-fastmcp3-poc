# Requirements — Second-Pass Review

## Goal

Validate the initial build (commit `a5b5536`) against FastMCP 3.2 official docs and the
agentskills.io spec, and close gaps around the two original objectives: **remote skill
hosting** and **offline queryability**.

## Functional Requirements

1. **Configurable reload** — server `reload` behavior is controlled by env var
   (`SKILLHUB_RELOAD`), default dev (`1`), production disabling documented.
2. **Persistent offline cache** — skills synced from the server land in a stable
   `./cache/skills/` directory on disk and remain usable after disconnect.
3. **Offline-only mode** — client demo can run with `--offline` and succeed purely
   from the local cache without any network call.
4. **Remote-hosting evidence** — MCP Inspector session captured in a text transcript
   showing resource discovery, tool invocation, and resource read against
   `http://localhost:8000/mcp`.
5. **Agent-facing docs** — `CLAUDE.md` at repo root + README sections for offline
   workflow, Inspector verification, and environment configuration.
6. **Hygiene** — `.gitignore` covers working-directory artifacts (`.claude/`,
   `reference/`, `cache/`).

## Non-Functional Requirements

1. **No regressions** — existing `client/test_client.py` continues to pass all 8
   sections with the new config defaults.
2. **No auth** — same stance as initial build.
3. **No new runtime deps** — use only `fastmcp` and its transitive packages
   (PyYAML already covered).
4. **No core rewiring** — provider construction, tools, and resources remain as in
   `a5b5536`; the review is additive.

## Out of Scope

- Authentication / authorization.
- Alternative transports (SSE, stdio).
- Hash-aware incremental sync (deferred P4 in the plan).
- `dependencies` frontmatter / tags-as-list spec tweaks (deferred P5).
- Integration into Claude Code, Cursor, or ADK beyond standards-compliant on-disk format.
