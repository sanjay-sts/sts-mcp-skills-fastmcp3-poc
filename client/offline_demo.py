"""Offline workflow demo — sync skills to a persistent cache, then read them without the server.

Usage:
    # With server running — sync then read from disk:
    uv run python client/offline_demo.py

    # Server offline — read the cache populated by a prior sync:
    uv run python client/offline_demo.py --offline
"""

import argparse
import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.utilities.skills import sync_skills


SERVER_URL = "http://localhost:10001/skillmcp"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "skills"


def section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


async def sync_phase() -> list[Path]:
    """Connect to server and sync all skills into the persistent cache."""
    section(f"Phase 1 -- sync from {SERVER_URL} to {CACHE_DIR}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    async with Client(SERVER_URL) as client:
        paths = await sync_skills(client, CACHE_DIR, overwrite=True)
    for p in paths:
        print(f"  [ok] {p.relative_to(CACHE_DIR.parent)}")
    print(f"\n  Synced {len(paths)} skill(s).")
    return paths


def offline_phase() -> int:
    """Read skills purely from the local cache; no network, no client."""
    section(f"Phase 2 -- read from disk only: {CACHE_DIR}")
    if not CACHE_DIR.exists():
        print(f"  Cache is empty. Run without --offline first (server must be up).")
        return 1

    skill_dirs = sorted(d for d in CACHE_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print(f"  No skills in cache. Run without --offline first.")
        return 1

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"  [skip] {skill_dir.name}: no SKILL.md in cache")
            continue
        text = skill_md.read_text(encoding="utf-8")
        files = sorted(str(f.relative_to(skill_dir)) for f in skill_dir.rglob("*") if f.is_file())
        print(f"  === {skill_dir.name} ({len(files)} file(s), {len(text)} chars in SKILL.md) ===")
        preview = text[: text.find("\n\n", 200) if text.find("\n\n", 200) > 0 else 300]
        for line in preview.splitlines()[:10]:
            print(f"    {line}")
        print(f"    ... [{len(text) - len(preview)} more chars]\n")

    print(f"  Read {len(skill_dirs)} skill(s) from disk. Server was never contacted in this phase.")
    return 0


async def run(offline_only: bool) -> int:
    if not offline_only:
        await sync_phase()
    else:
        section("Skipping sync phase (--offline)")
    return offline_phase()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip sync; read existing cache only. Use when the server is down.",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(run(args.offline)))


if __name__ == "__main__":
    main()
