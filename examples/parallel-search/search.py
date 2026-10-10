"""Search and optionally fetch a page through Poirot's MCP loader, without an LLM."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from uuid import uuid4

from poirot.backend.agents.mcp import build_mcp_manager


async def run(objective: str, queries: list[str], urls: list[str]) -> None:
    config_path = Path(__file__).with_name("mcp_servers.yaml")
    manager = build_mcp_manager(str(config_path))
    if manager is None:
        raise RuntimeError("Set POIROT_MCP_ENABLED=true to enable the example.")
    session_id = str(uuid4())
    try:
        await manager.load_startup()
        tools = {tool.name: tool for tool in manager.get_tools(["core"])}
        if "web_search" not in tools or (urls and "web_fetch" not in tools):
            raise RuntimeError("Parallel tools could not be loaded; check the MCP startup log.")
        search = await asyncio.wait_for(
            tools["web_search"].ainvoke({
                "objective": objective,
                "search_queries": queries,
                "session_id": session_id,
            }),
            timeout=300,
        )
        print(json.dumps({"web_search": search}, ensure_ascii=False), flush=True)
        if urls:
            fetch = await asyncio.wait_for(
                tools["web_fetch"].ainvoke({
                    "urls": urls,
                    "objective": objective[:200],
                    "search_queries": queries,
                    "session_id": session_id,
                }),
                timeout=300,
            )
            print(json.dumps({"web_fetch": fetch}, ensure_ascii=False), flush=True)
    finally:
        await manager.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("objective", help="What information to find")
    parser.add_argument("--query", action="append", required=True, help="Search keywords; repeat for related queries")
    parser.add_argument("--url", action="append", default=[], help="Specific page to fetch; repeat for related pages")
    args = parser.parse_args()
    asyncio.run(run(args.objective, args.query, args.url))


if __name__ == "__main__":
    main()
