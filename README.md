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
