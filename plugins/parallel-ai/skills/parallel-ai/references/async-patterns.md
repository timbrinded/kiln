# Async Patterns for the Parallel.ai Task API

When you submit a task to the Parallel.ai API, execution is asynchronous by default. The API offers several patterns for retrieving results, ranging from a simple blocking call to full webhook delivery. This guide covers each pattern, when to use it, and how to implement it.

---

## Task Lifecycle

Every task run moves through a defined sequence of states:

```
queued → running → completed
                 → failed
                 → cancelled
```

Two additional transitional states exist:

- `action_required` — the task is paused and waiting for user input before it can proceed
- `cancelling` — a cancellation has been requested but has not yet taken effect

The field `is_active` is `true` when the status is `queued`, `running`, or `cancelling`. Use this field as a simple active-check when polling, rather than enumerating every active state manually.

---

## Pattern 1: Blocking Result Call

The simplest way to get output. After creating a task run, call the `/result` endpoint immediately. This endpoint blocks the HTTP connection until the task completes (or fails), then returns the final output in a single response.

```bash
# Step 1: Create the task run
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"processor":"base","input":"What is the market cap of Apple?"}' \
  | jq -r '.run_id')

# Step 2: Block until result is ready
curl -s https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/result \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  | jq '.output'
```

No polling loop, no reconnect logic, no state management. The trade-off is that the HTTP connection stays open for the duration of the task. For short-lived tasks this is fine; for longer-running tasks it becomes fragile.

**Best for:** `lite` and `base` processors, interactive CLI usage, quick one-off lookups where simplicity matters more than resilience.

---

## Pattern 2: Polling

Create the task, then repeatedly check the run status until it reaches a terminal state (`completed`, `failed`, or `cancelled`). Once complete, fetch the result separately.

```bash
# Step 1: Create the task run
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"processor":"pro","input":"Summarise the latest 10-K filing for Microsoft."}' \
  | jq -r '.run_id')

# Step 2: Poll until terminal state
while true; do
  STATUS=$(curl -s https://api.parallel.ai/v1/tasks/runs/${RUN_ID} \
    -H "x-api-key: ${PARALLEL_API_KEY}" \
    | jq -r '.status')

  case $STATUS in
    completed)
      break
      ;;
    failed|cancelled)
      echo "Task ended with status: $STATUS"
      exit 1
      ;;
    *)
      echo "Status: $STATUS — waiting..."
      sleep 5
      ;;
  esac
done

# Step 3: Fetch the result
curl -s https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/result \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  | jq '.output'
```

Polling is more resilient than blocking because each HTTP call is short-lived. If your script restarts mid-way, you can resume polling from a stored `run_id`. The `is_active` field on the run object can be used as a simpler loop condition if you prefer it over matching individual status strings.

**Best for:** `pro` and above processors, batch scripts running over many tasks, situations where you want intermediate status updates logged to a terminal.

---

## Pattern 3: SSE Streaming (Beta)

Server-Sent Events (SSE) let you receive real-time progress updates as a task runs. You opt in at creation time by passing `enable_events: true` and the beta header. A separate `/events` endpoint then streams structured events as the task progresses.

This feature is currently in beta and requires the `parallel-beta: events-sse-2025-07-24` header on both the creation request and the streaming request.

```bash
# Step 1: Create the task run with events enabled
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "parallel-beta: events-sse-2025-07-24" \
  -d '{"processor":"ultra","input":"Conduct a deep competitive analysis of the EV battery market.","enable_events":true}' \
  | jq -r '.run_id')

# Step 2: Stream events until the task completes
curl -s --no-buffer "https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/events" \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: events-sse-2025-07-24"
```

### Event Types

| Event Type | Description |
|---|---|
| `task_run.progress_msg.plan` | Narrative update about the current step in the task plan |
| `task_run.progress_stats` | Numeric progress data: completion percentage (0–100) and source statistics |

The `task_run.progress_stats` events carry a completion percentage that can be surfaced directly in a progress bar or status display.

### Reconnection

If the SSE connection drops, resume from where you left off using the `last_event_id` query parameter:

```bash
curl -s --no-buffer \
  "https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/events?last_event_id=<last_seen_id>" \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "parallel-beta: events-sse-2025-07-24"
```

The server will replay events from that point forward, so you do not miss progress updates after a reconnect.

**Best for:** `ultra` and above processors, applications that display real-time progress to end users, any context where a 10+ minute task needs visible feedback rather than a silent wait.

---

## Pattern 4: Webhooks (Beta)

Webhooks decouple task submission from result handling entirely. You register a URL at task creation time; when the task reaches a terminal state, the Parallel.ai platform POSTs the result payload directly to your endpoint. Your submission code does not wait for anything.

This feature is currently in beta and requires the `parallel-beta: webhook-2025-08-12` header.

```bash
curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "parallel-beta: webhook-2025-08-12" \
  -d '{
    "processor": "pro",
    "input": "What were the key macroeconomic events of Q1 2025?",
    "webhook_url": "https://your-server.example.com/hooks/parallel"
  }'
```

The webhook payload includes the run status and the task output. To verify that the payload genuinely came from Parallel.ai, validate the HMAC signature using the webhook secret provided when you configured your endpoint.

**Best for:** server-to-server integrations, fire-and-forget pipelines, production systems that process results asynchronously (e.g., writing to a database, triggering a downstream workflow), any scenario where you cannot keep a long-lived HTTP connection open.

---

## Choosing a Pattern

| Pattern | Best For | Latency Tolerance | Complexity |
|---------|----------|-------------------|------------|
| Blocking | `lite`/`base`, interactive CLI | Under 2 minutes | Minimal |
| Polling | `pro`, batch scripts | 2–10 minutes | Low |
| SSE Streaming | `ultra`+, real-time progress display | 10 minutes+ | Medium |
| Webhooks | Production pipelines, server-to-server | Any | Higher (requires a server) |

When in doubt, start with the blocking pattern. Migrate to polling if connection stability becomes an issue. Add SSE if your users need to see progress. Reach for webhooks when you are building a production pipeline and cannot tolerate open connections.
