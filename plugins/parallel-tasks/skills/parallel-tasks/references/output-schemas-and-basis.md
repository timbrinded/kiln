# Output Schemas and Basis Citations

This reference covers task specifications, output schema types, validation rules, and the Basis citation framework for the Parallel.ai Task API.

---

## Task Specifications

A **Task Specification** (`task_spec`) is a declarative template attached to a task run that defines the structure and requirements for the output. It is optional, but using one provides:

- **Consistent results** — outputs conform to a predictable shape across runs
- **Schema validation** — the API enforces structure and catches malformed outputs early
- **Reusable templates** — define once, apply across many task runs
- **Self-documentation** — the schema describes what the task is expected to produce

`task_spec` is passed as a field in the `POST /v1/tasks/runs` request body alongside `processor` and `input`.

---

## Output Schema Types

There are three ways to specify an output schema, ranging from fully structured to completely open-ended.

### 1. JSON Schema

Use `type: "json"` with a `json_schema` object to enforce a structured output. The task result will be returned as a parsed JSON object conforming to the schema.

```json
"task_spec": {
  "output_schema": {
    "json_schema": {
      "type": "object",
      "properties": {
        "company_name": { "type": "string", "description": "Legal company name" },
        "revenue": { "type": "string", "description": "Annual revenue in USD" }
      },
      "required": ["company_name", "revenue"],
      "additionalProperties": false
    },
    "type": "json"
  }
}
```

The `content` field in the result will be a JSON object. Use this when downstream code needs to reliably parse and consume specific fields.

### 2. Text Schema

Use a plain string to describe the desired output in natural language. The processor will follow this description as a formatting instruction.

```json
"task_spec": {
  "output_schema": "A 3-paragraph summary of the company's competitive position"
}
```

The `content` field in the result will be a string. Use this for narrative, prose, or any output that does not need programmatic parsing.

### 3. Auto Schema

Omit `output_schema` entirely. The processor decides the output format on its own, enabling **Deep Research** style outputs where the processor can return rich, multi-section documents. This mode is only available on `pro` and higher processors.

```json
"task_spec": {}
```

Or simply omit `task_spec` from the request altogether.

---

## Schema Validation Rules

When using a JSON Schema, the API validates the schema itself before accepting the task run. The following rules apply:

| Rule | Severity | Description |
|------|----------|-------------|
| Root type must be object | error | The root schema must have `"type": "object"` |
| Root must have properties | error | The root object must include a `properties` field |
| Root cannot use anyOf | error | `anyOf` is not permitted at the root level |
| Standalone null type | error | `null` is only allowed as part of a union type, not as a standalone type |
| All fields must be required | warning | All properties defined in the schema should appear in the `required` array |
| additionalProperties must be false | warning | All object definitions should set `"additionalProperties": false` to prevent unexpected fields |

Errors cause the request to be rejected. Warnings are surfaced in the response but the task will still run.

Following the warnings (requiring all fields, disabling additional properties) produces the most reliable and predictable outputs.

---

## Input Schema (for Enrichment Tasks)

When the task `input` is a JSON object rather than a plain string, you can provide an `input_schema` inside `task_spec` to describe the structure of that input. This is common for enrichment workflows where each task run receives a record to process.

```json
"task_spec": {
  "input_schema": {
    "json_schema": {
      "type": "object",
      "properties": {
        "company": { "type": "string", "description": "Company name to enrich" }
      },
      "required": ["company"],
      "additionalProperties": false
    }
  },
  "output_schema": {
    "json_schema": {
      "type": "object",
      "properties": {
        "company_name": { "type": "string", "description": "Legal company name" },
        "revenue": { "type": "string", "description": "Annual revenue in USD" }
      },
      "required": ["company_name", "revenue"],
      "additionalProperties": false
    },
    "type": "json"
  }
}
```

The `input_schema` helps the processor understand what the input represents and improves output accuracy. It follows the same JSON Schema rules as `output_schema`.

---

## The Basis Framework

Every `TaskRunOutput` includes a `basis` array. Basis is a field-level citation system that records the evidence the processor used to populate each output field. It provides transparency, auditability, and a mechanism to assess output reliability.

### FieldBasis Object

Each entry in the `basis` array is a `FieldBasis` object:

| Field | Type | Description |
|-------|------|-------------|
| `field` | string | The output field this evidence supports. Use dot notation for nested fields (e.g., `executives.0.name`) |
| `citations` | array | Sources used. Each citation has `url`, `title`, and `snippet` |
| `reasoning` | string | Explanation of how the processor evaluated and synthesized the information |
| `confidence` | string | `"high"`, `"medium"`, or `"low"` |

### Confidence Levels

| Level | Meaning |
|-------|---------|
| `high` | Strong evidence from multiple authoritative sources with consistent information |
| `medium` | Adequate evidence but with some inconsistencies, or sourced from less authoritative references |
| `low` | Limited or conflicting evidence, or information from less reliable sources |

Treat `low` confidence fields as candidates for manual review before use in downstream processes.

---

## Per-Element Basis (Beta)

By default, `basis` entries cover entire fields. For array outputs where you need per-element citations — for example, a list of executives where each entry needs its own evidence chain — enable per-element basis with the beta header:

```
parallel-beta: field-basis-2025-11-25
```

With this header, the `basis` array will include separate entries for each element in the array, using indexed dot notation:

- `executives.0` — basis for the first executive
- `executives.1` — basis for the second executive
- `executives.0.name` — basis for a specific field within the first element

This is useful for bulk enrichment tasks where individual records need traceable provenance.

---

## Verification Patterns

When consuming task output, use the `basis` array to assess reliability before acting on results:

- **Check confidence levels first** — fields with `"high"` confidence can generally be used directly; `"low"` confidence fields should be flagged for review
- **Count citations** — a field backed by multiple citations from distinct sources is stronger than one with a single citation
- **Read the reasoning** — the `reasoning` field explains how the processor handled conflicting information; this is especially useful when sources disagreed
- **Audit low confidence fields** — if a field has `"low"` confidence, inspect the citations and reasoning to decide whether to accept, discard, or manually verify the value

---

## Full Enrichment Example

This example creates a task that enriches a company record, waits for the result, and returns structured output with field-level citations.

**Step 1: Create the task run**

```bash
curl -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "core",
    "input": { "company": "Stripe" },
    "task_spec": {
      "input_schema": {
        "json_schema": {
          "type": "object",
          "properties": {
            "company": { "type": "string", "description": "Company name to enrich" }
          },
          "required": ["company"],
          "additionalProperties": false
        }
      },
      "output_schema": {
        "json_schema": {
          "type": "object",
          "properties": {
            "company_name": { "type": "string", "description": "Legal company name" },
            "revenue": { "type": "string", "description": "Annual revenue in USD" }
          },
          "required": ["company_name", "revenue"],
          "additionalProperties": false
        },
        "type": "json"
      }
    }
  }'
```

**Response:**

```json
{
  "run_id": "trun_stripe01",
  "status": "queued",
  "is_active": true,
  "processor": "core",
  "created_at": "2025-11-25T09:00:00Z"
}
```

**Step 2: Fetch the result (blocking)**

```bash
curl https://api.parallel.ai/v1/tasks/runs/trun_stripe01/result \
  -H "x-api-key: ${PARALLEL_API_KEY}"
```

**Response:**

```json
{
  "run": {
    "run_id": "trun_stripe01",
    "status": "completed",
    "is_active": false,
    "processor": "core",
    "created_at": "2025-11-25T09:00:00Z",
    "modified_at": "2025-11-25T09:00:42Z"
  },
  "output": {
    "type": "json",
    "content": {
      "company_name": "Stripe, Inc.",
      "revenue": "$14 billion (estimated, 2023)"
    },
    "basis": [
      {
        "field": "company_name",
        "citations": [
          {
            "url": "https://stripe.com/about",
            "title": "About Stripe",
            "snippet": "Stripe, Inc. is a financial infrastructure platform..."
          }
        ],
        "reasoning": "Legal name confirmed directly from Stripe's official about page.",
        "confidence": "high"
      },
      {
        "field": "revenue",
        "citations": [
          {
            "url": "https://example.com/stripe-revenue-2023",
            "title": "Stripe Revenue Estimates 2023",
            "snippet": "Stripe's estimated annual revenue for 2023 is approximately $14 billion..."
          },
          {
            "url": "https://example.com/fintech-analysis",
            "title": "Fintech Private Company Revenue Analysis",
            "snippet": "Based on payment volume disclosures, Stripe revenue is estimated at $13-15B..."
          }
        ],
        "reasoning": "Stripe is private and does not disclose revenue. Two independent analyst estimates aligned closely. Figure presented as estimated.",
        "confidence": "medium"
      }
    ]
  }
}
```

The `company_name` field has high confidence from an authoritative source. The `revenue` field has medium confidence because the company is private — the reasoning explains why, and two citations triangulate the estimate. A consumer of this data would know to treat the revenue figure as an approximation.
