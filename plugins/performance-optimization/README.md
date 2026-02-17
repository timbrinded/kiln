# performance-optimization

A Claude Code plugin that encodes language-agnostic performance optimization knowledge distilled from Google's Abseil performance engineering wisdom. Covers measurement methodology, optimization techniques across 4 categories, and cross-language patterns for C++, Rust, and TypeScript.

## What it does

The plugin activates automatically when you ask to optimize, profile, benchmark, or discuss performance. It provides structured guidance through a decision tree that routes to the right technique based on the bottleneck type.

| Bottleneck | Reference | Techniques |
|------------|-----------|------------|
| Wrong algorithm | `techniques-algorithms.md` | Complexity reduction, data structure selection, bulk APIs, regex optimization |
| Memory layout | `techniques-memory.md` | Compact structs, field reordering, indices vs. pointers, arenas, bit vectors |
| Unnecessary work | `techniques-execution.md` | Fast paths, precomputation, deferred computation, specialization, caching |
| Too many allocations | `techniques-allocations.md` | Reserve/resize, move vs. copy, reuse temporaries, object pooling |
| Need to measure | `measurement.md` | Profiling methodology, flat profiles, microbenchmarking, hardware counters |
| Process questions | `optimization-process.md` | Project selection, success metrics, reversibility, rollout strategy |
| Cross-language | `language-equivalents.md` | C++ → Rust → TypeScript mapping for all techniques |

### Expected impact by category

| Category | Typical Impact |
|----------|---------------|
| Algorithm/data structure | 10–1000x |
| Memory representation | 2–10x |
| Avoid unnecessary work | 2–20x |
| Reduce allocations | 1.2–5x |
| Bulk APIs | 2–10x |

---

## Installation

### From the Kiln marketplace (recommended)

In the Claude Code interactive terminal:

```
/plugin marketplace add https://github.com/timbrinded/kiln.git
/plugin install performance-optimization@kiln
```

### Test without installing

```bash
claude --plugin-dir /path/to/kiln/plugins/performance-optimization
```

### Verify installation

The `performance-optimization` skill activates automatically when relevant — no slash command needed. Just talk naturally:

- "This function is too slow"
- "Optimize this loop"
- "Profile memory usage"
- "What data structure should I use here?"
- "Reduce allocations in this hot path"

---

## Usage

The skill uses **progressive disclosure** — only the relevant reference files are loaded based on the bottleneck type, keeping context window cost low.

### Optimization workflow

```
1. MEASURE  →  2. IDENTIFY  →  3. OPTIMIZE  →  4. VERIFY
   Profile       Find the          Apply           Measure
   first         bottleneck        technique        again
```

### Quick reference: latency numbers

| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 3 ns |
| Branch mispredict | 5 ns |
| Mutex lock/unlock | 15 ns |
| Main memory reference | 50 ns |
| Compress 1KB | 1 us |
| Read 4KB from SSD | 20 us |
| Datacenter round trip | 50 us |
| Read 1MB sequentially (RAM) | 64 us |
| Read 1MB from SSD | 1 ms |
| Disk seek | 5 ms |
| Read 1MB from disk | 10 ms |

### Language-specific tools

| Purpose | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| CPU profiling | `pprof`, `perf` | `perf`, `flamegraph`, `samply` | Chrome DevTools, `clinic.js` |
| Memory profiling | `tcmalloc` heap profiler | `dhat`, `heaptrack` | Chrome DevTools Memory tab |
| Microbenchmarking | Google Benchmark | `criterion`, `divan` | `vitest bench`, `Benchmark.js` |
| Hardware counters | `perf stat` | `perf stat`, `iai-callgrind` | N/A |

---

## Plugin structure

```
performance-optimization/
├── .claude-plugin/
│   └── plugin.json                  # Plugin manifest
├── skills/
│   └── performance/
│       ├── SKILL.md                 # Core skill — decision tree routing (~1,000 words)
│       └── references/
│           ├── philosophy.md        # Mindset, critical 3%, estimation, latency numbers
│           ├── measurement.md       # Profiling, benchmarks, methodology, measurement ROI
│           ├── techniques-algorithms.md    # Algorithms, data structures, bulk APIs, regex
│           ├── techniques-memory.md       # Compact structs, layout, arenas, bit vectors
│           ├── techniques-execution.md    # Fast paths, precompute, defer, specialize
│           ├── techniques-allocations.md  # Reduce allocs, avoid copies, reuse, pooling
│           ├── optimization-process.md    # Project selection, rollouts, automation
│           └── language-equivalents.md    # C++ → Rust → TypeScript mapping tables
└── README.md
```

**How progressive disclosure works:** The skill metadata (~100 words) is always in Claude's context. When triggered, SKILL.md adds ~1,000 words of decision tree routing. Only when a specific bottleneck is identified does the relevant reference file (~1,000–1,400 words) get loaded. Maximum context cost for a single optimization task is ~2,400 words — not 9,000.

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- No external dependencies, API keys, or build steps

---

## License

MIT
