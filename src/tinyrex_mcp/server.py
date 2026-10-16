"""Stdio MCP server that runs TinyRex Apify Store actors via APIFY_TOKEN."""

from __future__ import annotations

import json
import os
from importlib import resources
from typing import Any

from apify_client import ApifyClient
from mcp.server.fastmcp import FastMCP

DEFAULT_MAX_ITEMS = 50
DEFAULT_TIMEOUT_SECS = 180
USERNAME = "tinyrex"

mcp = FastMCP(
    "tinyrex-mcp",
    instructions=(
        "Run TinyRex scrapers and lookups on the Apify Store. "
        "Call list_actors to see available actors, then run_actor with an actor "
        "name and input. Requires env APIFY_TOKEN (user's own Apify API token). "
        "Actors are pay-per-event on Apify; failed or empty runs are often free "
        "per TinyRex pricing."
    ),
)


def _load_actors() -> list[dict[str, Any]]:
    raw = resources.files("tinyrex_mcp").joinpath("actors.json").read_text(encoding="utf-8")
    return json.loads(raw)


def _actor_by_name(name: str) -> dict[str, Any] | None:
    key = name.strip().lower()
    if key.startswith(f"{USERNAME}/"):
        key = key.split("/", 1)[1]
    for actor in _load_actors():
        if actor["name"] == key:
            return actor
    return None


def _client() -> ApifyClient:
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "APIFY_TOKEN is not set. Create a token at https://console.apify.com/settings/integrations "
            "and set it in the MCP server env (see README)."
        )
    return ApifyClient(token)


def _cap_items(items: list[Any], max_items: int) -> dict[str, Any]:
    total = len(items)
    capped = items[: max(0, max_items)]
    # Keep JSON payload reasonable for MCP hosts
    text = json.dumps(capped, ensure_ascii=False, default=str)
    truncated_payload = False
    if len(text) > 120_000:
        while capped and len(json.dumps(capped, ensure_ascii=False, default=str)) > 120_000:
            capped = capped[:- max(1, len(capped) // 5)]
        truncated_payload = True
        text = json.dumps(capped, ensure_ascii=False, default=str)
    return {
        "itemCount": total,
        "returnedCount": len(capped),
        "truncated": total > len(capped) or truncated_payload,
        "items": capped,
    }


@mcp.tool()
def list_actors() -> str:
    """List all public TinyRex Apify Store actors this MCP can run.

    Returns name, title, short description, Store URL, and an example input
    for each actor. Private / ToS-blocked actors are not included.
    """
    actors = _load_actors()
    payload = {
        "username": USERNAME,
        "count": len(actors),
        "actors": [
            {
                "name": a["name"],
                "fullName": f"{USERNAME}/{a['name']}",
                "title": a["title"],
                "description": a["description"],
                "storeUrl": a["storeUrl"],
                "exampleInput": a.get("exampleInput"),
            }
            for a in actors
        ],
        "note": (
            "Pass actor name (e.g. gleif-lei-lookup) or tinyrex/<name> to run_actor. "
            "Actors are paid PPE on Apify; failed/empty runs are often free per TinyRex pricing."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.tool()
def run_actor(
    actor: str,
    input: dict[str, Any] | None = None,
    max_items: int = DEFAULT_MAX_ITEMS,
    timeout_secs: int = DEFAULT_TIMEOUT_SECS,
    memory_mbytes: int | None = None,
) -> str:
    """Run a TinyRex Apify actor and return dataset items.

    Args:
        actor: Actor name (e.g. "gleif-lei-lookup") or "tinyrex/<name>".
        input: Actor input object (same fields as on the Apify Store). Use
            list_actors exampleInput as a starting point.
        max_items: Max dataset items to return (default 50). Total count is
            always included.
        timeout_secs: How long to wait for the run to finish (default 180).
        memory_mbytes: Optional memory override for the run (Apify default if omitted).
    """
    meta = _actor_by_name(actor)
    if meta is None:
        known = ", ".join(a["name"] for a in _load_actors())
        raise ValueError(f"Unknown actor {actor!r}. Known: {known}")

    if max_items < 1:
        raise ValueError("max_items must be >= 1")
    if timeout_secs < 10:
        raise ValueError("timeout_secs must be >= 10")

    run_input = input if input is not None else {}
    if not isinstance(run_input, dict):
        raise ValueError("input must be a JSON object")

    full_name = f"{USERNAME}/{meta['name']}"
    client = _client()
    run_kwargs: dict[str, Any] = {
        "run_input": run_input,
        "wait_secs": timeout_secs,
    }
    if memory_mbytes is not None:
        run_kwargs["memory_mbytes"] = memory_mbytes

    run = client.actor(full_name).call(**run_kwargs)
    if run is None:
        raise RuntimeError(f"Actor {full_name} returned no run (timed out or failed to start)")

    run_id = run.get("id")
    status = run.get("status")
    dataset_id = run.get("defaultDatasetId")
    usage = run.get("usageTotalUsd")

    items: list[Any] = []
    if dataset_id:
        items = list(client.dataset(dataset_id).iterate_items())

    capped = _cap_items(items, max_items)
    result = {
        "actor": full_name,
        "storeUrl": meta["storeUrl"],
        "runId": run_id,
        "status": status,
        "usageTotalUsd": usage,
        "datasetId": dataset_id,
        "consoleUrl": f"https://console.apify.com/actors/runs/{run_id}" if run_id else None,
        **capped,
    }
    if status not in ("SUCCEEDED", "SUCCEEDED_WITH_WARNINGS"):
        result["warning"] = (
            f"Run finished with status {status}. Items may be partial or empty. "
            "Failed/empty TinyRex runs are often free under PPE pricing."
        )
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
