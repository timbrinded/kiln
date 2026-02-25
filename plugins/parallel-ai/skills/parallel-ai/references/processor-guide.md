# Parallel.ai Processor Guide

Choosing the right processor tier is the most important decision when using Parallel.ai. The wrong choice either wastes budget and time (over-engineering) or produces shallow results (under-engineering). This guide covers all 18 processors, decision frameworks, chaining patterns, and common mistakes.

---

## Processor Tiers

### Standard Processors

| Processor | Cost ($/1000 tasks) | Cost per task | Latency | Strengths |
|-----------|--------------------:|--------------|---------|-----------|
| `lite` | $5 | $0.005 | 10s–60s | Basic metadata, fallback, low latency |
| `base` | $10 | $0.010 | 15s–100s | Reliable standard enrichments |
| `core` | $25 | $0.025 | 60s–5min | Cross-referenced, moderately complex |
| `core2x` | $50 | $0.050 | 60s–10min | High complexity cross-referenced |
| `pro` | $100 | $0.100 | 2min–10min | Exploratory web research |
| `ultra` | $300 | $0.300 | 5min–25min | Advanced multi-source deep research |
| `ultra2x` | $600 | $0.600 | 5min–50min | Difficult deep research |
| `ultra4x` | $1,200 | $1.200 | 5min–90min | Very difficult deep research |
| `ultra8x` | $2,400 | $2.400 | 5min–2hr | The most difficult deep research |

### Fast Processors

Every standard processor has a `-fast` variant (e.g., `lite-fast`, `base-fast`, `core-fast`, etc.) optimized for lower latency at the same price point. Use fast variants when your use case is interactive or latency-sensitive. There are 9 fast variants in total, one per standard tier.

| Fast Variant | Base Equivalent | Best For |
|---|---|---|
| `lite-fast` | `lite` | Real-time lookups, data validation |
| `base-fast` | `base` | Interactive enrichment workflows |
| `core-fast` | `core` | Moderately complex tasks where speed matters |
| `core2x-fast` | `core2x` | High complexity with time constraints |
| `pro-fast` | `pro` | Research tasks in interactive tools |
| `ultra-fast` | `ultra` | Deep research in time-constrained pipelines |
| `ultra2x-fast` | `ultra2x` | Difficult research with latency budget |
| `ultra4x-fast` | `ultra4x` | Very difficult research, faster output |
| `ultra8x-fast` | `ultra8x` | Maximum effort, optimized scheduling |

---

## Decision Framework

### By Use Case

| Use Case | Recommended Processor |
|---|---|
| Simple fact lookup | `lite` or `base` |
| Company enrichment | `base` or `core` |
| Competitive analysis | `pro` or `ultra` |
| Deep research report | `ultra` through `ultra8x` |
| Quick data validation | `lite-fast` |
| Interactive enrichment | `base-fast` or `core-fast` |
| Market mapping | `core` or `core2x` |
| Executive profiling | `core` or `pro` |
| Investment research | `ultra` or `ultra2x` |

Start conservative. If results are insufficient, step up one tier. Most enrichment tasks that feel like they need `pro` are actually handled well by `base` or `core`.

### By Latency Requirement

| Latency Budget | Use |
|---|---|
| Under 30s | `lite-fast` or `base-fast` |
| Under 2min | `base` or `core` |
| Under 10min | `core2x` or `pro` |
| Under 30min | `ultra` or `ultra-fast` |
| Latency doesn't matter | `ultra2x`+ for hardest tasks |

For any user-facing or interactive workflow, default to a `-fast` variant. For batch pipelines running overnight, standard variants are fine.

### By Budget

| Budget Sensitivity | Use | Why |
|---|---|---|
| High volume / low margin | `lite` ($0.005/task) | Scale to millions of tasks cheaply |
| Standard enrichment | `base` ($0.01/task) | Best value for most enrichment |
| Research quality | `pro` ($0.10/task) | 10x cost, meaningful quality jump |
| Deep analysis | `ultra` ($0.30/task) | Full multi-source synthesis |
| Maximum depth | `ultra2x`–`ultra8x` | Rare; only for genuinely hard problems |

The jump from `ultra` to `ultra8x` is 8x the cost. Reserve `ultra4x` and `ultra8x` for tasks that are explicitly hard: obscure companies, thin public information, highly contested facts, or tasks requiring synthesis across many conflicting sources.

---

## Multi-Processor Chaining

Chaining lets you do an initial cheap lookup and then pass that context into a deeper processor without re-researching from scratch. Use `previous_interaction_id` to reference a prior task result.

**Pattern:** Run `base` for initial data, then run `pro` with the prior result as context.

```bash
# Step 1: Initial lookup with base
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "processor": "base",
    "input": "What does Acme Corp do? Find their main product lines and founding year."
  }' | jq -r '.run_id')

# Get result and capture interaction_id
RESULT=$(curl -s https://api.parallel.ai/v1/tasks/runs/${RUN_ID}/result \
  -H "x-api-key: ${PARALLEL_API_KEY}")
INTERACTION_ID=$(echo $RESULT | jq -r '.run.interaction_id')

# Step 2: Deep dive using prior context
curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: ${PARALLEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"processor\": \"pro\",
    \"input\": \"Who are Acme Corp's top 3 competitors and what are their relative strengths?\",
    \"previous_interaction_id\": \"${INTERACTION_ID}\"
  }"
```

**Why this matters:** Without `previous_interaction_id`, the `pro` processor starts from scratch. With it, the processor skips re-fetching facts already established in the `base` run, saving both time and money. The second call costs `pro` rates, but it does `pro`-tier work on top of `base`-tier groundwork rather than `pro`-tier work duplicating `base`-tier work.

**Chain depth:** You can chain more than two steps. Each `previous_interaction_id` passes the full prior context forward. This is useful for pipelines that progressively deepen research: `lite` → `core` → `ultra`.

---

## Common Mistakes

### 1. Using `ultra8x` when `core` suffices

`ultra8x` is for the hardest research tasks: obscure subjects, thin public footprint, highly contested information. For most company enrichment and fact-finding tasks, `core` or `core2x` is more than sufficient. The cost difference is 96x ($0.025 vs $2.40 per task). Defaulting to maximum power because the result "really matters" is not a good reason — validate that the task is actually difficult first.

**Fix:** Start with `base` or `core`. Inspect results. Only escalate if the output is genuinely insufficient for the specific task.

### 2. Not using fast variants for interactive use cases

If a user is waiting for a result in a UI or CLI, `base` at 15s–100s latency may produce an acceptable result but the tail latency (100s) is frustrating. `base-fast` targets the low end of that range. The cost is identical.

**Fix:** Default to `-fast` variants for any human-in-the-loop workflow. Use standard variants for batch jobs where latency is irrelevant.

### 3. Ignoring `previous_interaction_id` and re-researching from scratch

Running a follow-up `pro` task on the same subject without referencing the prior `base` result means paying `pro` rates for work the `base` processor already did. This also increases latency since the processor rediscovers known facts.

**Fix:** Always capture `interaction_id` from prior responses and pass it in follow-up tasks. Treat it as a session ID for a research thread.

### 4. Defaulting to `pro` when `base` handles most enrichment

`pro` is for exploratory web research — tasks where the processor needs to discover, synthesize, and reason across multiple sources. Most enrichment tasks (company size, location, industry, funding stage, contact data) are well within `base` or `core` capability. `pro` at $0.10/task is 10x the cost of `base` at $0.01/task.

**Fix:** Reserve `pro` for tasks that genuinely require open-ended research or synthesis. Use `base` as the default starting point for enrichment pipelines and only escalate when results are demonstrably insufficient.

---

## Quick Reference

```
lite / lite-fast     → simple, fast, cheap. Good for validation and metadata.
base / base-fast     → default for enrichment. Handles most structured lookups.
core / core2x        → cross-referencing, moderate complexity, reliable depth.
pro                  → exploratory research, competitive intel, open-ended queries.
ultra / ultra2x+     → deep multi-source synthesis. Use for genuinely hard tasks.
-fast variants       → same price, lower latency. Always use for interactive flows.
previous_interaction_id → thread context across calls. Never re-research from scratch.
```
