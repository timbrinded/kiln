# Execution Optimization Techniques

## Fast Paths for Common Cases

Code that handles all cases uniformly pays the cost of generality even for simple inputs. Structure code to optimize the common path without hurting uncommon cases.

### Principles

1. **Identify the common case**: Profile or reason about what inputs occur most frequently.
2. **Handle it first**: Place the common case in an `if` branch at the top, with the general fallback below.
3. **Keep the fast path small**: Smaller code means fewer instruction cache misses. Move the slow path to a separate function.
4. **Avoid false generality**: If 95% of inputs are single-byte, do not force them through a multi-byte decoder.

### Patterns

**Early return on common case**:
```
// Fast path: most tokens are not special
if (!is_special_token(input[0])) {
    return handle_normal(input);
}
// Slow path: full analysis
return handle_special(input);
```

**Sentinel/flag check before expensive work**:
```
// Skip expensive error processing if no errors
if (!any_errors_set) return;
for (auto& error : errors) { ... }
```

**Array lookup for filtering**: Use a 256-element boolean array indexed by the first byte to gate whether full processing is needed. A single memory access replaces a complex condition or function call.

### Real-World Examples

- **UTF-8 ASCII scanning**: Extend the fast path to handle trailing single ASCII bytes, avoiding the slower generic multi-byte routine for short all-ASCII strings.
- **Varint parsing**: Minimize the fast path to single-byte case only. Multi-byte parsing defers to a separate `ParseSlow` function, reducing code size and icache pressure.
- **InlinedVector resize**: Simpler fast paths for common resize operations, avoiding transaction machinery that is only needed for exception safety in complex cases.

## Precompute Expensive Information

### At Initialization Time

Compute derived data during setup rather than on every use:

- **Pre-compute boolean flags**: If checking `kernel->is_expensive()` happens per execution step, compute it once during graph initialization and store as a bit-field.
- **Build lookup tables**: Replace repeated function calls in inner loops with table lookups. Example: A 256-element probability array replaces per-character `Prob()` calls.
- **Validate at module boundaries**: Check inputs once at entry points rather than re-validating deep inside call stacks.

### Hoist Computations Out of Loops

Move invariant computations outside loop bodies:

```
// Before: recomputed every iteration
for (i in 0..n) {
    let dim = shape.dimension(dimension_numbers.front());
    process(data[i], dim);
}

// After: computed once
let dim = shape.dimension(dimension_numbers.front());
let data_ptr = data.as_ptr();
for (i in 0..n) {
    process(data_ptr[i], dim);
}
```

Caching pointers to buffer data avoids repeated bounds checking and offset calculation.

## Defer Expensive Computation

The opposite of precomputation: delay work until it is actually needed.

### When Deferring Wins

- **Conditional computation**: If expensive work is only needed for a subset of cases, compute lazily. Example: Defer `GetSubSharding()` until confirming the relevant operand matches. Real-world result: CPU time dropped from 43 seconds to 2 seconds.
- **On-demand statistics**: Instead of updating stats on every allocation/deallocation, compute when the less-frequent `Stats()` method is called.
- **Conservative initial allocation**: Start with small allocations and grow. Example: Reducing initial parse tree node pool from 200 to 10 yielded 7.5% CPU reduction for a web server.

### Lazy Initialization

Construct expensive objects only when first accessed. Useful for:
- Configuration objects that may never be queried
- Cache structures that may never be needed
- Optional features that most code paths skip

## Specialize Code

When a call-site does not need the full generality of a library function, a specialized version can be dramatically faster.

### Patterns

**Type-specific formatting**: Custom integer-to-string conversion is 4x faster than `sprintf`/`format!`. Encode digits directly instead of parsing format strings.

**Pattern-specific matching**: For simple prefix patterns, a string prefix check is vastly cheaper than a full regex match. Detect common patterns and dispatch to specialized implementations.

**Hash function specialization**: A general-purpose hash may be suboptimal for specific key distributions. Specialized hash functions (e.g., Murmur hash with domain-specific feature encoding) improve distribution.

**Compile-time specialization**: When a parameter is a compile-time constant, specialized code paths avoid runtime checks. C++: `__builtin_constant_p`, Rust: `const` generics, TypeScript: N/A (JIT handles this).

## Caching to Avoid Repeated Work

### Application-Level Caching

Cache the results of expensive computations keyed by their inputs:

- **Fingerprint-based caching**: Compute a fingerprint of the input and check a cache before doing expensive work. Example: Cache proto parsing results using proto fingerprint as key.
- **Memoization**: For pure functions with repeated inputs, store results in a hash map keyed by arguments.

### Caching Pitfalls

- **Cache invalidation**: If underlying data changes, cached results become stale. Ensure clear invalidation strategy.
- **Memory pressure**: Unbounded caches grow until they cause memory problems. Use LRU eviction or size limits.
- **Cache thrashing**: If the working set exceeds cache capacity, every access is a miss. Right-size the cache or accept the miss rate.

## Making the Compiler's Job Easier

Compilers optimize conservatively due to aliasing rules and incomplete information. Help the compiler generate better code:

### Reduce Function Call Overhead

- **Avoid function calls in hot paths**: Each call has frame setup cost (register saves, stack adjustment). Inline small functions or use `__attribute__((always_inline))` / `#[inline(always)]`.
- **Separate slow paths**: Move unlikely code to a separate function. Mark it `__attribute__((noinline))` / `#[cold]`. This keeps the hot path compact for icache.
- **Tail calls for slow paths**: If the slow path is the last thing in a function, structure it as a tail call to avoid frame setup.

### Help Aliasing Analysis

- **Copy to local variables**: Copy small data from pointers/slices to local variables before heavy use. This tells the compiler the values cannot change through aliasing, enabling register allocation and auto-vectorization.
- **Use raw pointers over slices in innermost loops**: When the compiler cannot prove that a slice reference does not alias with other data, raw pointers with known bounds enable better optimization (applies to C++ and Rust).

### Hand-Unrolling Hot Loops

In critical inner loops where the compiler's unroller is insufficient:

- Process multiple elements per iteration (e.g., 16 bytes at a time, then 4, then 1)
- Use SIMD intrinsics for parallel processing when available
- Process from the end when the interesting data is typically near the end (e.g., scanning for separators in long strings)

**Caveat**: Hand-unrolling reduces readability and portability. Reserve for measured critical paths only.

## Reduce Stats Collection Costs

### Balance Utility Against Overhead

Stats collection has real cost: counter increments, lock acquisitions, memory for counters. Balance their diagnostic value against runtime overhead.

- **Drop unused stats**: Stats that nobody reads should be removed. Example: Removing alarm count stats contributed to reducing alarm-setting time from 771 ns to 271 ns.
- **Sample instead of counting everything**: Maintain stats for a sample of events rather than all events. Use power-of-two sampling rates (e.g., 1-in-32) for fast modulus via bitwise AND.
- **Defer aggregation**: Accumulate raw events and aggregate on-demand rather than maintaining running aggregates.

### Sampling Patterns

Most monitoring subsystems use sampling:
- Memory allocator tracking (tcmalloc tracks a sample of allocations)
- Request tracing (Dapper samples a fraction of requests)
- CPU profiling (periodic sampling, not per-instruction tracking)

Reducing sampling rate (e.g., from 1-in-10 to 1-in-32) can significantly reduce overhead for high-frequency operations like packet processing in real-time systems.
