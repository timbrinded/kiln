# Task Groups — Batch Processing with Parallel.ai

## Overview

Task Groups let you batch process hundreds or thousands of tasks efficiently. Rather than submitting and tracking runs one by one, you organize them into a named group, monitor progress collectively, and retrieve results in bulk or as a live stream.

This is the preferred pattern when you have a large dataset to process — company lists, document corpora, URL queues — and want to fan out work across Parallel's infrastructure without managing individual run IDs yourself.

## Group Lifecycle

| Step | Action | Endpoint |
|------|--------|----------|
| 1 | Create group with shared task spec | `POST /v1beta/tasks/groups` |
| 2 | Add runs (up to 1,000 per request) | `POST /v1beta/tasks/groups/{taskgroup_id}/runs` |
| 3 | Monitor status or stream events | `GET /v1beta/tasks/groups/{taskgroup_id}` or `/events` |
| 4 | Retrieve all run results | `GET /v1beta/tasks/groups/{taskgroup_id}/runs` |

Steps 2 and 3 can overlap — you can begin streaming results before all runs have been added.

---

## Endpoints

### 1. Create Task Group

Define the shared `task_spec` (including output schema) once at the group level. All runs in the group inherit this spec.

```bash
GROUP_ID=$(curl -s -X POST https://api.parallel.ai/v1beta/tasks/groups \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "base",
    "task_spec": {
      "output_schema": {
        "type": "object",
        "properties": {
          "summary": { "type": "string" },
          "score": { "type": "number" }
        },
        "required": ["summary", "score"]
      }
    }
  }' | jq -r '.taskgroup_id')

echo "Group ID: $GROUP_ID"
```

### 2. Add Runs

Submit up to 1,000 runs per POST request. Each run provides its own `input`; the group-level `task_spec` applies to all.

```bash
curl -s -X POST "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/runs" \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "runs": [
      {"input": "Company A"},
      {"input": "Company B"},
      {"input": "Company C"}
    ]
  }'
```

You can call this endpoint multiple times to add more runs incrementally. Processing begins as runs are added — you do not need to signal when the group is "complete."

### 3. Retrieve Group Status

Poll the group to check aggregate progress.

```bash
curl -s "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}" \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

The response includes counts of runs by state (pending, running, completed, failed, cancelled) so you can track overall progress without fetching individual runs.

### 4. Fetch Group Runs

Retrieve results for all runs in the group at once.

```bash
curl -s "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/runs" \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

This is best used after the group finishes. For large groups or real-time processing, prefer the events stream.

### 5. Stream Group Events (SSE)

Subscribe to a server-sent event stream that delivers run results as they complete.

```bash
curl -s --no-buffer \
  "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/events?include_output=true" \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Query parameters:**

| Parameter | Description |
|-----------|-------------|
| `include_output=true` | Embed run output directly in the event payload |
| `include_input=true` | Embed the original run input in the event payload |
| `last_event_id=<id>` | Resume stream from this cursor after a disconnection |

**Event types:**

| Type | When emitted |
|------|--------------|
| `task_run.state` | A run completes, fails, or is cancelled |
| `error` | A stream-level error occurred |

Each event includes an `event_id` field you can use as a cursor for reconnection via `last_event_id`.

---

## Bash Script Pattern for Large Datasets

This script reads a JSON array from a file, creates a group, submits all items in batches of 1,000, then streams results to stdout.

```bash
#!/bin/bash
# Process a JSON array file through Parallel Task Groups
# Usage: ./batch-process.sh items.json [processor]

ITEMS_FILE="$1"
PROCESSOR="${2:-base}"
BATCH_SIZE=1000

if [[ -z "$PARALLEL_API_KEY" ]]; then
  echo "Error: PARALLEL_API_KEY is not set" >&2
  exit 1
fi

# Create group
GROUP_ID=$(curl -s -X POST https://api.parallel.ai/v1beta/tasks/groups \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"processor\": \"${PROCESSOR}\",
    \"task_spec\": {
      \"output_schema\": {
        \"type\": \"object\",
        \"properties\": {
          \"result\": { \"type\": \"string\" }
        },
        \"required\": [\"result\"]
      }
    }
  }" | jq -r '.taskgroup_id')

echo "Created group: $GROUP_ID" >&2

# Submit runs in batches of up to 1,000
TOTAL=$(jq length "$ITEMS_FILE")
echo "Submitting $TOTAL items in batches of $BATCH_SIZE..." >&2

for ((i=0; i<TOTAL; i+=BATCH_SIZE)); do
  BATCH=$(jq ".[$i:$((i+BATCH_SIZE))] | map({input: .})" "$ITEMS_FILE")
  curl -s -X POST "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/runs" \
    -H "x-api-key: ${PARALLEL_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"runs\": ${BATCH}}" > /dev/null
  echo "Submitted batch $((i/BATCH_SIZE + 1))" >&2
done

echo "All batches submitted. Streaming results..." >&2

# Stream results as they complete
curl -s --no-buffer \
  "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/events?include_output=true&include_input=true" \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

### Parsing the Event Stream

Each SSE event is a line prefixed with `data:`. Pipe through a simple filter to extract structured output:

```bash
./batch-process.sh items.json | \
  grep '^data:' | \
  sed 's/^data: //' | \
  jq -c 'select(.type == "task_run.state") | {input: .input, output: .output}'
```

---

## Best Practices

**Define `task_spec` at the group level.** Sharing a single spec across all runs ensures consistent output schemas and avoids redundant per-run configuration.

**Add runs incrementally, don't batch everything before starting.** Parallel begins processing as soon as runs are added. You can submit your first batch and immediately open the event stream while continuing to add more runs.

**Store results as they stream in.** For large groups, waiting for all runs to complete before reading results wastes time and risks losing data if your process exits. Write each `task_run.state` event to a file or database as it arrives.

**Use `include_output=true` on the events stream.** This delivers the run result inline with the completion event, avoiding a second API call per run to fetch output.

**Use `metadata` to tag runs for post-processing.** If you need to correlate results back to your source data (e.g., a database row ID or filename), attach it as metadata when adding runs. It will be returned with each result.

**Resume dropped streams with `last_event_id`.** Store the most recent `event_id` as you process events. If your connection drops, reconnect with `?last_event_id=<saved_id>` to resume without reprocessing.

**Respect the rate limit.** The API allows up to 2,000 task creates per minute across all groups. At `BATCH_SIZE=1000`, this means you can submit two full batches per minute without throttling.

---

## Example: Resumable Stream Consumer

```bash
#!/bin/bash
# Stream events from an existing group, resuming from last seen event
GROUP_ID="$1"
LAST_EVENT_ID="${2:-}"
OUTPUT_FILE="${3:-results.jsonl}"

CURSOR_PARAM=""
if [[ -n "$LAST_EVENT_ID" ]]; then
  CURSOR_PARAM="&last_event_id=${LAST_EVENT_ID}"
fi

curl -s --no-buffer \
  "https://api.parallel.ai/v1beta/tasks/groups/${GROUP_ID}/events?include_output=true${CURSOR_PARAM}" \
  -H "x-api-key: ${PARALLEL_API_KEY}" | \
while IFS= read -r line; do
  if [[ "$line" == data:* ]]; then
    EVENT="${line#data: }"
    TYPE=$(echo "$EVENT" | jq -r '.type // empty')
    if [[ "$TYPE" == "task_run.state" ]]; then
      echo "$EVENT" >> "$OUTPUT_FILE"
      LAST_EVENT_ID=$(echo "$EVENT" | jq -r '.event_id // empty')
      echo "Saved event $LAST_EVENT_ID" >&2
    fi
  fi
done

echo "Last event ID: $LAST_EVENT_ID" >&2
```

Run with a saved cursor to resume:

```bash
./stream-consumer.sh grp_abc123 evt_xyz789 results.jsonl
```
