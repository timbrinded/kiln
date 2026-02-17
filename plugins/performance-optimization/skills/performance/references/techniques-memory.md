# Memory Representation and Layout Techniques

## Why Memory Layout Matters

Memory representation affects performance through three mechanisms:

1. **Cache efficiency**: Smaller data structures touch fewer cache lines. A cache line is typically 64 bytes. Every unnecessary byte in a hot structure reduces the number of useful entries that fit in cache.
2. **Memory bandwidth**: Data must travel from DRAM to CPU. Smaller representations move faster. At scale, memory bandwidth is often the binding constraint.
3. **Allocation overhead**: Each heap allocation has metadata overhead (typically 8-16 bytes) and forces cache line alignment. Fewer allocations mean less overhead and better cache packing.

## Compact Data Structures

### Field Reordering

Compilers insert padding between fields of different alignment requirements. Reordering fields from largest to smallest alignment minimizes padding.

```
// Before: 24 bytes (with padding)
struct Event {
    bool active;       // 1 byte + 7 padding
    double timestamp;  // 8 bytes
    int32_t id;        // 4 bytes + 4 padding
};

// After: 16 bytes (no wasted padding)
struct Event {
    double timestamp;  // 8 bytes
    int32_t id;        // 4 bytes
    bool active;       // 1 byte + 3 trailing padding
};
```

### Smaller Numeric Types

Use the smallest representation that fits the data:

- Enum values rarely need 32 bits. Use `uint8_t` backing (C++: `enum class OpType : uint8_t`, Rust: `#[repr(u8)] enum OpType`).
- Counts that fit in 16 bits do not need 64-bit integers.
- Tensor dimensions that fit in 16 bits can be packed (4 dimensions in 8 bytes instead of 32).

### Bit-Level Encoding

When data has known value ranges, pack multiple values into fewer bytes:

- Boolean flags: pack 8 into a single byte
- Small enums: pack multiple into a byte
- Fixed-point representations for bounded floating-point values

Encapsulate bit manipulation behind clean APIs. Validate through benchmarks that the encoding/decoding cost is offset by cache improvement.

### Hot/Cold Field Separation

**Hot field proximity**: Place frequently-accessed-together fields adjacent so they share cache lines.

**Hot/cold separation**: Separate frequently-accessed mutable fields from rarely-accessed or read-only data:
- Move cold data to the end of the struct or behind a pointer
- Prevents cold field access from polluting cache lines holding hot data
- Prevents false sharing in concurrent access (mutable hot fields on different cache lines from read-only hot fields)

## Indices Instead of Pointers

64-bit pointers consume 8 bytes each. In pointer-rich structures (graphs, trees, linked data), pointer overhead dominates.

**Strategy**: Store objects in a contiguous array and use integer indices instead of pointers.

| Approach | Size per Reference | Notes |
|----------|-------------------|-------|
| 64-bit pointer | 8 bytes | Default on 64-bit systems |
| 32-bit index | 4 bytes | Supports up to ~4 billion elements |
| 16-bit index | 2 bytes | Supports up to 65,536 elements |
| Generational index | 4-8 bytes | Index + generation counter for safety |

Benefits beyond size reduction:
- Arrays have better cache locality than pointer-chasing
- Indices are trivially serializable
- Arrays can be relocated without updating references
- Simpler memory management (single allocation for the backing array)

**Rust note**: Generational indices (crates like `slotmap`, `thunderdome`) are idiomatic for graph-like structures, avoiding borrow checker issues with reference cycles.

**TypeScript note**: Array indices are the natural representation. Objects in arrays benefit from V8's hidden class optimization.

## Batched Storage

### Problem: Per-Element Allocation

Data structures that allocate a separate object per element (`std::map`, `std::unordered_map`, `std::list`, linked-list-based structures) incur:
- One heap allocation per element (metadata overhead + cache line alignment)
- Pointer chasing on traversal (poor cache locality)
- Allocator fragmentation over time

### Solution: Contiguous Storage

Use containers that store elements in contiguous memory:
- **Flat hash maps**: Store entries inline in a single allocation (SwissTable, hashbrown)
- **Vectors/arrays**: Contiguous element storage with index-based access
- **B-tree maps**: Store multiple elements per node, reducing allocation count and improving cache locality

## Inlined/Small-Buffer Storage

Many containers are frequently empty or hold only a few elements. Heap allocation for small counts is wasteful.

**Small-buffer optimization (SBO)**: Reserve inline space for a small number of elements. Allocate from the heap only when capacity is exceeded.

| Language | Container | Inline Capacity |
|----------|-----------|----------------|
| C++ | `absl::InlinedVector<T, N>` | N elements |
| Rust | `smallvec::SmallVec<[T; N]>` | N elements |
| Rust | `tinyvec::ArrayVec<[T; N]>` | N elements (no unsafe) |
| C++ | `std::string` (SSO) | ~22 chars (implementation-dependent) |
| Rust | `smol_str`, `compact_str` | ~22 chars |

**When to use**: When instances are frequently constructed as stack variables, when many instances exist simultaneously, or when the typical element count is small and known.

## Arena Allocation

### Concept

An arena allocates objects from a pre-allocated memory block. Deallocation frees the entire arena at once rather than individual objects.

Benefits:
- **Allocation cost**: Bump-pointer allocation is ~2 instructions vs. general-purpose allocator overhead
- **Cache packing**: Objects allocated together in time are adjacent in memory, improving spatial locality
- **Destruction cost**: Bulk deallocation avoids per-object destructor traversal

### When to Use Arenas

- Processing a request or batch of work with many temporary allocations
- Building a tree/graph structure that is discarded as a unit
- Protobuf message construction (protobuf has built-in arena support)

### Pitfalls

- **Long-lived arenas with short-lived objects**: If objects are allocated and logically freed at different rates but the arena is long-lived, memory bloats. The arena holds all memory until final deallocation.
- **Sizing**: Provide appropriate initial sizing. Too small causes multiple underlying allocations; too large wastes memory.

| Language | Arena Libraries |
|----------|----------------|
| C++ | protobuf arenas, `google::protobuf::Arena` |
| Rust | `bumpalo`, `typed-arena`, `blink-alloc` |
| TypeScript | Object pooling pattern (manual), pre-allocated `TypedArray` buffers |

## Arrays Instead of Maps

When the key domain is a small integer range or enum, replace map structures with direct-indexed arrays.

**Example**: A mapping from payload type (0-127) to clock frequency. A hash map has per-entry overhead; a 128-element array is a single cache-friendly allocation with O(1) access.

**When applicable**:
- Key domain is bounded and small (< few thousand)
- Key domain is dense (few gaps)
- Lookup frequency is high

## Bit Vectors Instead of Sets

Replace sets over small integer/enum domains with bit vectors:

- Each element occupies 1 bit instead of 8+ bytes in a hash set
- Set operations (union, intersection, difference) become single bitwise operations
- Iteration uses hardware popcount/ctz instructions

**Real-world results**:
- Spanner placement: Replacing `dense_hash_set<ZoneId>` with bit vector yielded 28-31% improvement across benchmark sizes.
- HLO reachability: Replacing `unordered_map<*, unordered_set<*>>` with a bitmap matrix dramatically improved compilation performance.

| Language | Bit Vector Libraries |
|----------|---------------------|
| C++ | `absl::InlinedBitVector`, `std::bitset` |
| Rust | `bitvec`, `fixedbitset`, `bitflags` (for enum sets) |
| TypeScript | `Uint32Array` with bitwise operations |

## Reducing Memory Indirections

### Identifying Indirections

Each pointer dereference is a potential cache miss. In structures like:

```
Object → unique_ptr<Data> → actual data
```

The CPU must load the object, follow the pointer to load the `Data` object (potentially a cache miss), then access the data. If `Data` can be inlined into the object, one cache miss is eliminated.

### Combining Lifetimes

When one object's lifetime is a superset of another, the shorter-lived object can often be stored inline (by value) rather than behind a pointer.

Good candidates for inlining:
- `unique_ptr` member initialized at construction and freed in destructor
- Small fixed-size buffers behind pointers
- Single-owner containers with known maximum size

Poor candidates:
- `shared_ptr` with indeterminate lifetime
- Large objects that would bloat the parent's cache footprint
- Optional data that is rarely present

### Memory Bandwidth Measurement

To identify memory bandwidth bottlenecks, measure cache miss rates:
- **L1 data cache misses**: High rate suggests poor spatial locality
- **LLC (Last-Level Cache) misses**: High rate means data is being fetched from DRAM
- **LLC miss percentage of total accesses**: If >10%, memory bandwidth is likely a bottleneck

Use hardware performance counters (perf stat, benchmark --benchmark_perf_counters) to gather these metrics.
