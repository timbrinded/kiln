# Search and Extract APIs

Parallel.ai's Search and Extract APIs are **synchronous** endpoints for web search and URL content extraction. Unlike the Task API, they return results directly — no run IDs, no polling, no async lifecycle.

> **Beta:** Both endpoints require the `parallel-beta: search-extract-2025-10-10` header in addition to `x-api-key`.

---

## Authentication

Every request requires **two** headers:

```bash
-H "x-api-key: ${PARALLEL_API_KEY}" \
-H "parallel-beta: search-extract-2025-10-10"
```

The beta header is mandatory — requests without it return `403`.

---

## Search API

**Endpoint:** `POST /v1beta/search`

Search the web and return URLs with excerpts. Synchronous — response in 1–3 seconds.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `objective` | string | Yes | What you're looking for |
| `search_queries` | array[string] | No | Specific search queries (auto-generated from objective if omitted) |
| `mode` | string | No | `one-shot` (default), `agentic`, or `fast` |
| `max_results` | integer | No | 1–20 (default: 10) |
| `source_policy` | object | No | `include_domains`, `exclude_domains`, `after_date` |
| `excerpts` | boolean\|object | No | Include excerpts in results (default: true) |
| `fetch_policy` | string | No | Controls how aggressively pages are fetched |

### Mode Comparison

| Mode | Latency | Behavior |
|------|---------|----------|
| `fast` | <1s | Single search pass, minimal processing |
| `one-shot` | 1–3s | Single search pass with result ranking and excerpts |
| `agentic` | 3–10s | Multiple search passes, refines queries based on initial results |

### Example

```bash
curl -s -X POST https://api.parallel.ai/v1beta/search \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Recent Series B funding rounds in AI infrastructure startups",
    "mode": "one-shot",
    "max_results": 5,
    "source_policy": {
      "after_date": "2025-01-01"
    }
  }' | jq '.results[] | {url, title, excerpts}'
```

### Response Schema

```json
{
  "search_id": "srch_abc123",
  "results": [
    {
      "url": "https://example.com/article",
      "title": "AI Startup Raises $50M Series B",
      "publish_date": "2025-06-15",
      "excerpts": [
        "The company announced a $50M Series B round led by..."
      ]
    }
  ],
  "warnings": [],
  "usage": {
    "requests": 1
  }
}
```

### Pricing

$5 per 1,000 requests. Rate limit: 600 requests/minute.

---

## Extract API

**Endpoint:** `POST /v1beta/extract`

Extract content from specific URLs. Synchronous — response in 1–20 seconds depending on page count.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | array[string] | Yes | URLs to extract content from |
| `objective` | string | No | Guides what to extract (improves relevance of excerpts) |
| `search_queries` | array[string] | No | Terms to highlight in excerpts |
| `fetch_policy` | string | No | Controls how aggressively pages are fetched |
| `excerpts` | boolean\|object | No | Return relevant excerpts (default: true) |
| `full_content` | boolean\|object | No | Return full page content (default: false) |

### Excerpts vs Full Content

- **`excerpts: true`** — Returns only the most relevant passages. Best for targeted questions about specific pages.
- **`full_content: true`** — Returns the complete page content. Best when you need everything from the page.
- Both can be enabled simultaneously. Use `excerpts` alone when you have a focused objective to minimize response size.

### Example

```bash
curl -s -X POST https://api.parallel.ai/v1beta/extract \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/blog/product-launch",
      "https://example.com/press/funding-announcement"
    ],
    "objective": "Key product features and funding details",
    "excerpts": true
  }' | jq '.results[] | {url, title, excerpts}'
```

### Response Schema

```json
{
  "extract_id": "extr_def456",
  "results": [
    {
      "url": "https://example.com/blog/product-launch",
      "title": "Introducing Our New Platform",
      "publish_date": "2025-05-20",
      "excerpts": [
        "The platform features real-time collaboration..."
      ],
      "full_content": null
    }
  ],
  "errors": [
    {
      "url": "https://example.com/404-page",
      "error": "fetch_failed",
      "message": "Page returned HTTP 404"
    }
  ],
  "warnings": [],
  "usage": {
    "urls": 2
  }
}
```

Note: URLs that fail to fetch appear in the `errors` array rather than `results`. Always check both arrays when processing responses.

### Pricing

$1 per 1,000 URLs extracted. Rate limit: 600 requests/minute.

---

## Combining Search + Extract

A common two-step pattern: search for relevant URLs, then extract their content.

```bash
# Step 1: Search for relevant pages
URLS=$(curl -s -X POST https://api.parallel.ai/v1beta/search \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Anthropic Claude pricing and capabilities",
    "mode": "one-shot",
    "max_results": 3
  }' | jq -r '[.results[].url]')

# Step 2: Extract content from those URLs
curl -s -X POST https://api.parallel.ai/v1beta/extract \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -H "Content-Type: application/json" \
  -d "{
    \"urls\": ${URLS},
    \"objective\": \"Pricing tiers and model capabilities\",
    \"excerpts\": true,
    \"full_content\": true
  }" | jq '.results[] | {url, title, excerpts}'
```

This pattern is ideal when you need more than just excerpts from search results — e.g., full page content for analysis, comparison, or summarization.

---

## Differences from the Task API

| | Search / Extract | Task API |
|---|---|---|
| **Execution** | Synchronous — response is the result | Asynchronous — returns run_id, poll for result |
| **Latency** | 1–20s | 10s–2hr depending on processor |
| **Endpoint prefix** | `/v1beta/search`, `/v1beta/extract` | `/v1/tasks/runs` |
| **Beta header** | `search-extract-2025-10-10` (required) | Feature-specific (optional) |
| **Processor selection** | N/A — no processor tiers | Required — 18 tiers from `lite` to `ultra8x` |
| **Run tracking** | No run_id, no status polling | Full lifecycle: queued → running → completed |
| **Output schemas** | Not supported | Supported via `task_spec` |
| **Pricing** | $5/1K searches, $1/1K extracts | $5–$2,400/1K runs by processor |
| **Best for** | Quick lookups, URL scraping | Deep research, enrichment, batch processing |

**When to use which:**
- **Search** when you need URLs and snippets fast — fact checks, link discovery, surface-level research.
- **Extract** when you already have URLs and need their content — scraping, content analysis, page comparison.
- **Task API** when you need deep research, structured output, citations, or batch processing.
