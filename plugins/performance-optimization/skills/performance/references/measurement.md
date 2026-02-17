# Measurement and Profiling

## Measurement Methodology

### First Principles

Measurement serves decision-making: roll back an unhelpful change, double down on a productive area, or prioritize between competing projects. The precision needed depends on the decision at stake.

- **Getting the big picture right** matters more than precision. A 2x error in measuring a large optimization changes decisions more than a 7th digit of precision on a small one.
- **Significant figures**: Most techniques provide only 1-2 significant digits of accuracy. Treat results accordingly.
- **Publish methodology before results**: Pre-registering how measurements will be conducted prevents post-hoc analysis manipulation. "Clearly errant outlier data points can be deleted" sounds reasonable but can undermine experiment soundness.

### Primary and Proxy Metrics

- **Primary metrics** measure what ultimately matters: queries-per-CPU, useful work per resource-second, end-to-end latency.
- **Proxy metrics** (CPU time in a function, cache misses, branch mispredictions) help confirm and explain changes but should not be confused with primary outcomes.
- **Metrics must align with success**: If a metric tells you to do the opposite of a seemingly good thing, the metric is flawed. Example: "bytes processed" penalizes reading fewer fields per record, while "records processed" correctly reflects that less work per record is good.

### The Jelly Beans Trap

Testing multiple hypotheses on the same data increases the chance of finding spurious significance. Avoid:
- Running many A/B tests and cherry-picking the one that "worked"
- Measuring many metrics and celebrating the one that improved
- Re-analyzing the same data with different cuts until something looks significant

**Countermeasure**: Pre-specify what you expect to see. If results are surprising in either direction, investigate further rather than celebrating or dismissing.

### Anchoring Bias

Estimation is useful for planning, but do not let estimates bias measurement interpretation. The actual data may differ from expectations. Reality is what matters.

- A higher-than-expected result might come from a missed consideration (e.g., huge page-backed text reducing both iTLB and dTLB misses)
- A lower-than-expected result might stem from optimistic assumptions
- Extraordinary claims in either direction require extraordinary evidence

## Profiling

### Getting Started

1. **Build with debug info and optimizations**: Production binaries with symbols enable meaningful profiles without sacrificing performance characteristics.
2. **Start with CPU profiles** (pprof, perf, or equivalent): Identify which functions consume the most time.
3. **Get allocation profiles**: Memory allocation pressure causes cache misses across the entire system. Allocation profiles reveal where memory is allocated and how much.
4. **Gather hardware counter profiles**: Cache misses, branch mispredictions, TLB misses, and instructions retired provide insight into low-level bottlenecks.

### Handling Flat Profiles

When no single function dominates:

- **Value cumulative 1% improvements**: In a flat profile, many 1% improvements compound. Twenty 1% improvements yield ~18% total.
- **Use flame graphs**: Look for loops near the top of call stacks. The loop or the code it calls could potentially be restructured.
- **Look for structural changes**: Step back from micro-optimizations. Seek changes higher in the call stack (batch initialization, algorithmic replacement).
- **Check allocation profiles**: Even if CPU is evenly spread, concentrated allocations may cause widespread cache pressure.
- **Profile lock contention**: Some mutex implementations support contention profiling. High contention indicates serialization bottlenecks.

### In-Process Profiling

Sampling strategies for profiling within a running process:

- **Duration vs. duration-less**: Some profilers track events over a time window; others capture instantaneous snapshots.
- **Sampling reduces overhead**: Collecting some data, even heavily sampled, is useful for gauging behavior at scale.
- **Design upfront**: Decide sampling rate and duration before collecting data to avoid bias.

### Profiling Pitfalls

- **Heap profiling and reference counting**: For long-lived reference-counted objects, heap profiles show where memory was allocated, not what code holds it alive. The code holding the last reference may be unrelated to the allocation site.
- **Non-local effects**: Changes to allocators, compilers, or shared libraries affect profiles across the entire application. A function appearing more expensive may simply be the victim of cache pressure from elsewhere.
- **Spooky action at a distance**: Changing one data structure's memory layout can affect performance of unrelated code through shared cache effects. Process-level partitioning (not per-request randomization) is needed to measure these "blast radius" effects.

## Microbenchmarking

### Purpose

Microbenchmarks trade fidelity for speed. A 90%-accurate oracle that responds in 10 minutes enables better decisions than a 99%-accurate one that takes a month. Use microbenchmarks to:

- Quickly explore the solution space before committing to production experiments
- Verify that a change improves the targeted operation
- Prevent performance regressions in CI
- Isolate specific operations for hardware counter analysis

### How to Microbenchmark Well

1. **Test individual properties**: Do not benchmark entire workflows. Isolate the specific operation (iterator creation, lookup, insertion).
2. **Observe production behavior**: Use profiles to determine which operations are actually critical in production before benchmarking.
3. **Use benchmark frameworks**: Google Benchmark (C++), Criterion (Rust), Benchmark.js/vitest (TypeScript) standardize iteration, warmup, and statistical analysis.
4. **Include benchmarks with changes**: Every performance-sensitive change should come with a microbenchmark demonstrating the improvement.

### Microbenchmark Pitfalls

- **Unrealistic conditions**: Benchmarks run in isolation with warm caches, no contention, and no background work. Production conditions differ dramatically.
- **Compiler elimination**: The compiler may optimize away work that has no observable effect. Use `benchmark::DoNotOptimize` (C++), `std::hint::black_box` (Rust), or similar constructs.
- **Misleading metrics**: A prefetch that increases time spent in `malloc` but improves application throughput would look bad in a microbenchmark but good in production.
- **Missing the system**: A microbenchmark cannot capture cache pressure from co-running workloads, memory bandwidth contention, or thermal throttling.

### Hardware Performance Counters

For precise measurement of low-level effects:

- **Cycles, instructions retired**: Basic throughput metrics
- **Cache misses** (L1, L2, LLC): Identify memory access pattern problems
- **Branch mispredictions**: Identify unpredictable branch patterns
- **TLB misses**: Identify memory mapping overhead

**Limitations**: At most 32 events simultaneously. Hardware typically has 4-8 physical counters; requesting more causes multiplexing and reduced accuracy. Counting mode only (where, not which code location).

## Measurement ROI

Measurement itself has a return on investment:

- **High ROI**: Spending a small effort to realize a 2x difference in measured results is easier than finding another equally-sized optimization from scratch.
- **Low ROI**: Spending twice the effort to refine measurement of a small optimization is poor ROI. Added precision is lost in the noise of larger effects.
- **Missing numbers**: Numbers off the page matter more than precision of numbers on the page. Do not overlook large positive or negative externalities while polishing small numbers.

## Decision Making with Imperfect Data

Optimization decisions must often be made without perfect data:

- **Avoid confirmation bias**: Look for evidence that could change the plan, not just evidence that confirms it.
- **Representative data**: Measure effects on the wider population or a broadly representative set, not just one favorable case.
- **Negative results where there is no opportunity**: If an optimization cannot affect a test case, a negative result on that case is meaningless. Do not abandon a good idea based on spurious negatives.
- **Scaling effects**: An optimization may falter at broader scale if initial data points were biased by streetlamp effects (measuring only where the light is).
