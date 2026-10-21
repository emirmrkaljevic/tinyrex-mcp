#!/usr/bin/env python3
"""Local smoke test: list_tools + one cheap gleif run via MCP stdio client."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> int:
    if not os.environ.get("APIFY_TOKEN"):
        print("APIFY_TOKEN not set", file=sys.stderr)
        return 1

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "tinyrex_mcp"],
        env={**os.environ},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("tools:", names)
            assert "list_actors" in names and "run_actor" in names

            listed = await session.call_tool("list_actors", {})
            text = listed.content[0].text  # type: ignore[union-attr]
            data = json.loads(text)
            print("actor_count:", data["count"])
            assert data["count"] == 22

            result = await session.call_tool(
                "run_actor",
                {
                    "actor": "gleif-lei-lookup",
                    "input": {
                        "companyNames": ["Siemens AG"],
                        "maxResultsPerName": 1,
                        "includeParents": False,
                    },
                    "max_items": 5,
                    "timeout_secs": 120,
                },
            )
            out = json.loads(result.content[0].text)  # type: ignore[union-attr]
            print("runId:", out.get("runId"))
            print("status:", out.get("status"))
            print("itemCount:", out.get("itemCount"))
            print("returnedCount:", out.get("returnedCount"))
            if out.get("status") not in ("SUCCEEDED", "SUCCEEDED_WITH_WARNINGS"):
                print("warning:", out.get("warning"))
                return 2
            if out.get("itemCount", 0) < 1:
                print("expected at least 1 dataset item", file=sys.stderr)
                return 3
            print("smoke OK")
            return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
