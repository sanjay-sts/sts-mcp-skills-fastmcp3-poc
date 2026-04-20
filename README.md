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

See [`TESTING.md`](TESTING.md) for the full end-to-end walkthrough covering the
Python client, the offline demo, and MCP Inspector, plus expected outputs.

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

## Configuration

The server reads three environment variables:

| Variable | Default | Meaning |
|----------|---------|---------|
| `SKILLHUB_HOST` | `0.0.0.0` | Bind interface. Set to `127.0.0.1` to restrict to localhost. |
| `SKILLHUB_PORT` | `8000` | TCP port for the HTTP server. |
| `SKILLHUB_RELOAD` | `1` | `1` = rescan skills dir on every request (dev). Set `0` in production — per FastMCP docs, reload mode adds per-request overhead. |

Example production-style start:

```bash
SKILLHUB_HOST=127.0.0.1 SKILLHUB_RELOAD=0 python -m server.main
```

> **Security note:** the default `0.0.0.0` binds on all interfaces and there is no
> authentication. For anything beyond local PoC use, bind to `127.0.0.1` or put the
> server behind an authenticating reverse proxy.

## Offline Workflow

The test client and demo script prove two distinct capabilities:

- **`client/test_client.py`** — live RPC verification (8 scenarios).
- **`client/offline_demo.py`** — persistent-cache sync + disconnect-and-read-locally.

End-to-end offline flow:

```bash
# 1) Start the server
python -m server.main

# 2) In another terminal: sync skills to ./cache/skills/, then read them back from disk
python client/offline_demo.py

# 3) Stop the server (Ctrl+C in the first terminal)

# 4) Re-run the demo with --offline — it reads the cache without any network call
python client/offline_demo.py --offline
```

What this proves: after a single sync, the synced skills are usable locally and
survive the server going down. `./cache/skills/` is gitignored.

## Verified via MCP Inspector

A transcript of an MCP Inspector session against this server (Streamable HTTP,
`http://localhost:8000/mcp`) is at
[`scratchpad/02_cc_review/inspector_evidence.md`](scratchpad/02_cc_review/inspector_evidence.md).
It captures the resources list (7 `skill://` URIs), the tool list (`search_skills`,
`get_skill_metadata`), one resource read, and one tool call.
