# Performance Philosophy

## The Critical 3%

Knuth's often-misquoted principle: "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil." The full context is essential: **a 12% improvement, easily obtained, is never considered marginal** in established engineering disciplines.

The misinterpretation leads to deferring all performance work until profiling reveals a hotspot. This creates problems:

- **Flat profiles emerge**: Large systems developed without performance awareness distribute cost thinly across thousands of functions. No single function dominates, making optimization appear impossible.
- **Library code is opaque**: Users of library code cannot easily modify external implementations. By the time a library becomes a bottleneck, switching has high cost.
- **Inertia compounds**: System changes become harder after deployment. Early architectural decisions (data format choices, API boundaries, allocation patterns) constrain future optimization options.
- **Overprovisioning masks waste**: Throwing hardware at a slow system is expensive and obscures opportunities for algorithmic improvement.

**The productive stance**: Choose faster alternatives when readability and complexity remain unaffected. Reserve deep optimization for the measured critical 3%.

## Performance-Aware Design

Performance awareness does not mean premature optimization. It means:

1. **Choose efficient defaults**: Prefer `flat_hash_map` over `unordered_map`, `Vec::with_capacity` over repeated `push`, pre-allocated arrays over dynamic maps for small domains.
2. **Design deep modules**: Organize code so performance improvements fit within encapsulation boundaries. Significant functionality through narrow interfaces enables optimization without API changes.
3. **Expose bulk APIs**: Single-item APIs force callers into per-item overhead (function calls, lock acquisitions, cache misses). Bulk APIs amortize fixed costs and enable algorithmic improvements.
4. **Prefer view types**: Accept borrowed references (`string_view`, `&str`, `Span<T>`) over owned containers in function parameters. Eliminate unnecessary copies at API boundaries.

## Back-of-Envelope Estimation

Estimation guides where to invest optimization effort. The goal is better decisions, not perfect-in-hindsight ones.

### Latency Reference Numbers

Approximate latencies for common operations (order of magnitude):

| Operation | Latency | Notes |
|-----------|---------|-------|
| L1 cache reference | 0.5 ns | |
| L2 cache reference | 3 ns | ~6x L1 |
| Branch mispredict | 5 ns | |
| Mutex lock/unlock | 15 ns | Uncontended |
| Main memory reference | 50 ns | ~100x L1 |
| Compress 1KB (Snappy) | 1,000 ns | 1 us |
| Read 4KB from SSD | 20,000 ns | 20 us |
| Datacenter round trip | 50,000 ns | 50 us |
| Read 1MB sequentially (memory) | 64,000 ns | 64 us |
| Read 1MB over 100 Gbps network | 100,000 ns | 100 us |
| Read 1MB from SSD | 1,000,000 ns | 1 ms |
| Disk seek | 5,000,000 ns | 5 ms |
| Read 1MB from disk | 10,000,000 ns | 10 ms |
| Send packet CA-Netherlands-CA | 150,000,000 ns | 150 ms |

### Estimation Technique

Break the problem into operations with known costs. Multiply and sum.

**Example: Sorting 1 billion 4-byte integers**

- Memory bandwidth: 4GB array, ~16GB/s throughput, ~30 passes for quicksort = ~7.5 seconds
- Branch mispredictions: ~15 billion mispredicts at 5ns each = ~75 seconds
- Total estimate: ~82 seconds
- Refinement (L3 cache fits working set): reduces memory cost to ~2.5 seconds

**Example: Loading 30 image thumbnails**

- Sequential disk reads: 30 x 15ms (5ms seek + 10ms transfer) = 450ms
- Parallel across K disks: ~15ms expected latency
- SSD variant: 30 x (20us + 1ms) = ~30ms total

### Why Estimate?

- **Prioritize projects**: Given finite time, pursue highest return-on-investment first. Estimation fills in "return" before results are in hand.
- **Gauge complexity tolerance**: An estimate of 15% savings justifies more complexity than an estimate of 0.5%.
- **Identify opportunities**: Knowing the size of a problem domain reveals where to look.
- **Calibrate intuition**: After a project concludes, compare estimates to actuals. Learn from misses without penalizing errors. The goal is to improve the thought process.

## The Optimization Mindset

### Measure Before and After

An unmeasured optimization is a tree that fell with no one around. Measurement:
- Confirms the optimization had the intended effect (not coincidence from another change)
- Prevents anchoring bias (actual data may be better or worse than anticipated)
- Provides calibration data for future estimates

### Prefer Clear Code

Prefer writing clear, idiomatic code whenever possible. It is:
- Easier to read and debug
- Easier for the compiler to optimize in the long run
- More likely to benefit from future language/runtime improvements

Reserve low-level tricks for measured hotspots where the compiler cannot be taught to perform the optimization.

### Think in Systems

A locally expensive operation may improve system-wide performance. Example: TCMalloc's "expensive" prefetch makes allocation look slower in profiles but improves application throughput by reducing cache misses at the point of use. Always measure at the system level, not just the component level.

### Structural Changes Over Micro-Optimizations

When profiles show no obvious hotspot, look for structural changes higher in the call stack:
- Replace incremental graph construction with batch initialization
- Replace per-item processing with bulk processing
- Replace general-purpose code with specialized implementations for common cases
- Reduce allocation pressure to improve cache behavior system-wide
