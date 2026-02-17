# Algorithmic and Data Structure Techniques

## Algorithmic Complexity Improvements

The highest-impact optimizations come from algorithmic improvements: reducing the computational complexity class of an operation.

### Identify the True Complexity

Before optimizing constants, verify the algorithm's complexity class is appropriate:

- **O(N^2) hidden in loops**: Nested iterations over the same data, repeated linear scans inside a loop, or string concatenation in a loop can hide quadratic behavior.
- **O(N log N) where O(N) suffices**: Sorting to find a maximum, sorting to deduplicate when a hash set would work.
- **O(log N) where O(1) is available**: Tree-based lookups where a hash table or array index would work.

### Real-World Algorithmic Improvements

**Replace incremental with batch construction**: Code that builds a graph structure incrementally by looping over nodes and edges can often be restructured to build in one shot. This removes internal per-edge checks and enables the implementation to use more efficient algorithms (e.g., reverse post-order initialization makes cycle detection trivial since ranks are pre-assigned in topological order).

**Replace sorted-list intersection with hashing**: O(N log N) node-source-sharing detection becomes O(N) by hashing one side and probing with the other. Real-world result: 21% latency reduction.

**Replace tree-based map with hash map**: O(log N) lookups become O(1). When replacing an interval map with a hash table, adjacent-block coalescing still works via hash lookup for adjacent keys. Real-world result: ~4x throughput improvement.

**Replace O(|V|^2) with O(|V|+|E|)**: A deadlock detection algorithm replaced its O(|V|^2)-space approach with dynamic topological sort. Scaled from a 2K node limit to millions of nodes. Performance went from 23,553 ns/edge at 2K to 534 ns/edge at 1M.

## Data Structure Selection

### Decision Framework

| Situation | Preferred Structure | Avoid |
|-----------|-------------------|-------|
| Key-value with string/complex keys | Flat hash map | Tree-based map (unless ordering needed) |
| Small domain (enum, small int range) | Array indexed by key | Any map type |
| Set over small integer domain | Bit vector | Hash set, tree set |
| Ordered iteration required | B-tree map | Linked list, skip list |
| Frequent iteration, rare insert | Sorted vector | Tree-based containers |
| Many small instances | Inlined/small-buffer container | Heap-allocated container |

### Hash Table Choice

Proper hash tables provide O(1) expected-time operations. Key considerations:

- **Hash function quality**: A poor hash function causes clustering and degrades to O(N). Use a well-tested hash (SwissTable uses wyhash, Rust's hashbrown uses the same algorithm).
- **Open addressing vs. chaining**: Open-addressing (flat) tables store entries inline, improving cache locality. Chaining tables allocate per entry.
- **Load factor**: Higher load factors save memory but increase probe lengths. Most good implementations auto-tune this.

### Flatten Nested Maps

Converting `Map<A, Map<B, C>>` to `Map<Pair<A, B>, C>` reduces allocation/insertion costs significantly. One allocation per entry instead of one map per outer key.

**When flattening helps**: When the outer key space is large relative to typical inner map sizes.

**When nesting is better**: When the first key has few values and each inner map is large (avoids duplicating the outer key in every compound key).

## Bulk API Design

### Why Bulk APIs Matter

Per-item API calls incur fixed costs:
- Function call overhead (frame setup, register saves)
- Lock acquisition/release per call
- Cache line loads for per-call metadata
- Missed algorithmic optimization opportunities

Bulk APIs amortize these costs across N items.

### Patterns

**Batch lookup**: Instead of `Lookup(id) -> Result` called N times, provide `LookupMany(ids[]) -> Results[]`. Enables:
- Single lock acquisition
- Prefetching of multiple keys
- Sorted-order access for cache-friendly traversal

**Batch mutation**: Instead of `Delete(ref)` called N times, provide `DeleteRefs(refs[])`. Amortizes locking overhead within a single mutex acquisition.

**Cache decode results**: Store decoded/parsed entries for future lookups rather than re-processing. Example: Cache block decode results so subsequent lookups reuse parsed data.

### View Types for Zero-Copy APIs

Accept borrowed references instead of owned containers in function parameters:

| Language | View Type | Owned Type |
|----------|-----------|------------|
| C++ | `string_view`, `Span<T>`, `FunctionRef` | `string`, `vector<T>`, `function` |
| Rust | `&str`, `&[T]`, `&dyn Fn()` | `String`, `Vec<T>`, `Box<dyn Fn()>` |
| TypeScript | `Readonly<T[]>` (conceptual) | `T[]` |

Benefits:
- Eliminate copies at API boundaries
- Allow callers to choose their container type
- Enable passing subranges without allocation

### Pre-Allocated Arguments

Pass already-available data to low-level routines to avoid recomputation. If a caller has already computed a value the callee would need to recompute, pass it as a parameter.

Example: A stats-recording function that needs the current wall time. If the caller already has the time, provide a variant that accepts it rather than calling the time function again.

## Search and Iteration Optimization

### Search Order Matters

Counter-intuitively, searching a larger index first can be faster if it allows skipping a smaller index. If the larger index is a superset of the smaller one, exhausting the larger index means the smaller one is unnecessary. Real-world result: 19% throughput improvement by searching full-text before title/anchor tiers.

### Reduce Iteration Work

- **Filter early**: Check a cheap condition before expensive processing. Example: Array lookup on first byte of a token to filter before expensive fingerprinting.
- **Break early**: Exit loops as soon as the answer is determined.
- **Batch iteration**: Process elements in chunks rather than one at a time to amortize loop overhead.

## Regular Expression Optimization

Regular expressions are a common source of unexpected cost:

- **Anchor patterns**: `^pattern$` anchors avoid scanning the entire input.
- **Avoid `.` when possible**: In UTF-8 mode, `.` matches multi-byte characters, requiring byte-by-byte automaton stepping. Literal character classes are faster.
- **Minimize capturing groups**: Each capture group adds tracking overhead. Use non-capturing `(?:...)` when the match content is not needed.
- **Prefix matching shortcut**: For patterns like `prefix.*`, a simple prefix check is vastly cheaper than a full regex match.
- **Pre-compile patterns**: Compile regex patterns once and reuse. Never compile inside a loop.
