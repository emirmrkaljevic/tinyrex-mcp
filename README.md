# tinyrex-mcp

**Run [TinyRex](https://apify.com/tinyrex) Apify Store actors from any MCP-capable AI agent** (Claude Desktop, Cursor, and others) using **your own** `APIFY_TOKEN`.

This is a thin stdio [Model Context Protocol](https://modelcontextprotocol.io/) server: it lists the public TinyRex actors and starts a run, then returns dataset items (capped for MCP hosts).

> Actors are **pay-per-event (PPE)** on Apify. Failed or empty runs are often free under TinyRex pricing — check each actor’s Store page. You pay Apify with your own account; this MCP does not bill separately.

## Install

Python 3.11+:

```sh
pip install git+https://github.com/emirmrkaljevic/tinyrex-mcp.git
# or clone and:
# pip install -e .
```

Requires an [Apify API token](https://console.apify.com/settings/integrations) in the environment as `APIFY_TOKEN`.

## Claude Desktop / Cursor (`mcpServers`)

```json
{
  "mcpServers": {
    "tinyrex": {
      "command": "tinyrex-mcp",
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

If the script is not on `PATH`, use the module form:

```json
{
  "mcpServers": {
    "tinyrex": {
      "command": "python",
      "args": ["-m", "tinyrex_mcp"],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `list_actors` | Lists all **17 public** TinyRex actors (name, title, description, Store URL, example input). |
| `run_actor` | Runs `tinyrex/<name>` with an `input` object, waits for the run, returns dataset items (default max 50) plus `itemCount`, `runId`, and status. |

### Example: LEI lookup

1. `list_actors` → find `gleif-lei-lookup`
2. `run_actor` with:

```json
{
  "actor": "gleif-lei-lookup",
  "input": { "companyNames": ["Siemens AG"], "maxResultsPerName": 1 },
  "max_items": 5
}
```

## Public actors wrapped

| Actor | Store |
|---|---|
| tech-stack-detector | [apify.com/tinyrex/tech-stack-detector](https://apify.com/tinyrex/tech-stack-detector) |
| ats-jobs-scraper | [apify.com/tinyrex/ats-jobs-scraper](https://apify.com/tinyrex/ats-jobs-scraper) |
| shopify-products-scraper | [apify.com/tinyrex/shopify-products-scraper](https://apify.com/tinyrex/shopify-products-scraper) |
| workday-jobs-scraper | [apify.com/tinyrex/workday-jobs-scraper](https://apify.com/tinyrex/workday-jobs-scraper) |
| woocommerce-products-scraper | [apify.com/tinyrex/woocommerce-products-scraper](https://apify.com/tinyrex/woocommerce-products-scraper) |
| ted-tenders-scraper | [apify.com/tinyrex/ted-tenders-scraper](https://apify.com/tinyrex/ted-tenders-scraper) |
| eu-grants-scraper | [apify.com/tinyrex/eu-grants-scraper](https://apify.com/tinyrex/eu-grants-scraper) |
| remote-jobs-scraper | [apify.com/tinyrex/remote-jobs-scraper](https://apify.com/tinyrex/remote-jobs-scraper) |
| rss-feed-scraper | [apify.com/tinyrex/rss-feed-scraper](https://apify.com/tinyrex/rss-feed-scraper) |
| sitemap-scraper | [apify.com/tinyrex/sitemap-scraper](https://apify.com/tinyrex/sitemap-scraper) |
| contact-details-extractor | [apify.com/tinyrex/contact-details-extractor](https://apify.com/tinyrex/contact-details-extractor) |
| us-uk-tenders-scraper | [apify.com/tinyrex/us-uk-tenders-scraper](https://apify.com/tinyrex/us-uk-tenders-scraper) |
| tenderned-tenders-scraper | [apify.com/tinyrex/tenderned-tenders-scraper](https://apify.com/tinyrex/tenderned-tenders-scraper) |
| seo-on-page-audit | [apify.com/tinyrex/seo-on-page-audit](https://apify.com/tinyrex/seo-on-page-audit) |
| broken-link-checker | [apify.com/tinyrex/broken-link-checker](https://apify.com/tinyrex/broken-link-checker) |
| gleif-lei-lookup | [apify.com/tinyrex/gleif-lei-lookup](https://apify.com/tinyrex/gleif-lei-lookup) |
| uk-companies-house-lookup | [apify.com/tinyrex/uk-companies-house-lookup](https://apify.com/tinyrex/uk-companies-house-lookup) |

Private / ToS-blocked actors are **not** exposed.

## Docker (stdio)

```sh
docker build -t tinyrex-mcp .
docker run --rm -i -e APIFY_TOKEN=YOUR_APIFY_TOKEN tinyrex-mcp
```

## Development

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e .
APIFY_TOKEN=... tinyrex-mcp   # stdio MCP
```

Smoke-test helpers (list tools + one cheap run) live in `scripts/smoke_test.py`.

## License

MIT. Brand: **TinyRex**. Store username: [tinyrex](https://apify.com/tinyrex).
