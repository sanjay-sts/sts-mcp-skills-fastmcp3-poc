"""Consumer demo: pull a single skill using the canonical FastMCP client utilities.

Uses the helpers from `fastmcp.utilities.skills` exactly as documented at
https://gofastmcp.com/servers/providers/skills — no hand-rolled protocol code.
It intentionally does NOT invoke an LLM; the point is to show the pull contract.

Progressive-disclosure levels exercised:
  L1  — `list_skills(client)`                  name + description + uri
  L2  — `download_skill(client, name, dir)`    SKILL.md body (materialised to disk)
  L3  — same `download_skill` call             supporting files (text + blob)
  Manifest — `get_skill_manifest(client, n)`   structured file listing w/ sha256

Usage:
    uv run python client/consumer_demo.py                           # code-review (default)
    uv run python client/consumer_demo.py --skill project-scaffolding
    uv run python client/consumer_demo.py --skill project-scaffolding --save
"""

import argparse
import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.utilities.skills import download_skill, get_skill_manifest, list_skills


SERVER_URL = "http://localhost:10001/skillmcp"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "consumed"


def section(title: str):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}\n")


async def consume(skill: str, save: bool) -> int:
    print(f"Connecting to SkillHub at {SERVER_URL}")
    async with Client(SERVER_URL) as client:
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
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            section(f"download_skill(client, {skill!r}, {CACHE_DIR!s}, overwrite=True)")
            skill_path = await download_skill(client, skill, CACHE_DIR, overwrite=True)
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", default="code-review", help="Skill name (default: code-review)")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Call download_skill to materialise all files under cache/consumed/<skill>/",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(consume(args.skill, args.save)))


if __name__ == "__main__":
    main()
