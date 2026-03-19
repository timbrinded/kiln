# Gotchas — When NOT to Flag

Before finalizing any finding, check it against this list. False positives erode trust faster than missed issues improve code. When in doubt, don't flag.

## Framework Conventions That Look Like Violations

### React / Next.js

- **`useEffect` with cleanup** — The cleanup function pattern (`return () => { ... }`) is not over-engineering. It's the prescribed way to handle subscriptions, timers, and event listeners. Don't flag it under Directive #10 (over-split).
- **`useCallback` / `useMemo` wrappers** — These look like unnecessary indirection but prevent re-renders in specific contexts. Only flag if the wrapped function is never passed as a prop or dependency.
- **Error boundaries as separate components** — React requires class components for error boundaries. The extra file/class is not over-split.
- **`'use client'` / `'use server'` directives** — These are framework requirements, not unnecessary code.
- **Server Actions as separate functions** — Next.js requires these to be defined in specific ways. Don't flag the indirection.
- **Loading/error/layout files in Next.js** — File-based conventions. The existence of `loading.tsx` next to `page.tsx` is not over-split.

### Express / Fastify / Hono

- **Middleware chains** — Multiple small middleware functions composed together is the intended pattern. Don't flag under Directive #10.
- **Error-handling middleware** — The `(err, req, res, next)` signature with 4 parameters is a framework requirement. Don't flag under Directive #13.

### Testing Frameworks

- **`describe` / `it` nesting** — Test structure conventions. Deep nesting is sometimes necessary for clarity.
- **`beforeEach` / `afterEach` setup** — Test lifecycle hooks. The indirection is by design.
- **Mock factories** — Functions that create mock objects often look over-engineered but serve test isolation.
- **Verbose assertions** — `expect(result).toEqual(expected)` with detailed objects is preferred over terse checks in tests.

### Vue / Svelte

- **Computed properties wrapping simple expressions** — These enable reactivity tracking. Not unnecessary abstraction.
- **`$:` reactive blocks in Svelte** — Compiler directive, not verbose code.

## Language Idioms That Are NOT Slop

### TypeScript

- **Type guards** (`function isFoo(x: unknown): x is Foo`) — These narrow types at runtime. The function exists for type safety, not abstraction. Don't flag under Directive #10 unless the guard is used exactly once AND could be an inline check.
- **Branded types** (`type UserId = string & { __brand: 'UserId' }`) — Deliberate type narrowing. Not unnecessary complexity.
- **`satisfies` operator** — Type-checking without widening. Not defensive coding.
- **Overload signatures** — Multiple function signatures before the implementation. Required by the type system.
- **Index signatures with explicit undefined** (`[key: string]: T | undefined`) — Correct typing for dictionaries. Not defensive.

### Rust

- **`match` with explicit arms** — Exhaustive matching is Rust's strength. Don't flag comprehensive match blocks under Directive #8.
- **`.unwrap_or_else(|| ...)` chains** — Idiomatic error handling. Not defensive coding.
- **`impl From<X> for Y`** — Trait implementations for conversions. Required by the ecosystem.
- **Lifetime annotations** — Required by the borrow checker. Never flag.
- **Builder pattern** — Common Rust pattern for constructing complex objects. Only flag if the built object has 2-3 fields.

### Python

- **`__init__` / `__repr__` / `__eq__` boilerplate** — Required by the data model. Use `@dataclass` suggestion instead of flagging.
- **Context managers** (`with` statements) — Resource management pattern. Not over-engineering.
- **Type hints on simple functions** — Part of the project's type-checking strategy. Don't flag.
- **`if __name__ == "__main__":` guard** — Standard Python convention. Not unnecessary code.

### Go

- **`if err != nil { return err }`** — THE Go error handling pattern. Never flag this. Ever.
- **Interface definitions with single method** — Go interfaces are typically small. Don't flag under Directive #10.
- **Separate `_test.go` files** — Language convention for test organization.
- **`ctx context.Context` as first parameter** — Go convention. Don't flag under Directive #13.

## Generated / Vendored Code — Skip Entirely

Do not review code in these locations:

- `node_modules/`, `vendor/`, `third_party/`
- `*.generated.*`, `*.gen.*`, `*_generated.*`
- `*.pb.go`, `*.pb.ts` (protobuf generated)
- `*.graphql.ts`, `*.graphql.d.ts` (codegen)
- `migrations/` (database migrations — typically generated)
- `*.min.js`, `*.min.css` (minified)
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`
- `*.snap` (test snapshots)
- Files with `// Code generated` or `# This file is auto-generated` headers

## Test Code Exceptions

Tests have different quality criteria than production code:

- **Verbose setup is acceptable** — Test readability benefits from explicit setup over abstractions
- **Duplication is often better than DRY** — Each test should be independently readable
- **Helper functions in test files are fine** — Test utilities called from multiple tests within the same file
- **Don't flag long test functions** — A test that reads top-to-bottom without helpers is often clearer than one with abstractions
- **Magic numbers in assertions are fine** — `expect(result.length).toBe(3)` doesn't need a named constant
- **Hardcoded test data is fine** — String literals, fixture objects, inline expected values

Only flag test code when:
- A helper function is defined but never called
- The same assertion is copy-pasted 10+ times and would genuinely benefit from a loop
- Test setup creates objects with 15+ fields when only 2 are relevant to the test

## When Complexity IS Warranted

### State Machines

Code that explicitly models states and transitions should be verbose. A 50-line switch statement handling 8 states is better than a "simplified" version that hides the state transitions. Don't flag under Directive #8 or #9.

### Error Handling at System Boundaries

Code that interfaces with external systems (HTTP clients, database drivers, file systems, user input) legitimately needs:
- Try/catch blocks (Directive #12 exception)
- Null checks on responses (Directive #5 exception)
- Default values for missing fields (Directive #6 exception)
- Multiple error code branches (Directive #8 exception)

The key distinction: defensive coding at the **boundary** is correct. Defensive coding **inside** the system where types are known is slop.

### Serialization / Deserialization

Code that parses external data (API responses, config files, user input) should validate aggressively. This is the one place where `typeof` checks, null guards, and fallback values are all appropriate.

### Infrastructure / Platform Code

Low-level code that other code builds on (HTTP frameworks, ORM layers, CLI parsers) often needs:
- Many parameters (it's a configuration surface, Directive #13 exception)
- Optional arguments (it serves many callers with different needs, Directive #14 exception)
- Multiple small functions (composability is the design goal, Directive #10 exception)

### Accessibility Code

Extra attributes, ARIA labels, focus management, and screen reader support are not bloat. Never flag accessibility-related code.

## The Decision Rule

When you're unsure whether something is slop or legitimate complexity, ask:

1. **Is this code at a system boundary?** (external data, user input, network) → Probably legitimate
2. **Is this a framework requirement?** (lifecycle methods, conventions, signatures) → Definitely legitimate
3. **Is this inside the system with known types?** → Probably slop
4. **Would removing this change behavior in any reachable code path?** → If yes, legitimate. If no, slop.

**Default to NOT flagging.** A finding you're unsure about is worse than a finding you missed.
