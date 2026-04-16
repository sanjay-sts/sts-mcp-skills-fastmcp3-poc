# Project Templates Guide

## Available Templates

### python-package
A standard Python package with pyproject.toml, src layout, and tests.
**Use when:** Creating reusable Python libraries, CLI tools, or utilities.
**Includes:** pyproject.toml, src/ layout, tests/, README.md, .gitignore

### fastapi-service
A FastAPI web service with routes, models, and Docker support.
**Use when:** Building REST APIs, microservices, or web backends.
**Includes:** main.py, routes/, models/, Dockerfile, requirements.txt, tests/

### mcp-server
A FastMCP3 server with tool and resource examples.
**Use when:** Building MCP servers for AI agent integration.
**Includes:** server.py, tools/, resources/, pyproject.toml, README.md

## Choosing a Template

| Need | Template | Why |
|------|----------|-----|
| Library/CLI tool | python-package | Standard packaging, src layout |
| REST API | fastapi-service | Production-ready FastAPI scaffold |
| AI agent tools | mcp-server | FastMCP3 with examples |
