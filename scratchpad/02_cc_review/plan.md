# Review & Verification — FastMCP3 Remote Skill Provider PoC

## Context

The PoC is committed as `a5b5536` on branch `#10_local_build`. This plan is a **second-pass review** using FastMCP 3.2 official docs (via context7), agentskills.io spec, and live audit, to validate what exists and propose gap-closing work for the two stated goals: **remote hosting** and **offline queryability**.

---

## Verified Correct (evidence-backed)

| Area | Our code | Spec/docs reference | Status |
|---|---|---|---|
| Manifest URI | `skill://{name}/_manifest` in `client/test_client.py:53` | context7: `prefecthq/fastmcp` docs confirm `skill://{name}/_manifest` | ✅ Correct (earlier research that said `manifest.json` was wrong) |
| Provider multi-root | `roots=[SKILLS_DIR, AGENTS_SKILLS_DIR]` in `server/main.py:36-42` | FastMCP docs show `roots=[...]` with first-match precedence | ✅ Correct |
| Supporting files mode | `supporting_files="resources"` | docs: `"resources"` exposes every file via `list_resources()`; `"template"` hides them | ✅ Correct choice for PoC (full enumeration) |
| `reload=True` | `server/main.py:41` | docs: OK for dev, adds per-request overhead, disable in prod | ⚠️ Dev-only; should be env-configurable |
| Client utilities | `list_skills`, `download_skill`, `sync_skills` from `fastmcp.utilities.skills` | docs: these are the canonical helpers over `list_resources`/`read_resource` | ✅ Correct |
| `CallToolResult` handling | `result.content[0].text` in `client/test_client.py:65,70,78` | FastMCP 3.2 returns `CallToolResult`, not list | ✅ Correct (fixed during build) |
| YAML frontmatter parse | `yaml.safe_load` in `server/main.py:71` | PyYAML is a transitive dep; handles folded scalars + nested maps | ✅ Correct |
| Frontmatter fields | `name`, `description`, `compatibility`, `metadata` | agentskills.io spec: name lowercase+hyphens ≤64, description ≤1024, `compatibility` is top-level | ✅ Correct |
| Progressive disclosure | L1 frontmatter → L2 `SKILL.md` body → L3 `references/`, `scripts/`, `assets/` | agentskills.io 3-level pattern | ✅ Correct |
| Custom tools | `search_skills`, `get_skill_metadata` via `@mcp.tool` | additive; don't conflict with provider resources | ✅ Correct |
| Health endpoint | `GET /health` via `@mcp.custom_route` | FastMCP supports custom routes alongside `/mcp` | ✅ Correct |
| MCP Inspector URL | README says `http://localhost:8000/mcp` | FastMCP docs confirm `/mcp` path is required on streamable-http | ✅ Correct |

---

## Gaps & Findings

### A. Hygiene (small, low-risk)

- **`reference/` dir** (70KB HTML builder guide) is untracked and not in `.gitignore`. Clutters `git status`. Choices: add to `.gitignore`, or commit it if intended for repo.
- **`.claude/`** untracked; typical to gitignore.
- **`sts_mcp_skills_fastmcp3_poc.egg-info/`** exists on disk; `.gitignore` already covers `*.egg-info/`, so it's not committed — no action needed but can be deleted locally.
- **`scratchpad/01_cc_initial_build/task-list.md` Task 14** shows `[ ]` but commit `a5b5536` exists — cosmetic drift.

### B. Configurability (correctness of production posture)

- **`reload=True` hardcoded** in `server/main.py:41`. FastMCP docs explicitly say "disable in production." Should be driven by env var (e.g., `SKILLHUB_RELOAD=1`).
- **`HOST` defaults to `0.0.0.0`**. Fine for PoC, but README doesn't warn that this exposes the server on all interfaces.

### C. Offline queryability — the main unproven story

This is the user's explicit goal, and it is **not demonstrated end-to-end**.

- `test_sync_skills` (`client/test_client.py:98-106`) writes to `tempfile.TemporaryDirectory()` and throws it away. It proves sync works as an RPC call, but not that skills are usable offline.
- No persistent sync directory, no "disconnect then read locally" demo, no docs on how a downstream agent (Claude Code, Cursor, ADK) consumes the synced dir.
- **The `_manifest` resource exposes SHA-256 hashes per file** (confirmed in FastMCP docs and examples/skills README), but `sync_skills()` utility does full overwrite — no hash-based skip. For real "sync" semantics over remote HTTP, that matters.

### D. Remote hosting — mostly proven, a few missing proofs

- ✅ Streamable HTTP works, 8 client tests pass (per `implementation.md`).
- ⚠️ **MCP Inspector not actually run** — README has instructions, but no captured output/screenshot proving Inspector can discover `skill://` resources over the remote endpoint.
- ⚠️ Server **is not currently running** at audit time (port 8000 free). Tests haven't been re-run post-commit.

### E. agentskills.io spec alignment (nice-to-have)

- **No `dependencies` field** in either SKILL.md. The spec allows declaring MCP server deps (`type: "mcp", transport: "streamable_http", url: ...`) — would be a neat self-reference: our own skills could declare our own server.
- **`metadata.tags` as comma-separated string** rather than YAML list. Works, but list form is more standard.

---

## Selected Scope

User chose **P1 + P2 + P3 + commit (no push)**. P4 (hash sync) and P5 (spec alignment) are deferred.
`reference/` will be added to `.gitignore` (kept local, never committed).

### P1 — Correctness & Hygiene

- [ ] **P1.1** `.gitignore`: add `.claude/`, `reference/`, and `cache/` (the last anticipates P2.1).
- [ ] **P1.2** `server/main.py`: make `reload` env-driven via `SKILLHUB_RELOAD` (default `1` for dev, `0` for prod). Update startup print to show the effective mode.
- [ ] **P1.3** `scratchpad/01_cc_initial_build/task-list.md`: mark Task 14 complete.
- [ ] **P1.4** Start server, run `client/test_client.py`, save transcript to `scratchpad/02_cc_review/test_client_transcript.txt`.

### P2 — Prove the offline story

- [ ] **P2.1** Add `client/offline_demo.py`:
  1. `sync_skills(client, Path("./cache/skills"), overwrite=True)` → persistent cache
  2. Print what was synced, disconnect
  3. Re-open cached files from disk only (no client) and print first 200 chars of each `SKILL.md`
  4. Accept a `--offline` flag that skips the sync phase and goes straight to reading the cache — this is how to run it when the server is down
- [ ] **P2.2** Extend README with **Offline Workflow** section walking through: start server → `offline_demo.py` (sync+read) → stop server → `offline_demo.py --offline` (read-only).

### P3 — Prove the remote story (MCP Inspector)

- [ ] **P3.1** With server running, launch `npx @modelcontextprotocol/inspector`, connect to `http://localhost:8000/mcp`, and capture:
  - Resources list (should show 7 `skill://` URIs)
  - Tools list (should include `search_skills`, `get_skill_metadata`)
  - One resource read (e.g., `skill://code-review/SKILL.md`)
  - One tool call (e.g., `search_skills` with query `review`)
  Save as `scratchpad/02_cc_review/inspector_evidence.md` (text summary; screenshots optional if the user wants to add them).
- [ ] **P3.2** Append a short "MCP Inspector Verified" note + link to evidence file in README.

### P-DOCS — Refresh all docs (user-requested)

- [ ] **D1** `scratchpad/01_cc_initial_build/task-list.md`: mark Task 14 complete (P1.3) and add a footnote pointing to `02_cc_review/` follow-up.
- [ ] **D2** `scratchpad/01_cc_initial_build/implementation.md`: append a "Post-build review (02_cc_review)" section summarizing what the review added (env-driven reload, offline demo, inspector evidence) and linking to the new folder.
- [ ] **D3** `scratchpad/01_cc_initial_build/design.md` and `requirements.md`: append a short "Superseded / extended by 02_cc_review" note at the top so future readers know to also read the review docs. No content rewrite.
- [ ] **D4** `scratchpad/01_cc_initial_build/plan.md`: append a similar "Status: complete — see 02_cc_review for follow-up" note.
- [ ] **D5** Create `scratchpad/02_cc_review/` with:
  - `plan.md` — copy of this plan file
  - `requirements.md` — the review's goals (verify remote hosting, prove offline workflow, inspector evidence)
  - `design.md` — how offline_demo.py works, env-driven reload, evidence format
  - `task-list.md` — checklist mirroring P1/P2/P3/D/COMMIT
  - `implementation.md` — deviations log (filled as tasks run)
  - `test_client_transcript.txt` — output of P1.4
  - `inspector_evidence.md` — output of P3.1
- [ ] **D6** `README.md` — add three sections:
  - **Offline Workflow** (P2.2) with commands and a what-it-proves paragraph
  - **Verified via MCP Inspector** (P3.2) with a brief summary linking to the evidence file
  - **Configuration** subsection documenting `SKILLHUB_RELOAD`, `SKILLHUB_HOST`, `SKILLHUB_PORT`
- [ ] **D7** Create `CLAUDE.md` at repo root (does not currently exist). Contents:
  - Short project overview (1 para)
  - Repo layout (same tree as README but annotated for an agent)
  - How to run server + tests + offline demo
  - Pointer to `scratchpad/01_cc_initial_build/` and `scratchpad/02_cc_review/` for full design/decision history
  - Explicit "No auth; bind to 127.0.0.1 for local-only" note

### Commit

- [ ] **C1** Stage only the intended files (`.gitignore`, `server/main.py`, `client/offline_demo.py`, `README.md`, `CLAUDE.md`, `scratchpad/**`). Do not stage `reference/` or `.claude/`.
- [ ] **C2** Single commit: `review: validate remote+offline skill hosting, add offline demo, CLAUDE.md, inspector evidence`. **Do not push without explicit user go-ahead.**

---

## Critical Files (to be modified or created)

**Code / config**
- `server/main.py` — env-driven reload (P1.2)
- `.gitignore` — add `.claude/`, `reference/`, `cache/` (P1.1)
- `client/offline_demo.py` — **new** (P2.1)

**Docs (all refreshed per user request)**
- `README.md` — offline workflow, inspector summary, config section (D6)
- `CLAUDE.md` — **new** at repo root (D7)
- `scratchpad/01_cc_initial_build/{plan,requirements,design,task-list,implementation}.md` — minor appends / supersession notes (D1–D4)
- `scratchpad/02_cc_review/` — **new** folder with plan/requirements/design/task-list/implementation + evidence files (D5)

No changes needed to the core provider wiring — it already matches the docs exactly. Reuse existing utilities: `sync_skills` and `read_resource` from `fastmcp.utilities.skills` (already imported in `client/test_client.py:9`).

---

## Verification Plan

| Check | Command | Expected |
|---|---|---|
| Server boots with new config | `SKILLHUB_RELOAD=0 python -m server.main` | Prints roots, listens on :8000, prints `reload=False` |
| Existing tests still pass | `python client/test_client.py` | 8 sections, "ALL TESTS PASSED" |
| Offline demo works w/ server | `python client/offline_demo.py` | Syncs 2 skills to `./cache/skills/`, then reads them back from disk |
| Offline demo works w/o server | Stop server, `python client/offline_demo.py --offline` | Reads local cache successfully, never contacts server |
| Inspector proof | Launch inspector, connect to `/mcp`, list resources | 7 `skill://` resources visible; evidence file populated |
| Hygiene | `git status` | Only intended changes; `.claude/`, `reference/`, `cache/` ignored |

---

## Out of Scope

- Authentication (user said "no auth at this point").
- Alternative transports (SSE, stdio).
- Claude Code / Cursor / ADK integration beyond showing the on-disk format is standards-compliant.
- Performance / load testing.
