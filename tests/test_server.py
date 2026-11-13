"""Offline unit tests for tinyrex-mcp (no APIFY_TOKEN or network required)."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from tinyrex_mcp.server import (
    _actor_by_name,
    _cap_items,
    _client,
    _load_actors,
    list_actors,
    run_actor,
)


def _callable(tool):
    """FastMCP may wrap the function; prefer the original callable."""
    return getattr(tool, "fn", getattr(tool, "__wrapped__", tool))


class ActorCatalogTests(unittest.TestCase):
    def test_catalog_has_unique_names_and_required_fields(self):
        actors = _load_actors()
        self.assertGreaterEqual(len(actors), 1)
        names = [a["name"] for a in actors]
        self.assertEqual(len(names), len(set(names)))
        required = ("name", "title", "description", "storeUrl", "exampleInput")
        for actor in actors:
            for key in required:
                self.assertIn(key, actor, msg=f"{actor.get('name')} missing {key}")
            self.assertTrue(actor["name"])
            self.assertTrue(str(actor["storeUrl"]).startswith("https://apify.com/tinyrex/"))
            self.assertIsInstance(actor["exampleInput"], dict)

    def test_actor_by_name_accepts_prefix_and_ignores_case(self):
        exact = _actor_by_name("gleif-lei-lookup")
        prefixed = _actor_by_name("tinyrex/gleif-lei-lookup")
        mixed = _actor_by_name("  TinyRex/GLEIF-LEI-LOOKUP  ")
        self.assertIsNotNone(exact)
        self.assertEqual(exact["name"], "gleif-lei-lookup")
        self.assertEqual(prefixed["name"], exact["name"])
        self.assertEqual(mixed["name"], exact["name"])

    def test_actor_by_name_unknown_returns_none(self):
        self.assertIsNone(_actor_by_name("not-a-real-actor"))
        self.assertIsNone(_actor_by_name("tinyrex/not-a-real-actor"))


class ListActorsTests(unittest.TestCase):
    def test_list_actors_matches_catalog(self):
        payload = json.loads(_callable(list_actors)())
        catalog = _load_actors()
        self.assertEqual(payload["username"], "tinyrex")
        self.assertEqual(payload["count"], len(catalog))
        self.assertEqual(len(payload["actors"]), len(catalog))
        listed = {a["name"] for a in payload["actors"]}
        self.assertEqual(listed, {a["name"] for a in catalog})
        sample = next(a for a in payload["actors"] if a["name"] == "remote-jobs-scraper")
        self.assertEqual(sample["fullName"], "tinyrex/remote-jobs-scraper")
        self.assertIn("exampleInput", sample)
        self.assertTrue(sample["storeUrl"].endswith("/remote-jobs-scraper"))


class CapItemsTests(unittest.TestCase):
    def test_caps_by_max_items_and_sets_truncated(self):
        items = [{"i": n} for n in range(10)]
        out = _cap_items(items, 3)
        self.assertEqual(out["itemCount"], 10)
        self.assertEqual(out["returnedCount"], 3)
        self.assertTrue(out["truncated"])
        self.assertEqual(out["items"], items[:3])

    def test_no_truncation_when_under_limit(self):
        items = [{"i": 1}, {"i": 2}]
        out = _cap_items(items, 50)
        self.assertEqual(out["itemCount"], 2)
        self.assertEqual(out["returnedCount"], 2)
        self.assertFalse(out["truncated"])
        self.assertEqual(out["items"], items)

    def test_caps_oversized_json_payload(self):
        # Each item is large enough that a handful already exceed the 120k cap.
        items = [{"blob": "x" * 40_000, "n": n} for n in range(8)]
        out = _cap_items(items, 8)
        self.assertEqual(out["itemCount"], 8)
        self.assertLess(out["returnedCount"], 8)
        self.assertTrue(out["truncated"])
        payload = json.dumps(out["items"], ensure_ascii=False, default=str)
        self.assertLessEqual(len(payload), 120_000)


class ClientAndValidationTests(unittest.TestCase):
    def test_client_requires_token(self):
        env = {k: v for k, v in os.environ.items() if k != "APIFY_TOKEN"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                _client()
        self.assertIn("APIFY_TOKEN", str(ctx.exception))
        self.assertNotIn("apify_api_", str(ctx.exception).lower())

    def test_run_actor_rejects_unknown_actor(self):
        with self.assertRaises(ValueError) as ctx:
            _callable(run_actor)(actor="definitely-not-an-actor", input={})
        self.assertIn("Unknown actor", str(ctx.exception))

    def test_run_actor_rejects_bad_limits_and_input_type(self):
        fn = _callable(run_actor)
        with self.assertRaises(ValueError) as ctx:
            fn(actor="gleif-lei-lookup", input={}, max_items=0)
        self.assertIn("max_items", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            fn(actor="gleif-lei-lookup", input={}, timeout_secs=5)
        self.assertIn("timeout_secs", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            fn(actor="gleif-lei-lookup", input=["not", "an", "object"])
        self.assertIn("input must be a JSON object", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
