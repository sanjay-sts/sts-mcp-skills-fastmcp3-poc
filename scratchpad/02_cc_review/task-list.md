# Task List — Second-Pass Review

## P1 — Correctness & Hygiene
- [x] P1.1 `.gitignore`: add `.claude/`, `reference/`, `cache/`
- [x] P1.2 `server/main.py`: env-driven `SKILLHUB_RELOAD`, startup log
- [x] P1.3 Mark `01_cc_initial_build/task-list.md` Task 14 complete
- [x] P1.4 Run server + `client/test_client.py`, capture `test_client_transcript.txt` (8/8 pass)

## P2 — Offline story
- [x] P2.1 `client/offline_demo.py` — sync + offline-read with `--offline` flag
- [x] P2.1v Verified: online run captured in `offline_demo_online_transcript.txt`
- [x] P2.1v Verified: server-down run captured in `offline_demo_offline_transcript.txt`
- [x] P2.2 README **Offline Workflow** + **Configuration** sections

## P3 — Remote story (MCP Inspector)
- [x] P3.1 Inspector evidence captured as `inspector_evidence.md` (protocol-level equivalent + manual repro steps)
- [x] P3.2 README **Verified via MCP Inspector** section

## P-DOCS — Refresh all docs (user-requested)
- [x] D1 01_cc task-list.md — Task 14 done + footnote
- [x] D2 01_cc implementation.md — "Post-build review" section
- [x] D3 01_cc design.md + requirements.md — supersession notes
- [x] D4 01_cc plan.md — status note
- [x] D5 02_cc_review/ folder populated (this task list, requirements, design, plan, implementation)
- [x] D6 README.md — offline + inspector + config sections
- [x] D7 CLAUDE.md created at repo root

## Commit
- [x] C1 Stage intended files only (reference/, .claude/, cache/ correctly ignored)
- [x] C2 Single commit `64a3f29` on #10_local_build (no push; awaiting user go-ahead)
