# Cross-Language Performance Equivalents

## Concept Mapping: C++ → Rust → TypeScript

This table maps performance optimization concepts across C++, Rust, and TypeScript. "N/A" indicates a concept that does not apply to that language's runtime model.

### Memory and Allocation

| Concept | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| Pre-allocate containers | `vector::reserve(n)` | `Vec::with_capacity(n)` | `new Array(n)`, pre-size TypedArrays |
| Small-buffer optimization | `absl::InlinedVector<T, N>` | `smallvec::SmallVec<[T; N]>`, `tinyvec` | N/A (GC-managed) |
| Arena allocation | `google::protobuf::Arena` | `bumpalo::Bump`, `typed_arena` | Object pooling pattern |
| View types (strings) | `std::string_view` | `&str` | Substring references (avoid `.slice()` copies in hot paths) |
| View types (arrays) | `std::Span<T>`, `absl::Span<T>` | `&[T]` | `Readonly<T[]>` (conceptual), `subarray()` for TypedArrays |
| View types (functions) | `absl::FunctionRef<R(Args...)>` | `&dyn Fn(Args) -> R` | Function references (natural) |
| Move semantics | `std::move(obj)` (explicit) | Default behavior (implicit) | Reference passing (no deep copy by default) |
| Compact enums | `enum class E : uint8_t` | `#[repr(u8)] enum E` | Union types (no memory control) |
| Bit fields | `struct { uint8_t a:3, b:5; }` | `bitflags` crate, manual bit ops | `Uint8Array` with bitwise ops |

### Data Structures

| Concept | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| Flat hash map | `absl::flat_hash_map` | `hashbrown::HashMap` (default `HashMap`) | `Map` (already good) |
| Flat hash set | `absl::flat_hash_set` | `hashbrown::HashSet` (default `HashSet`) | `Set` (already good) |
| Ordered map | `absl::btree_map` | `BTreeMap` | `Map` (insertion-ordered) |
| Bit vector | `absl::InlinedBitVector`, `std::bitset` | `bitvec`, `fixedbitset` | `Uint32Array` with bitwise operations |
| Indexed storage | `vector<T>` + `uint32_t` indices | `Vec<T>` + `u32` indices, `slotmap` | `Array<T>` + number indices (natural) |
| String interning | `absl::string_view` into pool | `string-interner` crate, `&'static str` | `Map<string, string>` dedup |
| Bump allocator | Custom arena | `bumpalo` | N/A |

### Compiler Hints and Optimization

| Concept | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| Inline hint | `inline`, `__attribute__((always_inline))` | `#[inline]`, `#[inline(always)]` | N/A (JIT decides) |
| Cold path hint | `__attribute__((noinline))`, `[[unlikely]]` | `#[cold]`, `#[inline(never)]` | N/A (JIT decides) |
| Branch prediction hint | `__builtin_expect`, `[[likely]]`/`[[unlikely]]` | `std::intrinsics::likely` (nightly) | N/A |
| Prevent dead code elimination | `benchmark::DoNotOptimize` | `std::hint::black_box` | `globalThis.sideEffect = result` |
| Const evaluation | `constexpr`, `consteval` | `const fn`, `const` generics | `as const` (type-level only) |
| SIMD | `_mm256_*` intrinsics, Highway | `std::simd` (nightly), packed_simd | N/A (WASM SIMD via wasm-bindgen) |

### Profiling and Benchmarking Tools

| Purpose | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| CPU profiling | `pprof`, `perf` | `perf`, `flamegraph`, `samply` | Chrome DevTools, `0x`, `clinic.js` |
| Memory profiling | `tcmalloc` heap profiler, `massif` | `dhat`, `heaptrack`, `bytehound` | Chrome DevTools Memory tab, `--inspect` |
| Microbenchmarking | Google Benchmark | `criterion`, `divan` | `vitest bench`, `Benchmark.js`, `mitata` |
| Hardware counters | `--benchmark_perf_counters` | `perf stat`, `iai-callgrind` | N/A |
| LLVM analysis | `llvm-mca` | `llvm-mca` (same backend) | N/A |
| Allocation tracking | `tcmalloc` sampling | `dhat`, `GlobalAlloc` wrapper | `--trace-gc`, Chrome DevTools Allocation Timeline |

### Patterns and Idioms

| Pattern | C++ | Rust | TypeScript |
|---------|-----|------|------------|
| Avoid copies in sort | Sort `vector<size_t>` of indices | Sort `Vec<usize>` of indices | Sort array of indices |
| Reuse temporary buffers | Declare outside loop, `.clear()` | Declare outside loop, `.clear()` | Declare outside loop, reset |
| Cache-friendly iteration | `vector<T>` sequential access | `Vec<T>` sequential access | `TypedArray` sequential access |
| Bulk API | `LookupMany(span<Key>)` | `lookup_many(&[Key])` | `lookupMany(keys: readonly Key[])` |
| Object pooling | Custom allocator, arena | `bumpalo`, `typed-arena` | Pool class with acquire/release |
| Lazy initialization | `static` local, `absl::call_once` | `once_cell::OnceCell`, `LazyLock` | Lazy getter pattern, `??=` |

## Applicability Matrix

Not all optimization techniques apply equally to all languages:

| Technique Category | C++ | Rust | TypeScript |
|-------------------|-----|------|------------|
| Algorithmic improvements | Full | Full | Full |
| Data structure selection | Full | Full | Full |
| Bulk API design | Full | Full | Full |
| Estimation and measurement | Full | Full | Full |
| Process/methodology | Full | Full | Full |
| Reduce allocations | Full | Full | Partial (GC handles small allocs well) |
| Memory layout / compaction | Full | Full | Limited (no layout control) |
| Cache line optimization | Full | Full | N/A (no memory layout control) |
| SIMD / vectorization | Full | Full (nightly/crates) | N/A (except WASM) |
| Compiler hints | Full | Full | N/A (JIT-managed) |
| Hardware counters | Full | Full (same tools) | N/A |
| LLVM analysis | Full | Full (shared backend) | N/A |

## TypeScript-Specific Concerns

While many C++/Rust techniques do not directly apply to TypeScript, equivalent concerns exist:

| C++/Rust Concern | TypeScript Equivalent |
|-----------------|----------------------|
| Cache line efficiency | V8 hidden class stability (monomorphic access) |
| Memory layout | Avoid megamorphic property access patterns |
| Code size → icache | Bundle size → parse/compile time |
| LLVM optimization | V8 TurboFan optimization (deoptimization bailouts) |
| Stack vs. heap | Smi (small integer) optimization, avoid boxing |
| Manual memory management | GC pressure management, WeakRef for caches |

### TypeScript Performance Priorities

1. **Algorithmic complexity** - same as any language
2. **Avoid megamorphic call sites** - polymorphic function calls prevent V8 optimization
3. **Minimize GC pressure** - reduce allocation rate in hot loops
4. **Keep objects monomorphic** - consistent property shapes enable V8 hidden class optimization
5. **Use TypedArrays for numeric work** - avoid boxing overhead of regular arrays for number-heavy computation
6. **Avoid `.slice()` copies in hot paths** - use index ranges instead
7. **Bundle size awareness** - smaller bundles parse and compile faster
