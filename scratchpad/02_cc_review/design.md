# Design — Second-Pass Review

## What actually changes (scope)

Only two source files are touched in the server + client code:

1. `server/main.py` — new `RELOAD` env flag, passed to `SkillsDirectoryProvider`
   and logged at startup.
2. `client/offline_demo.py` — **new** standalone script.

Everything else (provider wiring, tools, resources, URIs) is correct per context7 docs
and remains unchanged.

## Env-driven reload

FastMCP docs explicitly state `reload=True` "adds overhead to every request" and
should be disabled in production. Implementation:

```python
RELOAD = os.environ.get("SKILLHUB_RELOAD", "1") not in ("0", "false", "False", "")

mcp.add_provider(
    SkillsDirectoryProvider(
        roots=skill_roots,
        supporting_files="resources",
        reload=RELOAD,
    )
)
```

Default is `1` (dev-friendly). Startup print shows the effective value.

## Offline cache workflow

```
┌─────────────────┐        sync_skills         ┌────────────────────┐
│ SkillHub server │ ◄─────────────────────────│ offline_demo.py    │
│ :8000           │                            │ (Phase 1)          │
└─────────────────┘                            └─────────┬──────────┘
                                                         │ writes files
                                                         ▼
                                               ./cache/skills/
                                                 ├─ code-review/
                                                 └─ project-scaffolding/

       ┌────────────────────┐          read-only          ┌──────────────────┐
       │ offline_demo.py    │ ───────────────────────────▶│ ./cache/skills/  │
       │ --offline (Phase 2)│   (no Client, no network)   │                  │
       └────────────────────┘                             └──────────────────┘
```

### Demo script phases

1. **Phase 1 (sync)** — connects to `http://localhost:8000/mcp`, calls
   `sync_skills(client, Path("./cache/skills"), overwrite=True)`, closes the client.
2. **Phase 2 (offline read)** — walks `./cache/skills/`, reads each `SKILL.md`
   directly from disk, and prints a preview. No `Client`, no `asyncio` network.

With `--offline`, Phase 1 is skipped entirely, proving the cache is sufficient on its
own.

### Why this is the simplest thing that works

- `sync_skills()` already does the heavy lifting — we reuse the canonical utility
  rather than reinventing it.
- `./cache/skills/` is gitignored so the demo does not pollute the repo.
- A single `--offline` flag is enough to demonstrate the disconnect scenario; there's
  no need for a mock or a second server.

## MCP Inspector evidence format

`scratchpad/02_cc_review/inspector_evidence.md` is a plain-text record containing:

- the connection URL used (`http://localhost:8000/mcp`, Streamable HTTP)
- the full list of resources returned by the Inspector (should be 7 `skill://` URIs)
- the list of tools (`search_skills`, `get_skill_metadata`)
- one example resource read (e.g., `skill://code-review/SKILL.md`, first 300 chars)
- one example tool call (`search_skills` with `query=review`) and the raw response

Screenshots are optional — the text transcript is sufficient proof that the remote
endpoint serves skills correctly.

## CLAUDE.md positioning

`CLAUDE.md` is the AI-agent-facing README. Claude Code, Cursor, and similar clients
auto-load it on session start when present at the project root. Contents:

- one-paragraph project summary
- annotated repo tree
- commands to run server / tests / offline demo
- pointers to both scratchpad folders (`01_cc_initial_build/` and `02_cc_review/`)
- explicit security note: server binds to `0.0.0.0` by default with no auth; use
  `SKILLHUB_HOST=127.0.0.1` for local-only exposure.

## Verification matrix

Covered in the plan file; highlights:

| Scenario | Server up? | Command | Outcome |
|---|---|---|---|
| Baseline regression | yes | `python client/test_client.py` | 8/8 pass |
| Online demo | yes | `python client/offline_demo.py` | syncs + reads |
| Offline demo | no | `python client/offline_demo.py --offline` | reads cache only |
| Prod reload off | yes | `SKILLHUB_RELOAD=0 python -m server.main` | logs `Reload mode: False` |
