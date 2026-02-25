# parallel-ai

A Claude Code plugin for the Parallel.ai Task API — web research, data enrichment, and batch intelligence via HTTP/curl. No SDK required. All 18 processor tiers, async patterns, output schemas with basis citations, task groups, and source policies.

## What it does

| Mode | Input | Output |
|------|-------|--------|
| **Research** | Natural language query | Web research result with source citations |
| **Enrichment** | Structured JSON + output schema | Schema-conforming data with per-field citations |
| **Batch** | JSON array of items | Parallel-processed results via task groups |
| **Monitoring** | Run/group ID | Status, result, or event stream |

---

## Installation

### From the Kiln marketplace (recommended)

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install parallel-ai@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/parallel-ai
```

### Verify installation

After installing, run `/help` in Claude Code. You should see:

```
/parallel   (parallel-ai)  Run web research, data enrichment, batch tasks...
```

The `parallel-researcher` agent and the `parallel-ai` skill activate automatically when relevant.

---

## Usage

### Slash command

#### `/parallel research`

Run a web research query:

```
/parallel research "What are the main competitors to Figma in 2025?"
/parallel research "Latest Series B+ funding rounds in AI infrastructure" --processor pro
```

#### `/parallel enrich`

Enrich structured data with a schema:

```
/parallel enrich '{"company":"Stripe"}' --schema company-schema.json
/parallel enrich '{"person":"Jensen Huang"}'
```

#### `/parallel batch`

Batch process a list of items:

```
/parallel batch companies.json --processor base
/parallel batch leads.json --processor core
```

#### `/parallel status` / `result` / `stream`

Monitor existing task runs:

```
/parallel status trun_9907962f83aa4d9d98fd7f4bf745d654
/parallel result trun_9907962f83aa4d9d98fd7f4bf745d654
/parallel stream trun_9907962f83aa4d9d98fd7f4bf745d654
```

### Automatic skill activation

The `parallel-ai` skill activates automatically when you mention web research, data enrichment, or the Parallel API:

- "Research the competitive landscape for..."
- "Enrich this list of companies"
- "Look up current information about..."
- "Run a deep research task on..."

### Agent: parallel-researcher

The `parallel-researcher` agent triggers when Claude detects you need current web data, entity enrichment, or batch processing. It runs with `Read`, `Bash`, `Grep`, and `Glob` tools — Bash is required for curl execution.

---

## Configuration

Create a settings file at `.claude/parallel-ai.local.md` in your project root (or `~/.claude/parallel-ai.local.md` globally):

```yaml
---
default-processor: base
api-key-env: PARALLEL_API_KEY
---
```

### default-processor

The processor tier used when not specified per-request.

| Tier | Cost | Best For |
|------|------|----------|
| `lite` | $0.005/task | Simple fact lookups |
| `base` | $0.01/task | Standard enrichments |
| `core` | $0.025/task | Cross-referenced research |
| `pro` | $0.10/task | Exploratory research |
| `ultra` | $0.30/task | Deep multi-source research |

### api-key-env

Environment variable name holding the API key. Default: `PARALLEL_API_KEY`.

---

## Processor tiers

| Processor | $/1000 | Latency | Strengths |
|-----------|--------|---------|-----------|
| `lite` | 5 | 10s–60s | Basic metadata, fallback, low latency |
| `base` | 10 | 15s–100s | Reliable standard enrichments |
| `core` | 25 | 60s–5min | Cross-referenced, moderately complex |
| `core2x` | 50 | 60s–10min | High complexity cross-referenced |
| `pro` | 100 | 2min–10min | Exploratory web research |
| `ultra` | 300 | 5min–25min | Advanced multi-source deep research |
| `ultra2x` | 600 | 5min–50min | Difficult deep research |
| `ultra4x` | 1200 | 5min–90min | Very difficult deep research |
| `ultra8x` | 2400 | 5min–2hr | The most difficult deep research |

All 9 have `-fast` variants (same price, lower latency) for 18 total.

---

## Plugin structure

```
parallel-ai/
├── .claude-plugin/
│   └── plugin.json                              # Plugin manifest
├── agents/
│   └── parallel-researcher.md                   # Web research & enrichment agent
├── commands/
│   └── parallel.md                              # /parallel command (6 modes)
├── skills/
│   └── parallel-ai/
│       ├── SKILL.md                             # Core skill — mode routing (~900 words)
│       └── references/
│           ├── api-reference.md                 # Complete endpoint catalog
│           ├── processor-guide.md               # 18 tiers, decision framework, chaining
│           ├── async-patterns.md                # Blocking, polling, SSE, webhooks
│           ├── output-schemas-and-basis.md      # Schema types, Basis citations
│           ├── task-groups.md                   # Batch processing lifecycle
│           └── source-policies-and-advanced.md  # Source policies, context, metadata, MCP
└── README.md
```

**How progressive disclosure works:** The skill metadata (~100 words) is always in Claude's context. When triggered, SKILL.md adds ~900 words of mode routing. Only when a specific operation runs does the relevant reference file (~1,200 words each) get loaded. Maximum context cost for a single operation is ~2,100 words.

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- `PARALLEL_API_KEY` environment variable — [get an API key](https://parallel.ai)
- `jq` (recommended for JSON parsing in curl responses)

---

## License

MIT
