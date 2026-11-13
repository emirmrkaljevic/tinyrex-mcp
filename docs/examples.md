# Example prompts

Once [tinyrex-mcp](https://github.com/emirmrkaljevic/tinyrex-mcp) is set up in Claude Desktop or Cursor, you can type a request like the ones below. Each example shows the `run_actor` call that should follow. If you do not already know the actor name, call `list_actors` first; it returns every public TinyRex actor with an `exampleInput`.

Actors run on your Apify account (`APIFY_TOKEN`). They are pay-per-event; failed or empty TinyRex runs are often free. Keep `max_items` small while you try a new actor.

## Recent remote Python jobs

Prompt: "Find 10 recent remote Python jobs from Himalayas and Remote OK."

`run_actor` arguments:

```json
{
  "actor": "remote-jobs-scraper",
  "input": {
    "keywords": ["python"],
    "sources": ["himalayas", "remoteok"],
    "maxResultsPerSearch": 10
  },
  "max_items": 20
}
```

## Products from a Shopify store

Prompt: "Export the first 10 products from deathwishcoffee.com, including prices, variants and SKUs."

`run_actor` arguments:

```json
{
  "actor": "shopify-products-scraper",
  "input": {
    "stores": ["deathwishcoffee.com"],
    "maxProductsPerStore": 10
  },
  "max_items": 10
}
```

## Latest SEC filings for two tickers

Prompt: "Get the latest 10-K and 8-K filings for Apple and Tesla."

`run_actor` arguments:

```json
{
  "actor": "sec-edgar-filings-scraper",
  "input": {
    "companies": ["AAPL", "TSLA"],
    "formTypes": ["10-K", "8-K"],
    "maxFilingsPerCompany": 5
  },
  "max_items": 10
}
```

The `input` object uses the same fields as the actor's Apify Store page. `list_actors` includes a starter `exampleInput` for each one.
