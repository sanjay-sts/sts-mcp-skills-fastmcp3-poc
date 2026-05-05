# Graph Report - .  (2026-05-04)

## Corpus Check
- Corpus is ~17,335 words - fits in a single context window. You may not need a graph.

## Summary
- 258 nodes · 350 edges · 23 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Review Reload Env & YAML Bug|Review: Reload Env & YAML Bug]]
- [[_COMMUNITY_User Docs & Core Concepts|User Docs & Core Concepts]]
- [[_COMMUNITY_Skills & Project Templates|Skills & Project Templates]]
- [[_COMMUNITY_Client Utilities & Testing Surface|Client Utilities & Testing Surface]]
- [[_COMMUNITY_test_client.py Functions|test_client.py Functions]]
- [[_COMMUNITY_Server Design Decisions|Server Design Decisions]]
- [[_COMMUNITY_MCP Inspector Evidence|MCP Inspector Evidence]]
- [[_COMMUNITY_Offline Workflow & Cache|Offline Workflow & Cache]]
- [[_COMMUNITY_Initial Build Plan & Tasks|Initial Build Plan & Tasks]]
- [[_COMMUNITY_Compliance Audit & Provider|Compliance Audit & Provider]]
- [[_COMMUNITY_Demo Scripts (consumer & offline)|Demo Scripts (consumer & offline)]]
- [[_COMMUNITY_servermain.py (SkillHub)|server/main.py (SkillHub)]]
- [[_COMMUNITY_scaffold.py Script|scaffold.py Script]]
- [[_COMMUNITY_Agent-Facing Docs (CLAUDE.md)|Agent-Facing Docs (CLAUDE.md)]]
- [[_COMMUNITY_Reload Setting Note|Reload Setting Note]]
- [[_COMMUNITY_CallToolResult Note|CallToolResult Note]]
- [[_COMMUNITY_Custom Tools Plan Item|Custom Tools Plan Item]]
- [[_COMMUNITY_Health Endpoint Plan Item|Health Endpoint Plan Item]]
- [[_COMMUNITY_Test Client Transcript Plan|Test Client Transcript Plan]]
- [[_COMMUNITY_P5 Spec Alignment (Deferred)|P5 Spec Alignment (Deferred)]]
- [[_COMMUNITY_Hygiene Requirement|Hygiene Requirement]]
- [[_COMMUNITY_No New Runtime Deps|No New Runtime Deps]]
- [[_COMMUNITY_No Core Rewiring|No Core Rewiring]]

## God Nodes (most connected - your core abstractions)
1. `Compliance Audit vs gofastmcp.com` - 11 edges
2. `section()` - 10 edges
3. `run_all()` - 10 edges
4. `Initial Build Plan` - 10 edges
5. `README — FastMCP3 Skill Provider PoC` - 9 edges
6. `Skill: code-review` - 9 edges
7. `Task List (Initial Build + Post-Review)` - 9 edges
8. `SkillsDirectoryProvider (FastMCP)` - 9 edges
9. `TESTING.md Testing Guide` - 8 edges
10. `Implementation Notes` - 8 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `run()`  [INFERRED]
  C:\WorkSpace\Sanjay\FoundryCore\sts-mcp-skills-fastmcp3-poc\server\main.py → C:\WorkSpace\Sanjay\FoundryCore\sts-mcp-skills-fastmcp3-poc\client\offline_demo.py
- `SKILL.md description Single-Line String Rule` --semantically_similar_to--> `Improvement: yaml.safe_load Replaces Custom Regex`  [INFERRED] [semantically similar]
  CLAUDE.md → scratchpad/01_cc_initial_build/implementation.md
- `.agents/skills/ Cross-Agent Root` --semantically_similar_to--> `Vendor Skill Providers (Claude/Cursor/etc.)`  [INFERRED] [semantically similar]
  CLAUDE.md → TESTING.md
- `main()` --calls--> `run()`  [INFERRED]
  C:\WorkSpace\Sanjay\FoundryCore\sts-mcp-skills-fastmcp3-poc\client\consumer_demo.py → C:\WorkSpace\Sanjay\FoundryCore\sts-mcp-skills-fastmcp3-poc\client\offline_demo.py
- `README — FastMCP3 Skill Provider PoC` --cites--> `TESTING.md Testing Guide`  [EXTRACTED]
  README.md → TESTING.md

## Hyperedges (group relationships)
- **SkillHub Server Component Assembly** — concept_skillhub_server, concept_skillsdirectoryprovider, concept_search_skills_tool, concept_get_skill_metadata_tool, concept_health_endpoint, concept_streamable_http [EXTRACTED 0.95]
- **fastmcp.utilities.skills Helper Set** — concept_list_skills, concept_get_skill_manifest, concept_download_skill, concept_sync_skills [EXTRACTED 1.00]
- **Three Client Demo Scripts (Test, Offline, Consumer)** — concept_test_client, concept_offline_demo, concept_consumer_demo [EXTRACTED 0.95]
- **Offline workflow: server, sync helper, disk cache** — design_endpoint_skillmcp, plan_canonical_helpers, plan_cache_skills_dir, plan_offline_demo_py [EXTRACTED 0.90]
- **YAML folded-scalar bug detection, root cause, and fix** — impl_description_yaml_bug, impl_yaml_folded_scalar_root_cause, impl_fix_single_line_descriptions, insp_post_fix_capture [EXTRACTED 0.90]
- **Remote hosting verified: 7 resources, 2 tools, health endpoint** — insp_seven_resources, insp_two_tools, insp_health_response, plan_health_endpoint [EXTRACTED 0.85]

## Communities

### Community 0 - "Review: Reload Env & YAML Bug"
Cohesion: 0.06
Nodes (35): Env-driven reload design, Pre-flight audit findings, Bug: description showing only > in Inspector, Fix: single-line quoted descriptions in SKILL.md, Deviation: explicit reload env parse logic, Root cause: YAML folded scalar parser limitation in FastMCP _common.py, Commit 3a860b4 (single-line descriptions), _meta.fastmcp.skill grouping with is_manifest flags (+27 more)

### Community 1 - "User Docs & Core Concepts"
Cohesion: 0.09
Nodes (27): CLAUDE.md Agent Guide, Repo Layout, skill:// Resource URI Scheme, Security Posture (No Auth, PoC), SkillHub Project Overview, uv Dependency Management, Audit: Manifest JSON Schema, Audit: Resource URI Scheme (+19 more)

### Community 2 - "Skills & Project Templates"
Cohesion: 0.11
Nodes (26): compatibility Top-Level Field, Google ADK, agentskills.io Open Standard, Progressive Disclosure (L1/L2/L3), YAML Frontmatter (SKILL.md), Deviation: CallToolResult Return Type, Improvement: compatibility Top-Level Move, Implementation Notes (+18 more)

### Community 3 - "Client Utilities & Testing Surface"
Cohesion: 0.18
Nodes (21): Audit: fastmcp.utilities.skills Helpers, Claude Code as MCP Client, consumer_demo.py Client Script, download_skill Utility, get_skill_manifest Utility, list_skills Utility, .mcp.json Project-Scoped Config, Offline Skill Cache (+13 more)

### Community 4 - "test_client.py Functions"
Cohesion: 0.19
Nodes (19): Test client for SkillHub — exercises all skill provider capabilities., Test 1: Discover available skills., Test 2: List all skill:// resources., Test 3: Read a skill's SKILL.md content., Test 4: Read a skill's manifest., Test 5: Call search_skills tool., Test 6: Call get_skill_metadata tool., Test 7: Download a single skill to a temp directory. (+11 more)

### Community 5 - "Server Design Decisions"
Cohesion: 0.12
Nodes (19): SKILL.md description Single-Line String Rule, yaml.safe_load Frontmatter Parsing, Intentional Deviations (Not Gaps), PyYAML safe_load, Design Data Flow, Decision: No Custom Provider Subclass, Decision: reload=True for Dev, Decision: Single server/main.py (+11 more)

### Community 6 - "MCP Inspector Evidence"
Cohesion: 0.11
Nodes (19): Endpoint http://localhost:10001/skillmcp, Inspector evidence text format, Deviation: Inspector evidence as programmatic surrogate, Health response: 2 skills (code-review, project-scaffolding), Browser repro steps (Inspector at :6274), 7 skill:// resources exposed, Inspector evidence summary, 2 tools exposed: search_skills, get_skill_metadata (+11 more)

### Community 7 - "Offline Workflow & Cache"
Cohesion: 0.15
Nodes (17): Offline cache workflow (two phases), Phase 1: sync from server, Phase 2: offline read from disk, Rationale: simplest thing that works (reuse sync_skills, gitignore cache, single flag), Verification matrix (4 scenarios), Deviation: offline demo defaults (overwrite=True, anchored CACHE_DIR), Deviation: ASCII-only output (UnicodeEncodeError fix), ./cache/skills/ persistent directory (+9 more)

### Community 8 - "Initial Build Plan & Tasks"
Cohesion: 0.21
Nodes (15): get_skill_metadata MCP Tool, /health HTTP Endpoint, search_skills MCP Tool, SkillHub Server, Plan Architecture (FastMCP SkillHub), Plan File Structure, Initial Build Plan, Plan Task 0: Scratchpad Documentation (+7 more)

### Community 9 - "Compliance Audit & Provider"
Cohesion: 0.18
Nodes (14): supporting_files=resources Mode, Compliance Audit vs gofastmcp.com, Audit: SkillsDirectoryProvider Constructor, Audit Issue Fixed: Windows Path Separators in get_skill_metadata, Audit: Production vs Development, Audit: SKILL.md Format, Audit: Vendor Providers Choice, Audit Verdict: Conformant (+6 more)

### Community 10 - "Demo Scripts (consumer & offline)"
Cohesion: 0.26
Nodes (11): consume(), main(), section(), main(), offline_phase(), Offline workflow demo — sync skills to a persistent cache, then read them withou, Connect to server and sync all skills into the persistent cache., Read skills purely from the local cache; no network, no client. (+3 more)

### Community 11 - "server/main.py (SkillHub)"
Cohesion: 0.21
Nodes (10): get_skill_metadata(), _load_skills_index(), main(), _parse_frontmatter(), SkillHub — FastMCP3 skill provider over streamable HTTP., Search skills by keyword across names and descriptions.      Args:         qu, Get detailed metadata for a specific skill.      Args:         skill_name: Th, Extract YAML frontmatter from SKILL.md content as a dict. (+2 more)

### Community 12 - "scaffold.py Script"
Cohesion: 0.47
Nodes (5): load_templates(), main(), Load template definitions from assets/project-template.json., Generate project structure from template. Returns manifest of created files., scaffold()

### Community 13 - "Agent-Facing Docs (CLAUDE.md)"
Cohesion: 0.5
Nodes (4): CLAUDE.md auto-loaded by AI clients, CLAUDE.md AI agent guide, P-DOCS Refresh All Docs, FR5: Agent-facing docs (CLAUDE.md, README)

### Community 15 - "Reload Setting Note"
Cohesion: 1.0
Nodes (1): reload=True Setting

### Community 16 - "CallToolResult Note"
Cohesion: 1.0
Nodes (1): CallToolResult.content[0].text

### Community 17 - "Custom Tools Plan Item"
Cohesion: 1.0
Nodes (1): Custom tools: search_skills, get_skill_metadata

### Community 18 - "Health Endpoint Plan Item"
Cohesion: 1.0
Nodes (1): GET /health custom_route endpoint

### Community 19 - "Test Client Transcript Plan"
Cohesion: 1.0
Nodes (1): test_client_transcript.txt

### Community 20 - "P5 Spec Alignment (Deferred)"
Cohesion: 1.0
Nodes (1): P5 Spec alignment (deferred)

### Community 21 - "Hygiene Requirement"
Cohesion: 1.0
Nodes (1): FR6: Hygiene (gitignore covers cache, .claude, reference)

### Community 22 - "No New Runtime Deps"
Cohesion: 1.0
Nodes (1): NFR: No new runtime deps

### Community 23 - "No Core Rewiring"
Cohesion: 1.0
Nodes (1): NFR: Review additive, no core rewiring

## Knowledge Gaps
- **95 isolated node(s):** `Offline workflow demo — sync skills to a persistent cache, then read them withou`, `Connect to server and sync all skills into the persistent cache.`, `Read skills purely from the local cache; no network, no client.`, `Test client for SkillHub — exercises all skill provider capabilities.`, `Test 1: Discover available skills.` (+90 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Reload Setting Note`** (1 nodes): `reload=True Setting`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `CallToolResult Note`** (1 nodes): `CallToolResult.content[0].text`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Custom Tools Plan Item`** (1 nodes): `Custom tools: search_skills, get_skill_metadata`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Health Endpoint Plan Item`** (1 nodes): `GET /health custom_route endpoint`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Test Client Transcript Plan`** (1 nodes): `test_client_transcript.txt`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `P5 Spec Alignment (Deferred)`** (1 nodes): `P5 Spec alignment (deferred)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Hygiene Requirement`** (1 nodes): `FR6: Hygiene (gitignore covers cache, .claude, reference)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `No New Runtime Deps`** (1 nodes): `NFR: No new runtime deps`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `No Core Rewiring`** (1 nodes): `NFR: Review additive, no core rewiring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SkillsDirectoryProvider (FastMCP)` connect `Compliance Audit & Provider` to `Initial Build Plan & Tasks`, `User Docs & Core Concepts`, `Server Design Decisions`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Phase 1: sync from server` connect `Offline Workflow & Cache` to `Review: Reload Env & YAML Bug`, `MCP Inspector Evidence`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `README — FastMCP3 Skill Provider PoC` connect `User Docs & Core Concepts` to `Compliance Audit & Provider`, `Client Utilities & Testing Surface`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `Offline workflow demo — sync skills to a persistent cache, then read them withou`, `Connect to server and sync all skills into the persistent cache.`, `Read skills purely from the local cache; no network, no client.` to the rest of the system?**
  _95 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Review: Reload Env & YAML Bug` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `User Docs & Core Concepts` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Skills & Project Templates` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._