# Testing Guide

How to exercise SkillHub with (1) the bundled Python MCP client, (2) the offline
demo, and (3) MCP Inspector.

Captured transcripts for each scenario live in
[`scratchpad/02_cc_review/`](scratchpad/02_cc_review/) and can be diffed against
your own runs.

---

## 0. Prerequisites

```bash
pip install -e .
python -c "import fastmcp; print(fastmcp.__version__)"   # should be 3.2.x or newer
```

No auth is required in any of the scenarios below. Python 3.10+.

---

## 1. Start the server

```bash
python -m server.main
```

Expected startup output:

```
Starting SkillHub on 0.0.0.0:8000
Skills roots: ['.../skills']
Reload mode:  True (set SKILLHUB_RELOAD=0 for production)
MCP endpoint: http://localhost:8000/mcp
Health check:  http://localhost:8000/health
```

Sanity check from another terminal:

```bash
curl http://localhost:8000/health
# {"status":"healthy","skills_count":2,"skills":["code-review","project-scaffolding"]}
```

Alternative (production-style):

```bash
SKILLHUB_HOST=127.0.0.1 SKILLHUB_RELOAD=0 python -m server.main
```

The startup banner will now print `Reload mode:  False` and the endpoint becomes
`http://127.0.0.1:8000/mcp`. Use this host/port in the client and Inspector steps
below if you run this way.

---

## 2. Python MCP client — full regression

In a second terminal, with the server up:

```bash
python client/test_client.py
```

Expected: eight sections printed, ending with `ALL TESTS PASSED`.

| # | Section | What it proves |
|---|---|---|
| 1 | `list_skills` | 2 skills discovered (`code-review`, `project-scaffolding`) |
| 2 | `list_resources` | 7 `skill://` URIs exposed |
| 3 | Read `skill://code-review/SKILL.md` | 1,626 chars of SKILL.md returned |
| 4 | Read `skill://project-scaffolding/_manifest` | JSON with 4 files + sizes |
| 5 | `search_skills` tool | returns matches for `review` and `scaffold` |
| 6 | `get_skill_metadata` tool | full metadata: 4 files, 8,394 bytes total |
| 7 | `download_skill` | code-review downloaded to temp dir |
| 8 | `sync_skills` | all skills downloaded to temp dir |

Full reference transcript:
[`scratchpad/02_cc_review/test_client_transcript.txt`](scratchpad/02_cc_review/test_client_transcript.txt).

---

## 3. Offline workflow — sync then read without the server

This proves the **queryable-offline** capability: skills are usable locally after
one sync, even when the server is down.

```bash
# Step A — with the server still running, sync + read from disk
python client/offline_demo.py
```

Expected:

- Phase 1 syncs two skills into `./cache/skills/` (which is gitignored).
- Phase 2 reads each `SKILL.md` straight off disk and prints a preview.

Reference:
[`scratchpad/02_cc_review/offline_demo_online_transcript.txt`](scratchpad/02_cc_review/offline_demo_online_transcript.txt).

```bash
# Step B — stop the server (Ctrl+C in terminal 1)

# Step C — re-run the demo with --offline; it never touches the network
python client/offline_demo.py --offline
```

Expected: Phase 1 is skipped; Phase 2 reads the local cache and prints the same
SKILL.md previews. If the cache is empty the script tells you to run without
`--offline` first.

Reference:
[`scratchpad/02_cc_review/offline_demo_offline_transcript.txt`](scratchpad/02_cc_review/offline_demo_offline_transcript.txt).

---

## 4. MCP Inspector (browser UI)

Start the server (step 1) if it is not already up, then:

```bash
npx @modelcontextprotocol/inspector
```

1. Open <http://localhost:6274>.
2. **Transport:** `Streamable HTTP`.
3. **URL:** `http://localhost:8000/mcp` (or `http://127.0.0.1:8000/mcp` if you
   used the production-style start).
4. Click **Connect**.

### Resources panel — should list 7 entries

- `skill://code-review/SKILL.md`
- `skill://code-review/_manifest`
- `skill://project-scaffolding/SKILL.md`
- `skill://project-scaffolding/_manifest`
- `skill://project-scaffolding/assets/project-template.json`
- `skill://project-scaffolding/references/templates-guide.md`
- `skill://project-scaffolding/scripts/scaffold.py`

Click any entry to read it.

- `skill://code-review/SKILL.md` → YAML frontmatter + markdown (~1,626 chars).
- `skill://project-scaffolding/_manifest` → JSON listing of 4 files with sizes
  and SHA-256 hashes.

### Tools panel — should list 2 tools

| Tool | Call with | Expect |
|---|---|---|
| `search_skills` | `{"query": "review"}` | JSON array with `code-review` |
| `search_skills` | `{"query": "scaffold"}` | JSON array with `project-scaffolding` |
| `get_skill_metadata` | `{"skill_name": "project-scaffolding"}` | frontmatter + 4 files + `total_size: 8394` |

Full reference transcript and step-by-step walkthrough:
[`scratchpad/02_cc_review/inspector_evidence.md`](scratchpad/02_cc_review/inspector_evidence.md).

---

## 5. Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ConnectionRefusedError` in the client | Server not running | Run `python -m server.main` |
| Inspector can't connect | Wrong URL or transport | Use **Streamable HTTP** + `/mcp` path |
| `curl /health` hangs | Server still starting | Retry after 1–2 s |
| `UnicodeEncodeError` on Windows | Ancient cp1252 console | Use a modern terminal, or `set PYTHONIOENCODING=utf-8` |
| `FileExistsError` from `sync_skills` | Re-sync without overwrite | Already handled — `offline_demo.py` passes `overwrite=True` |
| `offline_demo --offline` reports empty cache | Never ran the sync phase | Run it once with the server up first |

---

## 6. What the test surface covers

- **Remote hosting** — every call in steps 2, 3-A, and 4 crosses the
  streamable-HTTP boundary at `http://…/mcp`. Nothing reads skill files from
  the client's filesystem during those scenarios.
- **Offline queryability** — step 3-B reads only from `./cache/skills/`; the
  server is stopped.
- **Config** — the production-style variant in step 1 proves
  `SKILLHUB_RELOAD=0` cleanly disables reload mode (per FastMCP docs).
- **MCP protocol conformance** — step 4 uses the standard MCP Inspector with
  no project-specific adapter; any other MCP-compliant client can connect
  the same way.
