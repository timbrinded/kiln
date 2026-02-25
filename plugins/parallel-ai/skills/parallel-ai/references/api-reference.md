# Parallel.ai Task API Reference

## Authentication

All requests require an API key passed as a request header.

| Header | Value |
|--------|-------|
| `x-api-key` | `${PARALLEL_API_KEY}` |
| `Content-Type` | `application/json` |

**Base URL:** `https://api.parallel.ai`

---

## Task Runs (v1)

### POST /v1/tasks/runs

Create a new task run. The task is queued and executed asynchronously.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `processor` | string | Yes | The processor to use (e.g. `"base"`, `"research"`) |
| `input` | string \| object | Yes | The task input — a plain string or structured object |
| `task_spec` | object | No | Output schema or task constraints |
| `metadata` | object | No | Arbitrary key-value metadata attached to the run |
| `source_policy` | object | No | Controls which data sources the task may access |
| `previous_interaction_id` | string | No | Links this run to a prior interaction for context continuity |
| `mcp_servers` | array | No | MCP server configurations available to the task |

**Example**

```bash
curl -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "base",
    "input": "What is the market cap of Apple?",
    "task_spec": {
      "output_schema": {
        "json_schema": {
          "type": "object",
          "properties": {
            "market_cap": { "type": "string", "description": "Current market capitalization in USD" }
          },
          "required": ["market_cap"],
          "additionalProperties": false
        },
        "type": "json"
      }
    },
    "metadata": {
      "requested_by": "analyst-team"
    }
  }'
```

**Response**

```json
{
  "run_id": "trun_abc123",
  "interaction_id": "trun_abc123",
  "status": "queued",
  "is_active": true,
  "processor": "base",
  "metadata": {
    "requested_by": "analyst-team"
  },
  "created_at": "2025-07-24T10:00:00Z",
  "modified_at": "2025-07-24T10:00:00Z"
}
```

---

### GET /v1/tasks/runs/{run_id}

Retrieve the current status of a task run.

**Path Parameters**

| Parameter | Description |
|-----------|-------------|
| `run_id` | The run ID returned from the create endpoint (format: `trun_...`) |

**Example**

```bash
curl https://api.parallel.ai/v1/tasks/runs/trun_abc123 \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response**

```json
{
  "run_id": "trun_abc123",
  "interaction_id": "trun_abc123",
  "status": "running",
  "is_active": true,
  "processor": "base",
  "metadata": {},
  "created_at": "2025-07-24T10:00:00Z",
  "modified_at": "2025-07-24T10:00:05Z"
}
```

**Status Values**

| Status | Description |
|--------|-------------|
| `queued` | Task is waiting to be processed |
| `running` | Task is actively executing |
| `action_required` | Task is paused and requires external input |
| `completed` | Task finished successfully |
| `failed` | Task encountered an unrecoverable error |
| `cancelling` | Cancellation requested, in progress |
| `cancelled` | Task was cancelled |

---

### GET /v1/tasks/runs/{run_id}/result

Retrieve the result of a completed task run. This endpoint **blocks** until the task reaches a terminal state (`completed`, `failed`, or `cancelled`).

**Example**

```bash
curl https://api.parallel.ai/v1/tasks/runs/trun_abc123/result \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response**

```json
{
  "run": {
    "run_id": "trun_abc123",
    "interaction_id": "trun_abc123",
    "status": "completed",
    "is_active": false,
    "processor": "base",
    "metadata": {},
    "created_at": "2025-07-24T10:00:00Z",
    "modified_at": "2025-07-24T10:00:30Z"
  },
  "output": {
    "type": "json",
    "content": {
      "market_cap": "$3.2 trillion"
    },
    "basis": [
      {
        "url": "https://example.com/apple-financials",
        "title": "Apple Inc. Market Data",
        "excerpt": "Apple's market capitalization as of..."
      }
    ]
  }
}
```

**Output Fields**

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"json"` \| `"text"` | Format of the `content` field |
| `content` | object \| string | The task output, shaped by `task_spec.output_schema` if provided |
| `basis` | array | Source citations used to produce the output |

---

### GET /v1/tasks/runs/{run_id}/input

Retrieve the original request body that was used to create this task run.

**Example**

```bash
curl https://api.parallel.ai/v1/tasks/runs/trun_abc123/input \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response**

Returns the original task run request body as submitted to `POST /v1/tasks/runs`.

```json
{
  "processor": "base",
  "input": "What is the market cap of Apple?",
  "metadata": {
    "requested_by": "analyst-team"
  }
}
```

---

### GET /v1/tasks/runs/{run_id}/events

Stream real-time progress events for a task run via Server-Sent Events (SSE).

> **Beta:** Requires the `parallel-beta` header.

**Required Headers**

| Header | Value |
|--------|-------|
| `parallel-beta` | `events-sse-2025-07-24` |

**Example**

```bash
curl https://api.parallel.ai/v1/tasks/runs/trun_abc123/events \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: events-sse-2025-07-24" \
  --no-buffer
```

**Event Types**

| Event Type | Description |
|------------|-------------|
| `task_run.progress_msg.plan` | Step-by-step plan the task is following |
| `task_run.progress_stats` | Periodic stats (tokens used, elapsed time, etc.) |

Each event follows the SSE format:

```
event: task_run.progress_msg.plan
data: {"step": 1, "description": "Searching for Apple market cap data..."}

event: task_run.progress_stats
data: {"elapsed_seconds": 5, "tokens_used": 1200}
```

---

## Task Groups (v1beta)

Task groups allow batching up to 1,000 task runs and tracking them collectively. All group endpoints are in beta.

> **Beta:** These endpoints use the `/v1beta/` path prefix.

---

### POST /v1beta/tasks/groups

Create a new task group.

**Example**

```bash
curl -X POST https://api.parallel.ai/v1beta/tasks/groups \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "label": "Q4 research batch"
    }
  }'
```

**Response**

```json
{
  "taskgroup_id": "tgrp_xyz789",
  "status": "open",
  "metadata": {
    "label": "Q4 research batch"
  },
  "created_at": "2025-07-24T10:00:00Z"
}
```

---

### POST /v1beta/tasks/groups/{taskgroup_id}/runs

Add task runs to an existing group. Accepts up to **1,000 runs per request**.

**Example**

```bash
curl -X POST https://api.parallel.ai/v1beta/tasks/groups/tgrp_xyz789/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "runs": [
      { "processor": "base", "input": "Market cap of Apple?" },
      { "processor": "base", "input": "Market cap of Microsoft?" },
      { "processor": "base", "input": "Market cap of Google?" }
    ]
  }'
```

**Response**

```json
{
  "added": 3,
  "run_ids": ["trun_001", "trun_002", "trun_003"]
}
```

---

### GET /v1beta/tasks/groups/{taskgroup_id}

Retrieve the current status and summary of a task group.

**Example**

```bash
curl https://api.parallel.ai/v1beta/tasks/groups/tgrp_xyz789 \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response**

```json
{
  "taskgroup_id": "tgrp_xyz789",
  "status": "running",
  "metadata": {},
  "counts": {
    "total": 3,
    "queued": 0,
    "running": 2,
    "completed": 1,
    "failed": 0
  },
  "created_at": "2025-07-24T10:00:00Z",
  "modified_at": "2025-07-24T10:00:15Z"
}
```

---

### GET /v1beta/tasks/groups/{taskgroup_id}/runs

Fetch all task runs belonging to a group.

**Example**

```bash
curl https://api.parallel.ai/v1beta/tasks/groups/tgrp_xyz789/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response**

```json
{
  "runs": [
    {
      "run_id": "trun_001",
      "status": "completed",
      "is_active": false,
      "processor": "base",
      "created_at": "2025-07-24T10:00:01Z",
      "modified_at": "2025-07-24T10:00:28Z"
    }
  ]
}
```

---

### GET /v1beta/tasks/groups/{taskgroup_id}/events

Stream SSE events for all runs in a task group.

**Example**

```bash
curl https://api.parallel.ai/v1beta/tasks/groups/tgrp_xyz789/events \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: events-sse-2025-07-24" \
  --no-buffer
```

Events follow the same format as single-run SSE events but include a `run_id` field to identify which run the event belongs to.

---

## Search and Extract APIs

`POST /v1beta/search` and `POST /v1beta/extract` are synchronous endpoints covered in `references/search-and-extract.md`. Both require the `parallel-beta: search-extract-2025-10-10` header in addition to `x-api-key`.

---

## Common Objects

### TaskRun Object

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Unique run identifier (format: `trun_...`) |
| `interaction_id` | string | Groups related runs into a single interaction thread |
| `status` | string | Current lifecycle status (see status table above) |
| `is_active` | boolean | `true` if the run has not yet reached a terminal state |
| `processor` | string | The processor this run was assigned to |
| `metadata` | object | Arbitrary metadata as provided at creation |
| `created_at` | string | ISO 8601 timestamp of creation |
| `modified_at` | string | ISO 8601 timestamp of last status change |

### TaskRunOutput Object

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"json"` \| `"text"` | Indicates the format of `content` |
| `content` | object \| string | The task result |
| `basis` | array | Array of source citations (url, title, excerpt) |

### Status Lifecycle

```
queued → running → completed
                 → failed
                 → cancelling → cancelled
       → action_required → running
```
