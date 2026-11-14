# tinyrex-mcp

[![Listed on mcpservers.org](https://img.shields.io/badge/mcpservers.org-listed-blue)](https://mcpservers.org/servers/emirmrkaljevic/tinyrex-mcp)

<a href="https://launchigniter.com/product/tinyrex-mcp?ref=badge-tinyrex-mcp" target="_blank"><img src="https://launchigniter.com/api/badge/tinyrex-mcp?theme=light" alt="Featured on LaunchIgniter" width="212" height="55" /></a>

**Run [TinyRex](https://apify.com/tinyrex) Apify Store actors from Claude Desktop, Cursor, and other MCP hosts**, using **your own** `APIFY_TOKEN`.

This is a thin stdio [Model Context Protocol](https://modelcontextprotocol.io/) server: it lists the public TinyRex actors and starts a run, then returns dataset items (capped for MCP hosts).

> Actors are **pay-per-event (PPE)** on Apify. Failed or empty runs are often free under TinyRex pricing: check each actor's Store page. You pay Apify with your own account; this MCP does not bill separately.

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
| `list_actors` | Lists all **27 public** TinyRex actors (name, title, description, Store URL, example input). |
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

More prompt-to-tool-call examples are in [docs/examples.md](docs/examples.md).

## Public actors wrapped

`list_actors` returns all 27 public TinyRex actors. Store pages:

- [tech-stack-detector](https://apify.com/tinyrex/tech-stack-detector)
- [ats-jobs-scraper](https://apify.com/tinyrex/ats-jobs-scraper)
- [shopify-products-scraper](https://apify.com/tinyrex/shopify-products-scraper)
- [workday-jobs-scraper](https://apify.com/tinyrex/workday-jobs-scraper)
- [woocommerce-products-scraper](https://apify.com/tinyrex/woocommerce-products-scraper)
- [ted-tenders-scraper](https://apify.com/tinyrex/ted-tenders-scraper)
- [eu-grants-scraper](https://apify.com/tinyrex/eu-grants-scraper)
- [remote-jobs-scraper](https://apify.com/tinyrex/remote-jobs-scraper)
- [rss-feed-scraper](https://apify.com/tinyrex/rss-feed-scraper)
- [sitemap-scraper](https://apify.com/tinyrex/sitemap-scraper)
- [contact-details-extractor](https://apify.com/tinyrex/contact-details-extractor)
- [us-uk-tenders-scraper](https://apify.com/tinyrex/us-uk-tenders-scraper)
- [tenderned-tenders-scraper](https://apify.com/tinyrex/tenderned-tenders-scraper)
- [seo-on-page-audit](https://apify.com/tinyrex/seo-on-page-audit)
- [broken-link-checker](https://apify.com/tinyrex/broken-link-checker)
- [gleif-lei-lookup](https://apify.com/tinyrex/gleif-lei-lookup)
- [uk-companies-house-lookup](https://apify.com/tinyrex/uk-companies-house-lookup)
- [bulk-website-screenshot](https://apify.com/tinyrex/bulk-website-screenshot)
- [bulk-email-validator](https://apify.com/tinyrex/bulk-email-validator)
- [pdf-ocr-text-extractor](https://apify.com/tinyrex/pdf-ocr-text-extractor)
- [npi-registry-lookup](https://apify.com/tinyrex/npi-registry-lookup)
- [lighthouse-audit](https://apify.com/tinyrex/lighthouse-audit)
- [sec-edgar-filings-scraper](https://apify.com/tinyrex/sec-edgar-filings-scraper)
- [france-company-search](https://apify.com/tinyrex/france-company-search)
- [norway-company-search](https://apify.com/tinyrex/norway-company-search)
- [finland-company-search](https://apify.com/tinyrex/finland-company-search)
- [audio-video-transcriber](https://apify.com/tinyrex/audio-video-transcriber)

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

Unit tests that do not need an Apify token: `python -m unittest discover -s tests`.
The same suite runs on Python 3.11, 3.12 and 3.13 in GitHub Actions on every push and pull request.

Smoke-test helpers (list tools + one cheap run, needs `APIFY_TOKEN`) live in `scripts/smoke_test.py`.

## License

MIT. Brand: **TinyRex**. Store username: [tinyrex](https://apify.com/tinyrex).
