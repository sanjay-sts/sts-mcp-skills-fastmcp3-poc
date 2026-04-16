"""Test client for SkillHub — exercises all skill provider capabilities."""

import asyncio
import json
import tempfile
from pathlib import Path

from fastmcp import Client
from fastmcp.utilities.skills import download_skill, list_skills, sync_skills


SERVER_URL = "http://localhost:8000/mcp"


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_list_skills(client: Client):
    """Test 1: Discover available skills."""
    section("1. List Skills")
    skills = await list_skills(client)
    for skill in skills:
        print(f"  - {skill.name}: {skill.description[:80]}...")
    print(f"\n  Total: {len(skills)} skill(s)")
    return skills


async def test_list_resources(client: Client):
    """Test 2: List all skill:// resources."""
    section("2. List Resources")
    resources = await client.list_resources()
    for r in resources:
        print(f"  {r.uri}")
    print(f"\n  Total: {len(resources)} resource(s)")


async def test_read_skill(client: Client, skill_name: str):
    """Test 3: Read a skill's SKILL.md content."""
    section(f"3. Read skill://{skill_name}/SKILL.md")
    content = await client.read_resource(f"skill://{skill_name}/SKILL.md")
    text = content[0].text if hasattr(content[0], "text") else str(content[0])
    preview = text[:300]
    print(f"  {preview}...")
    print(f"\n  Total length: {len(text)} chars")


async def test_read_manifest(client: Client, skill_name: str):
    """Test 4: Read a skill's manifest."""
    section(f"4. Read skill://{skill_name}/_manifest")
    content = await client.read_resource(f"skill://{skill_name}/_manifest")
    text = content[0].text if hasattr(content[0], "text") else str(content[0])
    manifest = json.loads(text)
    print(f"  Skill: {manifest.get('skill', 'N/A')}")
    for f in manifest.get("files", []):
        print(f"    {f['path']} ({f.get('size', '?')} bytes)")


async def test_search_skills(client: Client):
    """Test 5: Call search_skills tool."""
    section("5a. Search Skills (query='review')")
    result = await client.call_tool("search_skills", {"query": "review"})
    text = result.content[0].text if result.content else str(result)
    print(f"  {text}")

    section("5b. Search Skills (query='scaffold')")
    result = await client.call_tool("search_skills", {"query": "scaffold"})
    text = result.content[0].text if result.content else str(result)
    print(f"  {text}")


async def test_get_metadata(client: Client):
    """Test 6: Call get_skill_metadata tool."""
    section("6. Get Skill Metadata (project-scaffolding)")
    result = await client.call_tool("get_skill_metadata", {"skill_name": "project-scaffolding"})
    text = result.content[0].text if result.content else str(result)
    data = json.loads(text)
    print(f"  Name: {data.get('name')}")
    print(f"  Files: {len(data.get('files', []))}")
    print(f"  Total size: {data.get('total_size', 0)} bytes")
    for f in data.get("files", []):
        print(f"    {f['path']} ({f['size']} bytes)")


async def test_download_skill(client: Client):
    """Test 7: Download a single skill to a temp directory."""
    section("7. Download Skill (code-review)")
    with tempfile.TemporaryDirectory() as tmp:
        path = await download_skill(client, "code-review", Path(tmp))
        print(f"  Downloaded to: {path}")
        for f in Path(tmp).rglob("*"):
            if f.is_file():
                print(f"    {f.relative_to(tmp)}")


async def test_sync_skills(client: Client):
    """Test 8: Sync all skills to a temp directory."""
    section("8. Sync All Skills")
    with tempfile.TemporaryDirectory() as tmp:
        paths = await sync_skills(client, Path(tmp))
        print(f"  Synced {len(paths)} skill(s) to: {tmp}")
        for f in sorted(Path(tmp).rglob("*")):
            if f.is_file():
                print(f"    {f.relative_to(tmp)}")


async def run_all():
    print(f"Connecting to SkillHub at {SERVER_URL}...")
    async with Client(SERVER_URL) as client:
        await test_list_skills(client)
        await test_list_resources(client)
        await test_read_skill(client, "code-review")
        await test_read_manifest(client, "project-scaffolding")
        await test_search_skills(client)
        await test_get_metadata(client)
        await test_download_skill(client)
        await test_sync_skills(client)

    section("ALL TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(run_all())
