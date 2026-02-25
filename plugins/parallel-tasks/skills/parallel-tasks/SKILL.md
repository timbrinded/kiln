---
name: parallel-tasks
description: >
  This skill should be used when the user asks to "run a web research task",
  "enrich data", "look up company information", "competitive research",
  "batch process entities", "check task status", "use the Parallel API",
  "deep research", "find current information about", "enrich this list",
  "get citations for", "research this topic", "data enrichment pipeline",
  "run a batch of lookups", or needs to programmatically gather, verify,
  or enrich information from the web using the Parallel.ai Task API.
  Provides HTTP/curl-first guidance for all 18 processor tiers, async patterns,
  output schemas with basis citations, task groups, and source policies.
version: 0.1.0
---

# Parallel.ai Task API

HTTP/curl-first guide — no SDK required. All examples use `curl` + `jq`.

**Base URL:** `https://api.parallel.ai`

## Authentication

Every request requires the `x-api-key` header. Check for the API key:

```bash
echo ${PARALLEL_API_KEY:?"Set PARALLEL_API_KEY environment variable"}
```

Read `.claude/parallel-tasks.local.md` if it exists for overrides (see Settings below).

## Operational Modes

### Research Mode

Natural language query → choose processor → create run → get result.

1. Determine query complexity → select processor (see Quick Processor Table)
2. Create task run:
```bash
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"processor":"core","input":"What are the key competitive advantages of Stripe vs Square in 2025?"}' \
  | jq -r '.run_id')
```
3. Get result (blocks until complete):
```bash
curl -s https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/result \
  -H "x-api-key: ${PARALLEL_API_KEY}" | jq '.output'
```
4. Present result with basis citation summary

### Enrichment Mode

Structured input + output schema → create run → get enriched data.

1. Define JSON Schema for output fields (load `references/output-schemas-and-basis.md`)
2. Create task run with `task_spec` containing `output_schema` and optionally `input_schema`
3. Pass structured input as JSON object
4. Retrieve result — output conforms to schema, `basis` array provides per-field citations
5. Summarize confidence levels from basis

### Batch Mode

List of items → create task group → add runs → monitor → retrieve.

1. Load `references/task-groups.md` for group API
2. Create task group with shared `task_spec` and `processor`
3. Add runs in batches of up to 1,000 per POST
4. Stream group events or poll for completion
5. Retrieve and present results

### Monitoring Mode

Check status, get results, or stream events for existing runs/groups.

- **Status check:** `GET /v1/tasks/runs/{run_id}` → returns `status` field
- **Get result:** `GET /v1/tasks/runs/{run_id}/result` → blocks until complete
- **Stream events:** `GET /v1/tasks/runs/{run_id}/events` → SSE stream (load `references/async-patterns.md`)
- **Group status:** `GET /v1beta/tasks/groups/{taskgroup_id}` → group-level status

## Quick Processor Table

| Processor | $/1000 | Latency | Use When |
|-----------|--------|---------|----------|
| `lite` | 5 | 10s–60s | Simple fact lookups, validation |
| `base` | 10 | 15s–100s | Standard enrichments |
| `core` | 25 | 1–5min | Cross-referenced research |
| `pro` | 100 | 2–10min | Exploratory web research |
| `ultra` | 300 | 5–25min | Multi-source deep research |
| `ultra8x` | 2400 | 5min–2hr | Most difficult deep research |

All 9 processors have `-fast` variants (same price, lower latency). Full table in `references/processor-guide.md`.

## Decision Tree — Which Reference to Load

| Situation | Load |
|-----------|------|
| Need full endpoint details or curl syntax | `references/api-reference.md` |
| Choosing a processor tier or chaining processors | `references/processor-guide.md` |
| Handling long-running tasks, polling, SSE, webhooks | `references/async-patterns.md` |
| Building output schemas or understanding citations | `references/output-schemas-and-basis.md` |
| Processing a list of items in batch | `references/task-groups.md` |
| Source filtering, context reuse, metadata, MCP, beta features | `references/source-policies-and-advanced.md` |

## Settings

Read settings from `.claude/parallel-tasks.local.md` if present:

```yaml
---
default-processor: base
api-key-env: PARALLEL_API_KEY
---
```

**default-processor** (default: `base`): Processor used when not specified. Override per-request.

**api-key-env** (default: `PARALLEL_API_KEY`): Environment variable name holding the API key.

## Reference Files

| File | Contents | Words |
|------|----------|-------|
| `references/api-reference.md` | Complete endpoint catalog with curl examples | ~1200 |
| `references/processor-guide.md` | 18 processor tiers, decision framework, chaining | ~1200 |
| `references/async-patterns.md` | Blocking, polling, SSE, webhooks with curl | ~1200 |
| `references/output-schemas-and-basis.md` | Schema types, task specs, Basis citations | ~1200 |
| `references/task-groups.md` | Batch processing lifecycle, group endpoints | ~1200 |
| `references/source-policies-and-advanced.md` | Source policies, context reuse, metadata, MCP, beta headers | ~1200 |
