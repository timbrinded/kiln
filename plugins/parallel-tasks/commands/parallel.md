---
description: Run web research, data enrichment, batch tasks, web search, URL extraction, or check status via the Parallel.ai APIs
argument-hint: "<mode> [args] — modes: research, enrich, batch, search, extract, status, result, stream"
allowed-tools: Read, Bash, Grep, Glob
---

Execute Parallel.ai Task API operations using the parallel-tasks skill.

**Check prerequisites first:**
1. Verify `PARALLEL_API_KEY` is set: `echo ${PARALLEL_API_KEY:?"Set PARALLEL_API_KEY"}`
2. Read `.claude/parallel-tasks.local.md` if it exists for default processor and API key env var overrides

**Route by first argument:**

### `research` — Web research query
`/parallel research "What are the main competitors to Figma?" --processor core`

1. Parse query from `$1` and optional `--processor` flag (default from settings or `base`)
2. Load the parallel-tasks skill
3. Create task run with the query as `input` and selected processor
4. Get result using blocking `/result` endpoint for lite/base/core, or polling for pro+
5. Display the output text/JSON
6. Summarize basis citations: list sources with confidence levels

### `enrich` — Structured data enrichment
`/parallel enrich '{"company":"Stripe"}' --schema output-schema.json`

1. Parse JSON input from `$1` and optional `--schema` flag (path to JSON Schema file)
2. Load skill, then load `references/output-schemas-and-basis.md` for schema guidance
3. If `--schema` provided, read the file and use as `task_spec.output_schema`
4. If no schema, prompt user for desired output fields or use text output schema
5. Create task run with JSON object input and task_spec
6. Retrieve result and display structured output with per-field confidence

### `batch` — Batch process a list of items
`/parallel batch items.json --processor base`

1. Parse items file path from `$1` and optional `--processor` flag
2. Load skill, then load `references/task-groups.md` for group API
3. Read the items file (JSON array)
4. Create task group with shared processor and task_spec
5. Add runs in batches of up to 1,000
6. Stream group events, displaying results as they complete
7. Summarize: total items, completed, failed, sample results

### `search` — Web search
`/parallel search "Recent AI infrastructure funding rounds" --mode one-shot --max-results 5`

1. Parse objective from `$1`, optional `--mode` (default: `one-shot`), optional `--max-results` (default: 10)
2. Load the parallel-tasks skill, then load `references/search-and-extract.md`
3. Build request body with `objective`, `mode`, and `max_results`
4. POST to `/v1beta/search` with both `x-api-key` and `parallel-beta: search-extract-2025-10-10` headers
5. Display results: URL, title, publish date, and excerpts

### `extract` — Extract content from URLs
`/parallel extract "https://example.com/page1 https://example.com/page2" --objective "Key features" --full-content`

Also supports reading URLs from a file:
`/parallel extract urls.txt --objective "Pricing details"`

1. Parse URLs from `$1` — either space-separated inline or a file path (one URL per line)
2. Load the parallel-tasks skill, then load `references/search-and-extract.md`
3. Build request body with `urls`, optional `--objective`, and `--full-content` flag
4. POST to `/v1beta/extract` with both `x-api-key` and `parallel-beta: search-extract-2025-10-10` headers
5. Display results per URL; report any entries from the `errors` array

### `status` — Check run status
`/parallel status trun_9907962f83aa4d9d98fd7f4bf745d654`

1. Parse run_id from `$1`
2. `GET /v1/tasks/runs/{run_id}` to retrieve status
3. Display: status, processor, is_active, created_at, modified_at

### `result` — Get run result (blocks until complete)
`/parallel result trun_9907962f83aa4d9d98fd7f4bf745d654`

1. Parse run_id from `$1`
2. `GET /v1/tasks/runs/{run_id}/result` — blocks until completed
3. Display output content and basis citation summary

### `stream` — Stream SSE events for a run
`/parallel stream trun_9907962f83aa4d9d98fd7f4bf745d654`

1. Parse run_id from `$1`
2. Load `references/async-patterns.md` for SSE details
3. Stream events: `GET /v1/tasks/runs/{run_id}/events` with `--no-buffer`
4. Display progress messages and stats in real-time

### No arguments — Display help
`/parallel`

Display available modes with usage examples:
```
Parallel.ai APIs — Web research, enrichment, batch intelligence, search, and extraction

Usage:
  /parallel research "query" [--processor tier]       Run a web research task
  /parallel enrich '{"key":"val"}' [--schema file]    Enrich structured data
  /parallel batch items.json [--processor tier]        Batch process a list
  /parallel search "query" [--mode mode] [--max-results N]  Web search (sync)
  /parallel extract "url1 url2" [--objective "goal"]   Extract URL content (sync)
  /parallel status {run_id}                            Check task status
  /parallel result {run_id}                            Get task result
  /parallel stream {run_id}                            Stream task events

Processors: lite, base (default), core, pro, ultra, ultra2x, ultra4x, ultra8x
            Add -fast suffix for lower latency (e.g., base-fast)
Search modes: fast, one-shot (default), agentic

Requires: PARALLEL_API_KEY environment variable
```
