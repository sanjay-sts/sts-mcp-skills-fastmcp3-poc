# Implementation Notes — Second-Pass Review

## Pre-flight audit findings

Verified against FastMCP 3.2 docs via context7 (`/prefecthq/fastmcp`):

- **Manifest URI is `skill://{name}/_manifest`** — our `client/test_client.py:53`
  was already correct. Earlier session research that said `manifest.json` was wrong.
- **Multi-root provider** — `roots=[...]` with first-match precedence. Matches our
  `server/main.py:36-42` usage exactly.
- **`supporting_files="resources"`** — correct for full enumeration via
  `list_resources()`; "template" mode would hide supporting files behind the manifest.
- **`reload=True`** — explicitly flagged as a dev-only setting in the docs.
- **Manifest contains SHA-256 hashes** — relevant for a future hash-aware sync (P4),
  deferred.
- **`sync_skills()` / `download_skill()`** — canonical utilities from
  `fastmcp.utilities.skills`; no dedicated RPC, they wrap `list_resources` +
  `read_resource`.

## Deviations from plan (if any)

### Offline demo — ASCII-only output

First run on Windows Python 3.13 failed with `UnicodeEncodeError: 'charmap' codec
can't encode character '\u2713'`. The demo originally printed a `✓` checkmark and
em-dash `—`; replaced with `[ok]` and `--` so it runs on cp1252 consoles without
forcing a `PYTHONIOENCODING=utf-8` workaround. The SKILL.md contents themselves are
read with `encoding="utf-8"` so non-ASCII skill text is unaffected.

### Inspector evidence — programmatic surrogate

MCP Inspector is a browser-based UI that cannot be driven headlessly. The evidence
file captures the same protocol calls made via `test_client.py` (the programmatic
equivalent of Inspector) plus explicit step-by-step instructions for reproducing in
the browser. Both establish the same contract: 7 resources, 2 tools, and a working
resource read + tool call over streamable HTTP.

### Description field showing only `>` in Inspector — root-caused and fixed

**Symptom:** MCP Inspector's Resources panel (and `list_skills(client)`) showed
`"description": ">"` for both `skill://code-review/SKILL.md` and
`skill://project-scaffolding/SKILL.md`.

**Root cause:** FastMCP's `SkillsDirectoryProvider` uses a line-by-line YAML
parser at
`.venv/Lib/site-packages/fastmcp/server/providers/skills/_common.py:33-74`
(`parse_frontmatter`). It splits on the first `:` per line and does not handle
YAML folded scalars. Our frontmatter had:

```yaml
description: >
  Review code changes for quality, bugs, security issues, and style.
  ...
```

The parser stored `description = ">"` and then ignored the indented continuation
lines because they contain no `:`. Our own server-side parser
(`server/main.py:_parse_frontmatter`) uses `yaml.safe_load` and is unaffected —
that's why tools (5a, 5b, 6) in `test_client_transcript.txt` showed the full
descriptions, but the resource-level `description` field surfaced in Inspector
came from the provider's parser and was broken.

**Fix:** Rewrite both `SKILL.md` descriptions as single-line quoted strings. They
are still well under the agentskills.io 1024-char limit and contain the same
substantive text.

**Verified after fix:** `list_skills` transcript now shows
`code-review: Review code changes for quality, bugs, security issues, and style...`
— full text. Re-listing resources in Inspector shows the resolved descriptions.

**Note (upstream):** The FastMCP parser limitation still affects any skill whose
SKILL.md uses a folded scalar. A more robust fix would be upstream (replace the
line parser with `yaml.safe_load`), but that is out of scope here and we sidestep
it by keeping descriptions on a single line — which is also what the
agentskills.io examples do.

### Reload env parse

Treated `"0"`, `"false"`, `"False"`, and empty string as false; everything else is
truthy. Avoids importing `distutils.util.strtobool` (removed in Python 3.12) and
doesn't depend on `os.environ.get(..., "1") == "1"` which would accept `"yes"` as
false — fine for a small PoC, explicit here.

### Offline demo defaults

`sync_phase` uses `overwrite=True` because the demo is expected to be run repeatedly.
`CACHE_DIR` is `<repo>/cache/skills/` (absolute, anchored to the script location) so
running from any CWD still hits the same directory.

## Verification

Commands run and outputs captured in:

- `test_client_transcript.txt` — P1.4 regression run
- `inspector_evidence.md` — P3.1 MCP Inspector session
