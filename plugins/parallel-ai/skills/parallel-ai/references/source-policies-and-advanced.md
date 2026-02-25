# Source Policies and Advanced Features

This reference covers source policies, interaction context chaining, metadata, MCP server integration, beta headers, rate limits, and error handling for the Parallel.ai Task API.

---

## Source Policies

Source policies give you control over which domains a processor can access during research, and optionally constrain content freshness.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `include_domains` | array[string] | Restrict sources to only these domains (max 10) |
| `exclude_domains` | array[string] | Block sources from these domains (max 10) |
| `after_date` | string (YYYY-MM-DD) | Only use content published on or after this date (Search API only) |

**Domain matching:** Specifying an apex domain such as `example.com` automatically includes all subdomains (e.g. `blog.example.com`, `docs.example.com`).

**Constraint:** `include_domains` and `exclude_domains` are mutually exclusive — you cannot use both in the same request.

### Example: Restrict to Authoritative Sources

```bash
curl -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "core",
    "input": "Latest product announcements from Apple",
    "source_policy": {
      "include_domains": ["apple.com", "9to5mac.com", "macrumors.com"]
    }
  }'
```

### Applicability

Source policies (`include_domains`, `exclude_domains`, `after_date`) apply to both the Task API (`POST /v1/tasks/runs`) and the Search API (`POST /v1beta/search`). The Extract API does not use source policies since URLs are provided explicitly.

### Best Practices

- Use `include_domains` when you need results grounded in specific authoritative sources — official documentation, trusted publications, or known data providers.
- Use `exclude_domains` to filter out known low-quality or unreliable sources without restricting the broader search space.
- Combine `after_date` with a focused `input` or `task_spec` when you need recent developments only — this avoids stale content surfacing in the results.
- Keep domain lists short and targeted. The max of 10 domains per policy encourages precision over breadth.

---

## Interaction Context Reuse

Tasks in Parallel.ai are stateless by default, but you can chain related tasks by passing a `previous_interaction_id`. This allows a follow-up task to build on the research and context established by a prior run without re-fetching or re-processing that context.

Any completed task run returns an `interaction_id` in its result. Pass this ID into a subsequent request to continue the research thread.

### Example: Chaining a Follow-Up Task

```bash
curl -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "pro",
    "input": "Now analyze their competitive advantages in detail",
    "previous_interaction_id": "trun_e0083b6aac0544eb8686e8d2a76533d2"
  }'
```

### When to Use This

- Multi-step research workflows where later questions depend on earlier findings.
- Breaking a complex task into smaller, focused subtasks while preserving continuity.
- Refining or expanding on an initial summary without redundant source lookups.

The `previous_interaction_id` must reference a completed run. Passing the ID of a still-running or failed task will result in a validation error.

---

## Metadata

Metadata allows you to attach arbitrary key-value pairs to a task run. These are stored alongside the run and returned in responses, making them useful for tagging, filtering, or linking runs to your own internal systems for post-processing.

### Constraints

- Keys: strings, max 16 characters
- Values: strings, max 512 characters
- Metadata is not used by the processor during execution — it is for your own bookkeeping only

### Example

```json
"metadata": {
  "project": "q4-research",
  "entity_type": "competitor",
  "batch_id": "batch_001"
}
```

Common uses include associating runs with internal project identifiers, labeling runs by entity type for downstream filtering, or tracking batch membership when submitting multiple related tasks.

---

## MCP Server Integration (Beta)

You can provide external MCP (Model Context Protocol) tool servers for a task to use during execution. This extends what the processor can do beyond its built-in capabilities — for example, querying a private database, calling a proprietary API, or invoking custom logic hosted by your infrastructure.

### Configuration

```json
"mcp_servers": [
  {
    "url": "https://my-tool-server.example.com/mcp",
    "type": "sse"
  }
]
```

MCP server integration requires the beta opt-in header:

```
parallel-beta: mcp-server-2025-07-17
```

This feature is in beta. Availability and behavior may change. Test in non-production workflows before relying on it at scale.

---

## Beta Headers Reference

Several Parallel.ai features are available as opt-in betas. Enable them by including the `parallel-beta` header in your request. Multiple beta features can be enabled in a single request by comma-separating their values.

| Header Value | Feature | Status |
|---|---|---|
| `events-sse-2025-07-24` | SSE streaming for task run events | Beta |
| `webhook-2025-08-12` | Webhook notifications on run completion | Beta |
| `field-basis-2025-11-25` | Per-element basis citations in structured output | Beta |
| `mcp-server-2025-07-17` | MCP server integration during task execution | Beta |
| `search-extract-2025-10-10` | Search and Extract APIs | Beta |

### Example: Multiple Beta Features

```
parallel-beta: events-sse-2025-07-24, webhook-2025-08-12
```

Beta features are subject to change or removal. Pin your usage to the dated identifiers listed above so that changes to newer beta versions do not affect existing integrations unexpectedly.

---

## Rate Limits

| Product | Default Quota |
|---|---|
| Tasks / Task Groups | 2,000 creates per minute |
| Search API | 600 requests per minute |
| Extract API | 600 requests per minute |

Task/Group quota applies to:
- `POST /v1/tasks/runs`
- `POST /v1beta/tasks/groups/{id}/runs`

Search/Extract quota applies to:
- `POST /v1beta/search`
- `POST /v1beta/extract`

Status polling and result retrieval (`GET` endpoints) are not subject to the same rate limits, so polling for completion on already-submitted runs will not count against your creation quota.

If you are running large batch workloads, use Task Groups to submit many runs efficiently and poll or receive webhooks for completion rather than submitting individual runs in rapid sequence.

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|---|---|
| `401` | Invalid or missing API key |
| `402` | Insufficient credits to complete the request |
| `403` | Feature not available on your current plan |
| `422` | Validation error — bad request schema, invalid processor name, conflicting parameters, etc. |
| `429` | Rate limit exceeded |

### Handling 429 Rate Limit Errors

Back off and retry with exponential delay. Do not immediately resubmit at the same rate. If you consistently hit rate limits, consider batching work into Task Groups or spreading submissions over a longer window.

### Failed Runs

A `422` or other HTTP error on submission means the run was never created. For runs that are created but fail during execution, the failure is reflected in the run's status field rather than as an HTTP error code on the status endpoint.

Common causes of run-level failures:

- **Invalid output schema** — The `task_spec` defines a structured output schema that the processor could not populate correctly. Simplify the schema or make fields optional where possible.
- **Insufficient information** — The processor could not find enough reliable information to satisfy the task. Broaden the input, relax source policies, or switch to a higher-tier processor.
- **Timeout on complex tasks** — The task exceeded processing limits. Break the task into smaller subtasks, or use a higher-tier processor (`pro` or `ultra`) which supports more complex and longer-running research.

When a run fails, retrieve the run result to inspect the error details before retrying or adjusting your request.
