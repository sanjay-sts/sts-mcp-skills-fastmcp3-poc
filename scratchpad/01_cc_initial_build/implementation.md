# Implementation Notes — FastMCP3 Remote Skill Provider PoC

## Deviations from Original Plan

### 1. call_tool return type (Task 5)
FastMCP 3.2's `Client.call_tool()` returns a `CallToolResult` object, not a list.
- **Plan:** `result[0].text`
- **Fix:** `result.content[0].text`
- Applied consistently across all 3 `call_tool` sites in `client/test_client.py`.

### 2. pyproject.toml build system (Task 1)
Plan only had `[project]` section. Editable install (`pip install -e .`) failed without build-system config.
- **Fix:** Added `[build-system]` with setuptools and `[tool.setuptools.packages.find]`.

### 3. scaffold.py --list flag (Task 3)
Plan made `--template` and `--name` required via argparse, which prevented `--list` from working standalone.
- **Fix:** Made them optional with manual validation via `parser.error()` when not using `--list`.

## Post-Review Improvements

### 4. YAML frontmatter parser (Task 10)
Original custom regex parser couldn't handle nested YAML keys (`metadata:` sub-keys were concatenated into a flat string).
- **Fix:** Replaced with `yaml.safe_load()` (PyYAML, already a transitive dependency of fastmcp).
- Now correctly parses multi-line folded scalars (`>`), nested maps, and all YAML types.

### 5. agentskills.io spec alignment (Task 11)
`compatibility` was nested under `metadata` in `project-scaffolding/SKILL.md`. Per the agentskills.io specification, `compatibility` is a top-level frontmatter field.
- **Fix:** Moved to top-level: `compatibility: Requires Python 3.10+`

### 6. Cross-agent .agents/skills/ support (Task 12)
The agentskills.io open standard defines `.agents/skills/` as the cross-client interoperability directory (used by Codex, Gemini CLI, OpenCode, Roo Code, and others).
- **Fix:** Server now scans both `./skills/` (project-local) and `.agents/skills/` (cross-agent standard) if the latter exists.
- `SkillsDirectoryProvider` accepts a list of roots.

## Key Research Findings (ADK / agentskills.io)

- Agent Skills is an open standard at agentskills.io with 35+ adopters (Claude, Codex, Gemini, ADK, Copilot, etc.)
- Google ADK uses the same SKILL.md format and progressive disclosure (L1/L2/L3)
- ADK auto-generates `list_skills`, `load_skill`, `load_skill_resource` tools
- `.agents/skills/` is the standard cross-client discovery path
- Our FastMCP server complements ADK's in-process model by providing remote skill access over MCP

---

## Post-build review (→ `scratchpad/02_cc_review/`)

A second-pass review verified the PoC against FastMCP 3.2 docs (context7) and
agentskills.io spec, then added the following:

- **Env-driven reload**: `SKILLHUB_RELOAD` env var (docs recommend disabling in prod).
- **Offline workflow**: new `client/offline_demo.py` — syncs skills to `./cache/skills/`
  and proves they can be read with the server down (`--offline` flag).
- **MCP Inspector evidence**: transcript captured in
  `scratchpad/02_cc_review/inspector_evidence.md`.
- **CLAUDE.md**: agent-oriented entry point at repo root.
- **`.gitignore`**: adds `.claude/`, `reference/`, `cache/`.
- **Verified correct (no changes)**: `skill://{name}/_manifest` URI, multi-root provider
  wiring, `supporting_files="resources"`, `yaml.safe_load` parser, all frontmatter fields.
