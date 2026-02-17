---
name: performance-optimization
description: >-
  This skill should be used when the user asks to "optimize", "make faster",
  "speed up", "reduce memory", "improve performance", "reduce latency",
  "improve throughput", "profile", "benchmark", or mentions "slow code",
  "too slow", "performance bottleneck", "high memory usage", "allocation
  pressure", "GC pressure", "cache misses", or "hot path". Also applicable
  when reviewing code for performance characteristics, estimating the cost
  of an operation, or selecting data structures for performance.
---

# Performance Optimization

Language-agnostic performance optimization guidance distilled from Google's Abseil performance engineering wisdom. Applicable to C++, Rust, and TypeScript.

## Core Philosophy

Forget about small efficiencies 97% of the time. But a 12% improvement, easily obtained, is never considered marginal. Choose faster alternatives when readability and complexity remain unaffected. Reserve deep optimization for the measured critical 3%.

For full philosophy, estimation techniques, and latency numbers, consult **`references/philosophy.md`**.

## The Optimization Workflow

```
1. MEASURE  →  2. IDENTIFY  →  3. OPTIMIZE  →  4. VERIFY
   Profile       Find the          Apply           Measure
   first         bottleneck        technique        again
```

### 1. Measure First

Never optimize without a baseline measurement. Profile production or representative workloads.

### 2. Identify the Bottleneck

Determine which resource is constrained: CPU, memory, network, disk. Use the appropriate profiling tool.

### 3. Apply the Right Technique

Use the decision tree below to select the appropriate reference file.

### 4. Verify the Improvement

Measure again with the same methodology. Compare primary and proxy metrics. An unmeasured optimization is worthless.

## Quick Reference: Latency Numbers

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

Extended table with additional entries and notes in **`references/philosophy.md`**.

## Decision Tree: Which Reference to Consult

**"The algorithm is wrong or suboptimal"**
→ **`references/techniques-algorithms.md`** — Algorithmic complexity, data structure selection, bulk APIs, search/iteration optimization, regex optimization.

**"Too much memory used, or memory access is slow"**
→ **`references/techniques-memory.md`** — Compact structs, field reordering, indices vs. pointers, batched storage, inlined storage, arenas, bit vectors, reducing indirections.

**"Code does unnecessary work"**
→ **`references/techniques-execution.md`** — Fast paths, precomputation, deferred computation, specialization, caching, compiler hints, stats reduction.

**"Too many allocations or copies"**
→ **`references/techniques-allocations.md`** — Avoid unnecessary allocations, reserve/resize, move vs. copy, reuse temporaries, object pooling.

**"Need to measure or profile correctly"**
→ **`references/measurement.md`** — Profiling methodology, flat profiles, microbenchmarking, hardware counters, measurement ROI, decision-making with imperfect data.

**"Need to think about the optimization approach"**
→ **`references/optimization-process.md`** — Project selection, success metrics, reversibility, rollout strategy, automation, estimation calibration.

**"Need the equivalent technique in another language"**
→ **`references/language-equivalents.md`** — C++ → Rust → TypeScript mapping for all techniques, applicability matrix, TypeScript-specific concerns.

**"Need to understand the performance mindset"**
→ **`references/philosophy.md`** — The critical 3%, performance-aware design, back-of-envelope estimation, latency reference table, structural thinking.

## Optimization Categories at a Glance

| Category | Key Insight | Impact |
|----------|------------|--------|
| Algorithm/data structure | Reduce complexity class (O(N²) → O(N)) | 10-1000x |
| Memory representation | Smaller = fewer cache misses = faster everything | 2-10x |
| Avoid unnecessary work | Fast paths, precompute, defer, specialize | 2-20x |
| Reduce allocations | Each alloc costs time + cache + GC pressure | 1.2-5x |
| Bulk APIs | Amortize per-item overhead across N items | 2-10x |
| Measurement methodology | Measure the right thing the right way | Enables all above |

## Process Checklist

When undertaking performance optimization work:

- [ ] Define primary success metric before starting
- [ ] Estimate expected improvement (back-of-envelope)
- [ ] Profile to identify the actual bottleneck (do not guess)
- [ ] Apply one technique at a time for measurability
- [ ] Measure after each change with pre-defined methodology
- [ ] Compare estimate to actual result for calibration
- [ ] Consider non-local effects (cache pressure, distributed system impacts)
- [ ] Prefer two-way door decisions (reversible via feature flags)

## Language-Specific Quick Notes

**Rust**: Move semantics are default. Use `Vec::with_capacity`, `smallvec`, `bumpalo` for allocation control. `hashbrown` (default `HashMap`) uses SwissTable internally. Profile with `perf`, `criterion`, `flamegraph`. LLVM backend shared with C++ enables `llvm-mca` analysis.

**TypeScript**: Focus on algorithmic complexity, V8 hidden class stability (monomorphic objects), GC pressure reduction, and TypedArrays for numeric work. Most C++ memory-layout techniques do not apply. Profile with Chrome DevTools and `clinic.js`. Bundle size affects parse/compile time.

**C++**: Full access to all techniques. Use `absl::` types (InlinedVector, flat_hash_map, Span, string_view) for efficient defaults. Profile with `pprof` and `perf`. Use `llvm-mca` for instruction-level analysis.

For comprehensive cross-language mapping, consult **`references/language-equivalents.md`**.

## All Reference Files

| File | Content | Words |
|------|---------|-------|
| **`references/philosophy.md`** | Mindset, critical 3%, estimation, latency numbers | ~860 |
| **`references/measurement.md`** | Profiling, benchmarks, methodology, measurement ROI | ~1,200 |
| **`references/techniques-algorithms.md`** | Algorithms, data structures, bulk APIs, regex | ~1,000 |
| **`references/techniques-memory.md`** | Compact structs, layout, arenas, bit vectors, indirections | ~1,300 |
| **`references/techniques-execution.md`** | Fast paths, precompute, defer, specialize, caching | ~1,200 |
| **`references/techniques-allocations.md`** | Reduce allocs, avoid copies, reuse, pooling | ~1,100 |
| **`references/optimization-process.md`** | Project selection, rollouts, automation, estimation | ~1,400 |
| **`references/language-equivalents.md`** | C++ → Rust → TypeScript mapping tables | ~1,000 |
