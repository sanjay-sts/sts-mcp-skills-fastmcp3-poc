# Requirements — FastMCP3 Remote Skill Provider PoC

## Functional Requirements

1. **Skill Serving**: Serve Agent Skills (SKILL.md + supporting files) over MCP protocol
2. **Simple Skill**: At least one skill with SKILL.md only (Level 1+2 disclosure)
3. **Complex Skill**: At least one skill with scripts/, references/, assets/ (Level 3 disclosure)
4. **Remote Transport**: Server accessible via streamable HTTP (not just stdio)
5. **Skill Discovery**: Clients can list all available skills via `skill://` resource URIs
6. **Skill Manifests**: Clients can read `skill://{name}/_manifest` for file listings with sizes/hashes
7. **Skill Download**: Clients can download individual skills or sync all skills
8. **Search Tool**: MCP tool to search skills by keyword across names/descriptions
9. **Metadata Tool**: MCP tool to get detailed metadata for a specific skill
10. **Health Endpoint**: HTTP GET `/health` returns server status

## Non-Functional Requirements

1. **No Authentication**: No auth required — pure capability testing
2. **Hot Reload**: Server re-scans skills directory on each request (dev mode)
3. **MCP Inspector Compatible**: Testable via `npx @modelcontextprotocol/inspector`
4. **Python Client Compatible**: Testable via FastMCP Client + utilities
5. **Cross-Agent Skill Format**: Skills use universal Agent Skills frontmatter fields
