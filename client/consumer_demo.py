# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "fastmcp>=3.2.0",
# ]
# ///
"""Consumer demo: pull a single skill using the canonical FastMCP client utilities.

Uses the helpers from `fastmcp.utilities.skills` exactly as documented at
https://gofastmcp.com/servers/providers/skills — no hand-rolled protocol code.
It intentionally does NOT invoke an LLM; the point is to show the pull contract.

Progressive-disclosure levels exercised:
  L1  — `list_skills(client)`                  name + description + uri
  L2  — `download_skill(client, name, dir)`    SKILL.md body (materialised to disk)
  L3  — same `download_skill` call             supporting files (text + blob)
  Manifest — `get_skill_manifest(client, n)`   structured file listing w/ sha256

Portable — this file is self-contained (PEP 723 inline metadata). Copy or curl it
into any folder and run with `uv run path/to/consumer_demo.py` — uv provisions a
temporary venv with fastmcp on first call; no project, no `pip install -e .`
required.

Usage:
    # From the repo (project env is already synced):
    uv run python client/consumer_demo.py
    uv run python client/consumer_demo.py --skill project-scaffolding --save

    # From any folder, no project needed:
    uv run path/to/consumer_demo.py --skill code-review
    uv run path/to/consumer_demo.py --server http://some-host:10001/skillmcp --save

    # Override where downloaded skills land (defaults to ./cache/consumed/ in CWD):
    uv run path/to/consumer_demo.py --save --cache ~/my-skills

Env overrides (same effect as flags):
    SKILLHUB_URL                 overrides --server
    SKILLHUB_CACHE               overrides --cache
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.utilities.skills import download_skill, get_skill_manifest, list_skills


DEFAULT_SERVER_URL = os.environ.get("SKILLHUB_URL", "http://localhost:10001/skillmcp")
DEFAULT_CACHE_DIR = Path(os.environ.get("SKILLHUB_CACHE", "cache/consumed")).expanduser()

# Canonical client-side destinations, mirroring the server-side vendor providers
# listed at https://gofastmcp.com/servers/providers/skills#vendor-providers.
# Download into one of these to make the synced skills immediately discoverable
# by that vendor's agent (e.g., Claude Code picks up ~/.claude/skills/).
VENDOR_PATHS = {
    "claude":   Path("~/.claude/skills"),
    "cursor":   Path("~/.cursor/skills"),
    "copilot":  Path("~/.copilot/skills"),
    "codex":    Path("~/.codex/skills"),
    "gemini":   Path("~/.gemini/skills"),
    "goose":    Path("~/.config/agents/skills"),
    "opencode": Path("~/.config/opencode/skills"),
}


def section(title: str):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}\n")


async def consume(skill: str, save: bool, server_url: str, cache_dir: Path) -> int:
    print(f"Connecting to SkillHub at {server_url}")
    async with Client(server_url) as client:
        # --- L1: list_skills returns SkillSummary(name, description, uri) ---------
        section("L1 -- list_skills(client)")
        skills = await list_skills(client)
        by_name = {s.name: s for s in skills}
        for s in skills:
            flag = "<-- selected" if s.name == skill else ""
            print(f"  {s.name:<24} {flag}")
            print(f"    uri:         {s.uri}")
            print(f"    description: {s.description[:120]}{'...' if len(s.description) > 120 else ''}\n")
        if skill not in by_name:
            print(f"  ERROR: skill {skill!r} not found. Available: {sorted(by_name)}")
            return 1

        # --- Manifest: structured file listing ------------------------------------
        section(f"get_skill_manifest(client, {skill!r})")
        manifest = await get_skill_manifest(client, skill)
        print(f"  name:  {manifest.name}")
        print(f"  files: {len(manifest.files)}")
        for f in manifest.files:
            print(f"    {f.path:<50} {f.size:>8} bytes  {f.hash[:19]}")

        # --- L2 + L3: full skill pull via download_skill --------------------------
        if save:
            cache_dir.mkdir(parents=True, exist_ok=True)
            section(f"download_skill(client, {skill!r}, {cache_dir!s}, overwrite=True)")
            skill_path = await download_skill(client, skill, cache_dir, overwrite=True)
            print(f"  -> {skill_path}\n")
            for p in sorted(skill_path.rglob("*")):
                if p.is_file():
                    size = p.stat().st_size
                    print(f"    {p.relative_to(skill_path)}  ({size} bytes)")

            section("L2 -- SKILL.md (materialised to disk)")
            print((skill_path / "SKILL.md").read_text(encoding="utf-8"))
        else:
            # No --save: still demonstrate L2 by reading SKILL.md directly over MCP
            section("L2 -- SKILL.md (read over MCP, not written to disk)")
            result = await client.read_resource(f"skill://{skill}/SKILL.md")
            body = getattr(result[0], "text", "")
            print(body)
            print("\n(Run again with --save to also materialise all L3 supporting files.)")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Pull a single skill from a remote FastMCP server.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--skill", default="code-review", help="Skill name (default: code-review)")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Call download_skill to materialise all files under <cache>/<skill>/",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER_URL,
        help=f"MCP server URL (default: {DEFAULT_SERVER_URL}; env: SKILLHUB_URL)",
    )
    parser.add_argument(
        "--cache",
        default=None,
        help=f"Local directory for --save (default: {DEFAULT_CACHE_DIR}; env: SKILLHUB_CACHE)",
    )
    parser.add_argument(
        "--vendor",
        choices=sorted(VENDOR_PATHS),
        help=(
            "Shortcut: write into the canonical directory for a vendor "
            "(claude=~/.claude/skills, cursor=~/.cursor/skills, ...). "
            "Overrides --cache unless --cache is also given explicitly."
        ),
    )
    args = parser.parse_args()
    if args.cache is not None:
        cache_dir = Path(args.cache).expanduser().resolve()
    elif args.vendor is not None:
        cache_dir = VENDOR_PATHS[args.vendor].expanduser().resolve()
    else:
        cache_dir = DEFAULT_CACHE_DIR.resolve()
    sys.exit(asyncio.run(consume(args.skill, args.save, args.server, cache_dir)))


if __name__ == "__main__":
    main()
