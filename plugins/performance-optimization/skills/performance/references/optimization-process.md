# The Optimization Process

## Optimizing Optimization

Performance work itself should be optimized for return on investment. Spending time wisely means selecting the right projects, structuring rollouts for measurability, and knowing when to stop.

### Project Selection

Before starting optimization work, ask:

1. **Is the opportunity large enough?** Use back-of-envelope estimation to gauge the potential improvement. A 0.1% improvement rarely justifies weeks of effort unless the affected system is enormous.
2. **Can the change be measured?** An unmeasured optimization is a tree that fell with no one around. If production metrics cannot capture the effect, consider whether the work is worthwhile.
3. **What is the likelihood of success?** Some optimizations require deep investigation before knowing if they are feasible. Factor discovery cost into the decision.
4. **Is the operation already at its minimum?** Adding two integers cannot be made faster. Look higher in the stack for opportunities to reduce how often the operation occurs.

### Defining Success Metrics

Define success metrics before beginning work:

- **Primary metric**: The metric that ultimately matters (e.g., queries-per-CPU, end-to-end latency, throughput).
- **Proxy metrics**: Hardware counters, function-level CPU time, cache miss rates. These explain *why* the primary metric changed.
- **Align metrics with success**: If a metric tells the opposite of what a seemingly good change should show, the metric may be flawed.

## Application Productivity

### Measuring Useful Work

Optimize for how productive systems are: how much useful work accomplished per resource-second. While measuring resource consumption is straightforward, quantifying useful work requires intentional instrumentation.

- **Queries-per-CPU** is better than raw CPU time (captures both speed and work quality)
- **Records processed** is better than bytes processed (aligns with optimization goals like reading fewer fields)
- Compiler optimizations (inlining, dead code elimination) reduce instructions and improve productivity even though they increase compiler cost

### Kernel and Infrastructure Optimizations

Infrastructure changes (huge pages, thread scheduling, memory compaction) may make the infrastructure nominally more costly while dramatically improving application performance. Evaluate at the application level, not the component level.

## Optimizations Past Their Prime

Performance optimizations have a shelf life. Hardware changes, compiler improvements, and library updates can obsolete manual optimizations:

- **Prefer clear, idiomatic code**: Easier to read, debug, and for future compilers to optimize.
- **Check compiler capability first**: Before using bit-twiddling, intrinsics, or inline assembly, determine if the compiler can be taught to generate equivalent code.
- **Prefer portable solutions**: If manual optimization is needed, prefer portable code (e.g., SIMD abstraction libraries) over architecture-specific intrinsics.
- **Include benchmarks with changes**: Performance-sensitive changes should come with benchmarks demonstrating the improvement. These also detect when the optimization becomes obsolete.

## Configuration Knobs Considered Harmful

Configuration knobs for performance tuning create long-term maintenance burdens:

### Problems with Knobs

- **Stale overrides**: When a default changes (improved), callers who overrode the previous default remain pinned to worse-than-default behavior.
- **Combinatorial complexity**: Each knob multiplies the testing matrix. N binary knobs create 2^N configurations.
- **False optimization signal**: Tuning knobs gives the appearance of optimization work without addressing root causes.

### Best Practices

- **Design for outcome, not mechanism**: Express knobs in terms of desired outcome ("target latency") rather than implementation detail ("buffer size 4096").
- **Make the default optimal**: Invest in making the out-of-the-box behavior good for the common case.
- **Migrate, don't fork**: When a better implementation exists, migrate all users rather than offering both behind a flag. A complete migration eases maintenance and educational burden.
- **Sunset overrides**: Periodically audit knob overrides and remove those where the default has surpassed the override value.

## Two-Way Doors: Reversibility in Optimization

Jeff Bezos's framework: distinguish "one-way doors" (hard to reverse) from "two-way doors" (easy to reverse).

### Two-Way Door Patterns

Most software optimizations are two-way doors:

- **Feature flags**: Gate changes behind flags for easy rollback. Enables measuring impact in production without full commitment.
- **Incremental rollouts**: Roll out to a small percentage of traffic first. Detect regressions before full deployment.
- **Decoupled rollouts**: Separate the mechanism change from the policy change. Example: Deploy new code path first (off by default), then enable separately.

### One-Way Door Patterns

Some optimization decisions are hard to reverse:

- **API changes**: Once an API is public, removing or changing it requires migration of all callers.
- **Data format changes**: Changing on-disk or wire format requires backward compatibility or migration.
- **Algorithmic contracts**: Guaranteeing stable sort order or deterministic iteration means callers may depend on it.

### Decision Approach

- Prioritize blockers to landing; defer less important details.
- For one-way doors: invest in upfront analysis.
- For two-way doors: move quickly, measure, and adjust. Good decisions endure; missteps are corrected.

## Make at Most One Tradeoff at a Time

### Principle

Combining multiple changes makes it impossible to attribute effects. Each optimization should make at most one tradeoff:

- Change one variable at a time for measurability
- Export metrics along the way to track intermediate states
- Decouple changes: deploy mechanism separately from policy

### Rollout Structure

1. **Instrument**: Add metrics tracking the thing to be optimized, even before changing it.
2. **Change**: Make the single change.
3. **Measure**: Observe the effect on primary and proxy metrics.
4. **Decide**: Roll back if harmful, keep if beneficial, iterate if inconclusive.

### Real-World Pattern

Track metrics intended for future optimization even before pursuing them. Monitoring metadata memory usage and cache counts over time reveals when a problem has grown large enough to justify solving compared to other opportunities.

## Automation in Optimization

### Prevent Problems Mechanically

Automation is the first line of defense:

- **Presubmit checks**: Detect performance regressions before code lands. Example: Block configuration changes with large diffs unless explicitly overridden.
- **Continuous benchmarking**: Track benchmark results over time. Alert on regressions.
- **Automated migration**: When a better library exists, automate the migration rather than relying on manual updates.

### Keep Code Flexible

Automation helps maintain code flexibility for future optimization:

- Static analysis detecting suboptimal patterns
- Linting for known performance anti-patterns
- Automated testing of performance-critical paths

### Shift Left

Move performance validation earlier in the development cycle:
- Performance tests in CI
- Benchmark requirements for performance-critical code reviews
- Static analysis for common performance mistakes

## Spooky Action at a Distance

Performance changes can have non-local effects that are difficult to measure with standard techniques:

### Cache Pressure Effects

Changing one data structure's memory layout affects cache behavior for unrelated code sharing the same cache. This "blast radius" cannot be measured with per-request randomization.

**Measurement technique**: Process-level partitioning - some processes use only the old code, others use only the new code. This captures the full cache pressure effect, not just the direct effect on the modified code path.

### Distributed System Effects

Changing requests sent by a client to a server can dramatically impact server costs without affecting client-side metrics. Measure at the system level, not just the component making the change.

### Cross-Service Effects

Optimization in one service may increase or decrease load on dependent services. Consider the full dependency graph when evaluating impact.

## Virtuous Ecosystem Cycles

### Individual Insights, Systemic Solutions

Deep work with individual workloads produces optimization insights. Finding ways to scale these to the broader ecosystem multiplies impact:

- A fix for one application's hot path may reveal a library optimization benefiting all users
- A specialized hash function for one use case may inspire a better general-purpose implementation
- Profiling one service may expose infrastructure inefficiencies affecting everyone

### Balancing Specificity and Generality

Some optimizations trade ecosystem flexibility for specific-use performance:

- **Direct savings** (removing randomization for copy-intensive users) are clear
- **Indirect costs** (loss of randomization makes adding future optimizations harder) affect the broad ecosystem

Prefer solutions that benefit the ecosystem. When specific and general goals conflict, weigh the breadth of indirect impact against the depth of direct savings.

## Estimation in Practice

### Estimation Workflow

1. **Identify the resource**: CPU, memory, network, disk.
2. **Enumerate operations**: What operations does the code perform?
3. **Look up costs**: Use the latency reference table for order-of-magnitude costs.
4. **Multiply and sum**: Combine operation counts with per-operation costs.
5. **Sanity check**: Does the result match observed behavior within an order of magnitude?
6. **Refine**: Add detail (cache hierarchy effects, parallelism, contention) to improve accuracy.

### Calibration

After a project concludes, compare estimates to actual results:
- Do not penalize wrong estimates - the goal is learning.
- Understand why estimates were high or low.
- Adjust future estimating heuristics based on systematic over/under-estimation.
- A "surprise" in either direction may indicate an opportunity that was not noticed upfront.
