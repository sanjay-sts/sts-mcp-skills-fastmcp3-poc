# Compliance audit vs. https://gofastmcp.com/servers/providers/skills

Line-by-line validation of our PoC against the official FastMCP Skills Provider
page (retrieved 2026-04-19). Every item in the spec is listed here with the
file/line in our code and a verdict.

## 1. `SkillsDirectoryProvider` constructor

| Spec parameter | Spec default | Our value | File:line | Verdict |
|---|---|---|---|---|
| `roots: Path \| list[Path]` | (required) | `[SKILLS_DIR, AGENTS_SKILLS_DIR]` (list) | `server/main.py:36` | ✅ Conformant — uses the list form; first-match precedence honoured |
| `supporting_files: str` | `"template"` | `"resources"` | `server/main.py:40` | ✅ Valid enum value, deliberate choice (documented in `design.md`) |
| `reload: bool` | `False` | `RELOAD` (env-driven, default `True`) | `server/main.py:41` | ✅ Valid; dev default flagged, `SKILLHUB_RELOAD=0` turns it off for production per docs |
| `main_file_name: str` | `"SKILL.md"` | not set (default) | — | ✅ Matches |

Both roots are passed as `Path` objects. `AGENTS_SKILLS_DIR` is only appended if
it exists (our `server/main.py:26`), matching spec guidance for optional roots.

## 2. Resource URI scheme

Spec requires three URI shapes. All three are exercised by our clients.

| Spec URI | Exercised in | Test |
|---|---|---|
| `skill://{name}/SKILL.md` | `client/test_client.py:43`, `client/consumer_demo.py` (L2 read) | Test 3, transcript shows ~1,615-char body |
| `skill://{name}/_manifest` | `client/test_client.py:53`, `consumer_demo.py` via `get_skill_manifest` | Test 4, manifest parse returns 4 files for project-scaffolding |
| `skill://{name}/{path/to/file}` | `client/test_client.py:36` (list), `consumer_demo.py` via `download_skill` | Test 2 lists all 7 URIs including the 3 supporting files |

All supporting-file URIs use forward slashes per `_common.py:102` on the
provider side. Our own `get_skill_metadata` tool now also emits forward slashes
(fixed in this audit — was using `str(Path)` which is OS-native).

## 3. Manifest JSON schema

Spec shape:

```json
{"skill": "name", "files": [{"path": "...", "size": N, "hash": "sha256:..."}]}
```

We do not produce the manifest ourselves — `SkillsDirectoryProvider` does.
`client/consumer_demo.py` consumes it through `get_skill_manifest(...)` which
returns `SkillManifest(name, files=[SkillFile(path, size, hash)])`. Live
transcript (`scratchpad/02_cc_review/consumer_demo_project-scaffolding_transcript.txt`)
shows all 4 files with `sha256:…` prefixed hashes. ✅ Conformant.

## 4. Client utilities `fastmcp.utilities.skills`

Spec lists four. We use all four across the two client scripts:

| Utility | Spec signature (paraphrased) | Our call site | Verdict |
|---|---|---|---|
| `list_skills(client)` | returns objects with `name`, `description` (and `uri` in our installed source) | `client/consumer_demo.py` (L1 display), transitively used by `sync_skills` | ✅ |
| `get_skill_manifest(client, skill_name)` | returns `Manifest` with `files` of `path/size/hash` | `client/consumer_demo.py` | ✅ |
| `download_skill(client, skill_name, target, overwrite=False)` | materialises one skill to disk; handles text + blob internally | `client/consumer_demo.py` (with `--save`) | ✅ |
| `sync_skills(client, target, overwrite=False)` | materialises every skill; same overwrite semantics | `client/test_client.py:102`, `client/offline_demo.py:32` | ✅ |

Note: installed source calls the destination parameter `target_dir` (the page
uses `destination`); both are positional and we pass as such. No impact.

Important: we do **not** re-implement `read_resource` filtering or base64
decoding of blob files — `download_skill` does that internally. Earlier draft
of `consumer_demo.py` had hand-rolled that logic; current version does not.

## 5. SKILL.md format

| Spec requirement | Our SKILL.md | Verdict |
|---|---|---|
| File must exist at skill root | `skills/code-review/SKILL.md`, `skills/project-scaffolding/SKILL.md` | ✅ |
| Frontmatter optional | Present on both, opens with `---` | ✅ |
| `description` optional | Present on both, single-line quoted (to dodge FastMCP's naive parser on folded scalars — see `implementation.md`) | ✅ |
| Description length | Spec says no max documented | Both under ~330 chars (well under the 1024 agentskills.io ceiling) |
| Directory name is the skill identifier | `code-review`, `project-scaffolding` (lowercase + hyphens) | ✅ |
| Fallback if no frontmatter: first meaningful line | We always include frontmatter; fallback path untested (not required) | N/A |

## 6. Vendor providers

Spec lists `ClaudeSkillsProvider`, `CursorSkillsProvider`, etc. — wrappers that
hard-code platform directories. We intentionally use `SkillsDirectoryProvider`
with project-relative roots instead, because this PoC hosts a project-scoped
skill catalog, not a user-level one. This is an expected use case per the spec
(which shows `SkillsDirectoryProvider` first and introduces vendor providers
as conveniences). ✅ No conformance issue.

## 7. Production vs development

- Spec: `reload=True` is development-only; "disable it in production."
  - Our implementation honours this via `SKILLHUB_RELOAD` env var (default `1`
    for dev friendliness; `0` flips to production). Documented in README
    Configuration table and `CLAUDE.md`. ✅

- Spec multi-root example: project directory first, user-level second.
  - Our roots list order: `[./skills/, .agents/skills/]` — project-local first,
    cross-agent standard second. ✅

## 8. Security / size / format

Spec enumerates no constraints beyond the SHA-256 manifest. `download_skill`
in the FastMCP source (`fastmcp/utilities/skills.py:166-215`) additionally
rejects absolute paths and paths that escape the destination — our consumer
demo inherits this protection. ✅

## 9. Example code parity

| Spec example | Our analogue | Notes |
|---|---|---|
| `SkillsDirectoryProvider(roots=Path.home()/".claude"/"skills")` | `server/main.py:37-42` | Identical pattern, our roots differ by design |
| `resources = await client.list_resources()` then iterate `r.uri` | `client/test_client.py:34-37` | Match |
| `await client.read_resource("skill://my-skill/SKILL.md")` | `client/test_client.py:43`, `consumer_demo.py` no-save branch | Match |
| `list_skills(client)` | `consumer_demo.py` L1 | Match |
| `download_skill(client, name, dir)` / `sync_skills(client, dir)` | `consumer_demo.py --save`, `test_client.py`, `offline_demo.py` | Match |
| `get_skill_manifest(client, name)` iterating `manifest.files` | `consumer_demo.py` manifest section | Match |

## Issues found and fixed during this audit

1. **Windows path separators in custom tool output** — `server/main.py:94` was
   emitting `\` on Windows inside the custom `get_skill_metadata` tool response
   (`assets\project-template.json`). FastMCP's own manifest uses POSIX paths
   (`_common.py:102`). Fixed to `.relative_to(skill_dir).as_posix()`.

No other discrepancies were found.

## Intentional deviations (not gaps)

| Choice | Spec says | We do | Rationale |
|---|---|---|---|
| `supporting_files="resources"` | default `"template"` | `"resources"` | PoC wants full upfront enumeration in Inspector and Resources panel; documented in `design.md` |
| `reload` default | `False` | `True` (via env var) | Dev-first PoC; env toggle documented everywhere a user would look |
| Custom tools (`search_skills`, `get_skill_metadata`) | spec is silent | We add two `@mcp.tool` functions | Additive — doesn't alter any spec-defined URI or resource; visible in Inspector's Tools panel as extras |
| SKILL.md description YAML form | "Optional YAML frontmatter", no style mandated | Single-line quoted, not folded scalar | FastMCP's naive parser does not resolve folded scalars; single-line keeps the description readable in Inspector's Resources panel |

## Verdict

The PoC conforms to every requirement on <https://gofastmcp.com/servers/providers/skills>.
The one gap discovered during audit (Windows path separators in our custom
tool response) was fixed. Intentional deviations are documented.
