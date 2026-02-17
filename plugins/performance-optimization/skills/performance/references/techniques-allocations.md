# Allocation Reduction Techniques

## Why Allocations Are Expensive

Each heap allocation incurs three categories of cost:

1. **Allocator overhead**: Time spent in malloc/free (lock acquisition, free-list traversal, bookkeeping). Even fast allocators (tcmalloc, jemalloc, mimalloc) cost 15-50 ns per allocation.
2. **Initialization and destruction**: Constructors, destructors, and zero-filling. For small objects, this may exceed the allocator cost.
3. **Cache footprint expansion**: Each allocation occupies at least one cache line (64 bytes typically). More allocations mean more cache lines touched, evicting useful data.

Reducing allocations improves not just the code doing the allocation but also co-located code that benefits from better cache utilization.

## Avoid Unnecessary Allocations

### Cache Frequently-Created Objects

When the same object is repeatedly constructed and destroyed with identical content:

- **Static instance caching**: Instead of creating a new shared pointer on every call that needs a default value, cache a static instance and return references to it. Real-world result: 21% throughput increase from caching an empty `DeviceInfo`.
- **Statically-allocated zero data**: For operations that frequently need a zeroed buffer of a common size, allocate once statically rather than per-operation.

### Avoid Allocation in Hot Paths

Identify hot paths through profiling and eliminate allocations within them:

- Replace `make_shared`/`make_unique` with stack allocation when object lifetime is bounded by the scope
- Replace `String::new()` / `new String()` with pre-allocated buffers
- Replace temporary containers with fixed-size stack arrays when the maximum size is bounded

## Resize and Reserve Containers

### Pre-Size When Capacity Is Known

When the maximum or expected size of a container is known before filling it:

```
// Instead of:
let mut results = Vec::new();
for item in items {
    results.push(process(item));
}

// Pre-allocate:
let mut results = Vec::with_capacity(items.len());
for item in items {
    results.push(process(item));
}
```

This eliminates reallocation and copying during growth.

### Patterns

- **`reserve` + `push`**: Pre-allocate capacity, then append elements. Avoids reallocation without initializing elements.
- **`resize` + index assignment**: Pre-allocate and initialize, then fill by index. Avoids bounds checking in tight loops when using unchecked access.
- **Direct pointer fill**: For maximum performance, reserve capacity and fill via pointer arithmetic, bypassing per-element method call overhead.

### Pitfalls

- **Do not reserve one-at-a-time**: Calling `reserve(size + 1)` before each `push` causes quadratic cost (allocator called N times, each potentially copying all elements).
- **Do not use `resize` when `reserve` suffices**: `resize` default-constructs elements that will be immediately overwritten. Use `reserve` followed by `push_back`/`push` to construct elements once.
- **Beware over-reservation**: Reserving 10x the needed capacity wastes memory and cache space. Estimate conservatively when exact size is unknown.

## Avoid Copying

### Move Instead of Copy

When transferring ownership, move rather than copy. Moving transfers the internal buffer pointer rather than duplicating the data.

| Language | Move Semantics |
|----------|---------------|
| C++ | `std::move(obj)` - explicit, must use |
| Rust | Move is default - automatic, copies require explicit `Clone` |
| TypeScript | Object references are shared (no deep copy by default) |

### Sort Indices, Not Objects

When sorting large objects, sort a vector of indices into the original array instead:

```
// Instead of sorting large structs:
items.sort_by_key(|item| item.score);

// Sort indices:
let mut indices: Vec<usize> = (0..items.len()).collect();
indices.sort_by_key(|&i| items[i].score);
```

This avoids moving large objects during sort swaps.

### Avoid Unnecessary Intermediate Copies

- **gRPC/serialization**: Pass data directly to the transport layer rather than serializing to a buffer and then copying the buffer. Real-world result: 10-15% speedup for ~400KB tensors.
- **Move large options structs**: Pass configuration structs by move rather than by copy when the caller does not need them afterward.
- **Prefer `sort` over `stable_sort`**: Stable sort may allocate internal storage for the stability guarantee. If ordering of equal elements does not matter, use unstable sort.

### View Types at API Boundaries

Accept borrowed/view types in function signatures to avoid requiring callers to allocate matching container types:

- Accept `&str` / `string_view` instead of `String` / `std::string`
- Accept `&[T]` / `Span<T>` instead of `Vec<T>` / `vector<T>`
- Return views when the data outlives the call

## Reuse Temporary Objects

### Hoist Allocations Out of Loops

Objects declared inside loops are reconstructed every iteration, incurring allocation and initialization cost each time:

```
// Before: allocation per iteration
for item in items {
    let mut buffer = String::new();
    serialize(item, &mut buffer);
    send(buffer);
}

// After: reuse across iterations
let mut buffer = String::new();
for item in items {
    buffer.clear();
    serialize(item, &mut buffer);
    send(&buffer);
}
```

The reused buffer grows to accommodate the largest item and stays at that capacity for subsequent iterations.

### Protobuf/Container Reuse Pattern

Containers like protobuf messages, strings, and vectors grow to their largest-ever size and retain that capacity through `clear()`:

- **Benefit**: Avoids re-allocation for subsequent uses of equal or smaller size
- **Risk**: If one outlier use is very large, all subsequent uses retain the oversized allocation

**Mitigation**: Periodically reconstruct the container (e.g., every N iterations) to release oversized buffers:

```
let mut buffer = String::new();
for (i, item) in items.iter().enumerate() {
    if i % 1000 == 0 {
        buffer = String::new(); // Release oversized buffer periodically
    }
    buffer.clear();
    serialize(item, &mut buffer);
    send(&buffer);
}
```

## Object Pooling (TypeScript/GC Languages)

In garbage-collected languages, allocation is cheap but GC pressure is expensive. Object pooling reduces GC pressure:

### When to Pool

- Hot loops creating many short-lived objects of the same type
- Objects with expensive initialization (WebSocket connections, worker threads)
- Real-time constraints where GC pauses are unacceptable (game loops, audio processing)

### Pooling Pattern

```typescript
class ObjectPool<T> {
    private pool: T[] = [];
    constructor(private factory: () => T, private reset: (obj: T) => void) {}

    acquire(): T {
        return this.pool.pop() ?? this.factory();
    }

    release(obj: T): void {
        this.reset(obj);
        this.pool.push(obj);
    }
}
```

### Pitfalls

- **Pool sizing**: Unbounded pools waste memory. Cap the pool and let excess objects be GC'd.
- **Reset discipline**: Failing to fully reset pooled objects causes subtle bugs.
- **Premature optimization**: In most TypeScript applications, GC handles short-lived objects efficiently. Profile before pooling.

## Allocation-Aware Data Structure Choice

| Need | Allocation-Heavy | Allocation-Light |
|------|-----------------|-----------------|
| Key-value store | `HashMap` (node-based) | `Vec<(K, V)>` sorted, flat hash map |
| Set | `HashSet` (node-based) | Bit vector, sorted `Vec` |
| Graph | Node objects with pointer edges | Adjacency list in `Vec<Vec<usize>>` |
| String collection | `Vec<String>` (N+1 allocations) | Single `String` with offset table |
| Optional fields | `Box<T>` / heap pointer | Inline with sentinel value |
