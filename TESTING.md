# Testing Guide

How to exercise SkillHub with (1) the bundled Python MCP client, (2) the offline
demo, and (3) MCP Inspector.

Captured transcripts for each scenario live in
[`scratchpad/02_cc_review/`](scratchpad/02_cc_review/) and can be diffed against
your own runs.

---

## 0. Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (one-time install: see the uv docs)

```bash
uv sync
uv run python -c "import fastmcp; print(fastmcp.__version__)"   # should be 3.2.x or newer
```

`uv sync` creates `.venv/` (gitignored) and installs everything pinned in `uv.lock`.
Every subsequent command uses `uv run` so it picks up that environment without
requiring you to activate it. No auth is required in any of the scenarios below.

---

## 1. Start the server

```bash
uv run python -m server.main
```

Expected startup output:

```
Starting SkillHub on 0.0.0.0:10001
Skills roots: ['.../skills']
Reload mode:  True (set SKILLHUB_RELOAD=0 for production)
MCP endpoint: http://0.0.0.0:10001/skillmcp
Health check:  http://0.0.0.0:10001/health
```

Sanity check from another terminal:

```bash
curl http://localhost:10001/health
# {"status":"healthy","skills_count":2,"skills":["code-review","project-scaffolding"]}
```

Alternative (production-style):

```bash
SKILLHUB_HOST=127.0.0.1 SKILLHUB_RELOAD=0 uv run python -m server.main
```

The startup banner will now print `Reload mode:  False` and the endpoint becomes
`http://127.0.0.1:10001/skillmcp`. Use this host/port in the client and Inspector steps
below if you run this way.

---

## 2. Python MCP client — full regression

In a second terminal, with the server up:

```bash
uv run python client/test_client.py
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
uv run python client/offline_demo.py
```

Expected:

- Phase 1 syncs two skills into `./cache/skills/` (which is gitignored).
- Phase 2 reads each `SKILL.md` straight off disk and prints a preview.

Reference:
[`scratchpad/02_cc_review/offline_demo_online_transcript.txt`](scratchpad/02_cc_review/offline_demo_online_transcript.txt).

```bash
# Step B — stop the server (Ctrl+C in terminal 1)

# Step C — re-run the demo with --offline; it never touches the network
uv run python client/offline_demo.py --offline
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
3. **URL:** `http://localhost:10001/skillmcp` (or `http://127.0.0.1:10001/skillmcp` if you
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

## 5. Consumer demo — pull a single skill end to end

`client/consumer_demo.py` plays the role of a downstream consumer (an agent
framework, a custom tool, a test harness) that wants **one** complete skill.
It uses the canonical helpers from `fastmcp.utilities.skills` — `list_skills`,
`get_skill_manifest`, and `download_skill` — documented at
<https://gofastmcp.com/servers/providers/skills>. No hand-rolled protocol code.
It does not call an LLM; the goal is to prove the MCP pull contract.

```bash
# Pick the default (code-review): print L1 + manifest + L2 over MCP
uv run python client/consumer_demo.py

# Same for a different skill
uv run python client/consumer_demo.py --skill project-scaffolding

# Also materialise everything (L2 + L3) to ./cache/consumed/<skill>/
uv run python client/consumer_demo.py --skill project-scaffolding --save
```

### Running the consumer demo from any folder (no project needed)

The script has a PEP 723 inline-metadata header, so `uv run` will provision an
ephemeral venv with `fastmcp` on first call. Copy or point `uv run` at the
file from any directory — no `pyproject.toml`, no `uv sync`, no install:

```bash
# Outside the repo:
cd /any/other/folder
uv run /path/to/sts-mcp-skills-fastmcp3-poc/client/consumer_demo.py --skill code-review

# Point at a server on a different host/port without editing the file:
uv run /path/to/consumer_demo.py --server http://host:10001/skillmcp --skill code-review

# Materialise downloaded skills somewhere specific:
uv run /path/to/consumer_demo.py --save --cache ~/my-skills --skill project-scaffolding
```

With `--save` and no `--cache`, the default is `./cache/consumed/` **relative
to the current working directory** — so running from another folder keeps the
output in that folder, never in this repo.

Env overrides: `SKILLHUB_URL`, `SKILLHUB_CACHE`.

### Downloading into a vendor directory

FastMCP's vendor providers (documented at
<https://gofastmcp.com/servers/providers/skills#vendor-providers>) are a
**server-side** concept — subclasses of `SkillsDirectoryProvider` that pre-wire
`roots=` to e.g. `~/.claude/skills/` so the server reads that directory.

They do **not** control where a client writes downloaded skills. `download_skill`
writes to whatever path you pass. But if you *want* the downloaded skill to be
immediately picked up by, say, Claude Code (which reads `~/.claude/skills/`),
you can point `--cache` at that directory — the spec's own client example
does this:

```python
await download_skill(client, "pdf-processing", Path.home() / ".claude" / "skills")
```

For convenience, the demo ships a `--vendor` shortcut that expands to the
canonical path for each of the vendor providers listed on that docs page:

```bash
uv run consumer_demo.py --skill code-review --save --vendor claude
# → writes into ~/.claude/skills/code-review/

uv run consumer_demo.py --skill code-review --save --vendor cursor
# → writes into ~/.cursor/skills/code-review/
```

Supported values: `claude`, `cursor`, `copilot`, `codex`, `gemini`, `goose`,
`opencode`. If you also pass `--cache`, `--cache` wins. `--vendor` never writes
anywhere you didn't name — it's purely a shortcut for the `~/.<vendor>/skills`
path expansion.

What it proves:

- **L1 discovery** — `list_skills(client)` returns `SkillSummary(name,
  description, uri)` for every skill on the server. The description shown is
  what an agent would see at discovery time (now resolved correctly after the
  single-line YAML fix).
- **Manifest** — `get_skill_manifest(client, skill_name)` returns
  `SkillManifest(name, files=[SkillFile(path, size, hash), ...])`. SHA-256 hashes
  are included for integrity checking.
- **L2 read** — without `--save`, the demo reads `skill://<name>/SKILL.md`
  directly over MCP and prints the body. This is what an agent loads when it
  decides to apply the skill.
- **L2 + L3 materialisation** — with `--save`, `download_skill(client, name,
  target)` writes every file to disk, handling both `TextResourceContents`
  (SKILL.md, markdown, Python) and `BlobResourceContents` (JSON and other
  non-text MIMEs, base64-decoded internally by the utility).

Reference transcripts:
- [`scratchpad/02_cc_review/consumer_demo_code-review_transcript.txt`](scratchpad/02_cc_review/consumer_demo_code-review_transcript.txt)
- [`scratchpad/02_cc_review/consumer_demo_project-scaffolding_transcript.txt`](scratchpad/02_cc_review/consumer_demo_project-scaffolding_transcript.txt)

---

## 6. Use SkillHub from Claude Code in another folder

This scenario proves Claude Code running in an unrelated project can consume
skills from SkillHub over MCP without that project owning any of the code.

### 6.1 Keep the SkillHub server running

In *this* repo, start the server as in step 1:

```bash
uv run python -m server.main
```

Leave it running; `http://localhost:10001/skillmcp` is your MCP endpoint.

### 6.2 In the consumer project, add `.mcp.json` at its repo root

Pick any folder outside this repo (say `C:\path\to\some-other-project\`). Create
a `.mcp.json` in its root:

```json
{
  "mcpServers": {
    "skillhub": {
      "type": "http",
      "url": "http://localhost:10001/skillmcp"
    }
  }
}
```

Equivalent CLI, from inside that folder:

```bash
claude mcp add --transport http --scope project skillhub http://localhost:10001/skillmcp
```

Scope options:

| Scope | File | Shared with the team? |
|---|---|---|
| `local` (default) | `~/.claude.json` | No — this machine, this user only |
| `project` | `.mcp.json` at repo root | Yes — commit it |
| `user` | `~/.claude.json` | No, but applies across all your projects |

### 6.3 Launch Claude Code inside that folder

```bash
cd C:\path\to\some-other-project
claude
```

On the first use of a project-scoped server Claude Code prompts for workspace
trust before connecting. Approve once.

### 6.4 Verify inside the Claude Code session

```
/mcp
```

You should see `skillhub` listed with status `connected`, exposing:

- 7 resources under the `skill://` URI scheme
- 2 tools: `search_skills`, `get_skill_metadata`

From a terminal:

```bash
claude mcp list              # all registered servers
claude mcp get skillhub      # details for this one
```

### 6.5 Drive it from the chat

Sample prompts that exercise the remote skill:

- *"List the skills available from the skillhub MCP server."* → triggers `list_resources` and/or `search_skills`.
- *"Read `skill://code-review/SKILL.md` and use it to review this diff: …"* → forces Claude Code to pull the SKILL.md content from SkillHub and apply it.
- *"Fetch the project-scaffolding skill and tell me what templates it ships."* → triggers reads of `_manifest` and `assets/project-template.json`.

If any of these fail, revisit section 5 (the consumer_demo) — if that works
but Claude Code doesn't, the issue is the `.mcp.json` or the trust prompt,
not the server.

---

## 7. Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ConnectionRefusedError` in the client | Server not running | Run `uv run python -m server.main` |
| `uv: command not found` | uv not installed | Install per <https://docs.astral.sh/uv/> |
| `uv sync` fails on first run | Stale or missing `uv.lock` | `uv lock` then `uv sync` |
| Inspector can't connect | Wrong URL or transport | Use **Streamable HTTP** + `/skillmcp` path on port `10001` |
| `curl /health` hangs | Server still starting | Retry after 1–2 s |
| `UnicodeEncodeError` on Windows | Ancient cp1252 console | Use a modern terminal, or `set PYTHONIOENCODING=utf-8` |
| `FileExistsError` from `sync_skills` | Re-sync without overwrite | Already handled — `offline_demo.py` passes `overwrite=True` |
| `offline_demo --offline` reports empty cache | Never ran the sync phase | Run it once with the server up first |
| `consumer_demo` doesn't find the skill | Typo in `--skill` name | It prints the available skill names; copy one from the L1 list |
| `claude mcp list` doesn't show `skillhub` | Wrong folder or wrong scope | Run from the folder that holds `.mcp.json`; or use `--scope user` when adding |
| Claude Code can't reach SkillHub | Server bound to `127.0.0.1` but Claude in another context | Start server with `SKILLHUB_HOST=0.0.0.0` (default) |

---

## 8. What the test surface covers

- **Remote hosting** — every call in steps 2, 3-A, 4, 5, and 6 crosses the
  streamable-HTTP boundary at `http://…:10001/skillmcp`. Nothing reads skill
  files from the client's filesystem during those scenarios.
- **Offline queryability** — step 3-B reads only from `./cache/skills/`; the
  server is stopped.
- **Single-skill pull** — step 5 (`consumer_demo`) proves one complete skill
  (SKILL.md + manifest + all supporting files) can be pulled over MCP, handling
  both text and blob MIME types.
- **Third-party client consumption** — step 6 proves Claude Code in an
  unrelated folder can register SkillHub via `.mcp.json` and use the skills
  remotely, validating end-to-end MCP compatibility beyond our own client.
- **Config** — the production-style variant in step 1 proves
  `SKILLHUB_RELOAD=0` cleanly disables reload mode (per FastMCP docs).
- **MCP protocol conformance** — steps 4 and 6 use unmodified MCP clients
  (Inspector, Claude Code); any other MCP-compliant client can connect the
  same way.
