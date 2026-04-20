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

### List-skills description shows `>` literal (pre-existing, unchanged)

`list_skills(client)` utility returns `SkillSummary.description` starting with the
literal `>` YAML folded-scalar introducer, so `skill.description[:80]` prints as
`">..."`. This is the FastMCP client utility's behavior, independent of our
server-side `_parse_frontmatter` (which uses `yaml.safe_load` and returns the
resolved string correctly — see test 5a, 5b, 6 output in
`test_client_transcript.txt`). No action taken; upstream behavior, not introduced
here, not in scope for this review.

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
