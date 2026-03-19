# Code Quality Directives — Detailed Reference

14 directives for detecting and removing AI-generated verbosity. Each directive includes the principle, reasoning, red flags, and before/after examples.

---

## Directive #1: Write Skimmable Code

**Principle:** Code should communicate its intent at a glance. A reader should understand what a function does by reading the first and last few lines, not by tracing through every branch.

**Why:** AI-generated code often produces correct but dense blocks where the logic is spread evenly across 40 lines with no visual hierarchy. A human writing the same code would cluster the important logic together and make the structure obvious. Skimmability isn't about comments — it's about structure.

**Red Flags:**
- Functions over 30 lines with no visual grouping (blank lines separating logical phases)
- Multiple responsibilities mixed within a single function body
- Important business logic buried in the middle of boilerplate
- Conditional chains where each branch does significantly different things but looks structurally identical
- Return values computed through a long chain with no intermediate variable names that explain the phases

**Before:**
```typescript
function processOrder(order: Order, user: User, inventory: Inventory) {
  const items = order.items.filter(item => {
    const stock = inventory.getStock(item.productId);
    if (stock === null) {
      return false;
    }
    if (stock.quantity < item.quantity) {
      return false;
    }
    if (stock.reserved) {
      const available = stock.quantity - stock.reservedCount;
      if (available < item.quantity) {
        return false;
      }
    }
    return true;
  });
  const total = items.reduce((sum, item) => {
    const price = item.unitPrice * item.quantity;
    const discount = user.membership === 'premium' ? price * 0.1 : 0;
    return sum + price - discount;
  }, 0);
  const tax = total * 0.08;
  const finalTotal = total + tax;
  return { items, total: finalTotal, tax };
}
```

**After:**
```typescript
function processOrder(order: Order, user: User, inventory: Inventory) {
  const availableItems = order.items.filter(item => hasStock(inventory, item));

  const subtotal = calculateSubtotal(availableItems, user);
  const tax = subtotal * 0.08;

  return { items: availableItems, total: subtotal + tax, tax };
}

function hasStock(inventory: Inventory, item: OrderItem): boolean {
  const stock = inventory.getStock(item.productId);
  if (!stock || stock.quantity < item.quantity) return false;
  if (stock.reserved) return stock.quantity - stock.reservedCount >= item.quantity;
  return true;
}

function calculateSubtotal(items: OrderItem[], user: User): number {
  const discount = user.membership === 'premium' ? 0.1 : 0;
  return items.reduce((sum, item) => sum + item.unitPrice * item.quantity * (1 - discount), 0);
}
```

> **Note:** This directive can conflict with Directive #10 (don't over-split). The distinction: extract when it makes the parent function *skimmable*, not when the extracted function is trivially small. `hasStock` earns its existence because `processOrder` now reads as three clear phases.

---

## Directive #2: Minimize Possible States

**Principle:** Every argument, variable, and type widens the state space. Fewer possible states means fewer bugs and less code to handle those states.

**Why:** AI models add arguments "just in case" — optional config objects, feature flags, format parameters. Each optional argument doubles the state space. If a function takes 3 optional booleans, it has 8 possible configurations, and the AI will write handling for all 8 even if only 1 is ever used.

**Red Flags:**
- Functions accepting config objects where only 1-2 fields are ever set
- Boolean parameters that are always `true` or always `false` at every call site
- Union types wider than any caller produces (e.g., `string | number` but only strings are passed)
- Variables that are assigned once and never reassigned but declared with `let`
- State variables that could be derived from other state

**Before:**
```typescript
function formatDate(
  date: Date,
  format: 'short' | 'long' | 'iso' | 'relative' = 'short',
  locale: string = 'en-US',
  includeTime: boolean = false,
  timezone?: string
): string {
  // 40 lines handling every combination
}

// Every call site:
formatDate(order.createdAt)
formatDate(user.joinedAt)
```

**After:**
```typescript
function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', { dateStyle: 'short' });
}
```

> **Cross-language note:** In Go, this manifests as option structs with 10 fields. In Rust, as builder patterns with unused methods. The principle is the same: if no caller uses the flexibility, remove it.

---

## Directive #3: Use Discriminated Unions to Reduce State Space

**Principle:** When an object can be in one of N states, represent it as a discriminated union where each variant carries only the fields valid for that state. This makes illegal states unrepresentable.

**Why:** AI-generated code often uses a single flat type with optional fields, then scatters `if (obj.type === 'X')` checks throughout the code. A discriminated union moves that check to the type system, eliminating entire categories of bugs and the defensive code that protects against them.

**Red Flags:**
- Objects with multiple optional fields where certain combinations are invalid
- Repeated `if (x.status === 'loaded')` checks before accessing `x.data`
- `type` or `kind` fields checked manually instead of being the discriminant
- Error handling that checks `if (result.error)` and `if (result.data)` separately

**Before:**
```typescript
type ApiResult = {
  status: 'loading' | 'success' | 'error';
  data?: ResponseData;
  error?: Error;
  retryCount?: number;
};

function renderResult(result: ApiResult) {
  if (result.status === 'loading') {
    return <Spinner />;
  }
  if (result.status === 'error') {
    if (result.error) {  // defensive — error must exist if status is 'error'
      return <ErrorDisplay error={result.error} retries={result.retryCount ?? 0} />;
    }
    return <ErrorDisplay error={new Error('Unknown')} retries={0} />;
  }
  if (result.status === 'success') {
    if (result.data) {  // defensive — data must exist if status is 'success'
      return <DataView data={result.data} />;
    }
    return null;
  }
  return null;
}
```

**After:**
```typescript
type ApiResult =
  | { status: 'loading' }
  | { status: 'success'; data: ResponseData }
  | { status: 'error'; error: Error; retryCount: number };

function renderResult(result: ApiResult) {
  switch (result.status) {
    case 'loading': return <Spinner />;
    case 'success': return <DataView data={result.data} />;
    case 'error': return <ErrorDisplay error={result.error} retries={result.retryCount} />;
  }
}
```

> **Rust note:** Rust enums are discriminated unions natively. If you see Rust code using a struct with `Option<T>` fields to represent states, suggest an enum instead.

---

## Directive #4: Exhaustively Handle Multi-Type Objects, Fail on Unknown

**Principle:** When switching on a discriminated union or enum, handle every case explicitly and fail at compile time (or loudly at runtime) on unknown values.

**Why:** AI-generated code tends to use `if/else` chains with a permissive `else` clause that silently swallows unknown cases. When a new variant is added, the code silently does the wrong thing instead of failing loudly.

**Red Flags:**
- `else` clause that returns a default value for a discriminated union
- `switch` without `default: assertNever(x)` (TypeScript)
- `match` without exhaustiveness (though Rust enforces this)
- `if/else if/else` chain on a type field where the `else` isn't specific

**Before:**
```typescript
function getIcon(status: Status) {
  if (status === 'active') return <ActiveIcon />;
  if (status === 'paused') return <PausedIcon />;
  return <DefaultIcon />;  // what status produces this? unknown silently swallowed
}
```

**After:**
```typescript
function getIcon(status: Status) {
  switch (status) {
    case 'active': return <ActiveIcon />;
    case 'paused': return <PausedIcon />;
    case 'archived': return <ArchivedIcon />;
    default: assertNever(status);
  }
}
```

**Helper:**
```typescript
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}
```

---

## Directive #5: Trust the Types — No Defensive Null Checks on Non-Nullable Types

**Principle:** If the type system says a value is non-nullable, don't check for null. The type system is the source of truth.

**Why:** AI models add null checks compulsively because they've been trained on code from loosely-typed codebases. In a TypeScript project with strict null checks, checking `if (user != null)` when `user: User` (not `User | null`) is pure noise. Worse, it signals to readers that null is a possible state, creating confusion.

**Red Flags:**
- `if (x != null)` where `x` is typed as non-nullable
- `x?.property` on a non-optional type
- `x ?? defaultValue` where `x` cannot be null/undefined
- `typeof x === 'string'` where `x` is already typed as `string`
- `Array.isArray(x)` where `x` is already typed as an array

**Before:**
```typescript
function greetUser(user: User): string {
  if (user == null) {
    return 'Hello, guest';
  }
  const name = user.name ?? 'Unknown';
  if (typeof name === 'string') {
    return `Hello, ${name}`;
  }
  return 'Hello';
}
```

**After:**
```typescript
function greetUser(user: User): string {
  return `Hello, ${user.name}`;
}
```

> **Boundary exception:** At system boundaries (API responses, JSON parsing, database queries), values ARE potentially null regardless of types. See `references/gotchas.md`. This directive applies only inside the system where types are trustworthy.

> **Python note:** If the project uses a type checker (mypy, pyrefly, pyright) with strict mode, the same principle applies. Don't add `if x is not None` when the type annotation says `x: str`.

---

## Directive #6: Assert on Load, Be Opinionated About Parameters

**Principle:** Validate inputs early and fail loudly rather than propagating bad state with fallback defaults. If a value is required, assert its presence at the boundary.

**Why:** AI-generated code loves `?? fallback` patterns — providing defaults for values that should never be missing. This hides configuration errors and makes debugging harder. If `API_URL` is required, crashing at startup with "API_URL is not set" is better than silently using `http://localhost:3000` and failing mysteriously later.

**Red Flags:**
- `process.env.API_URL ?? 'http://localhost:3000'` for a required config value
- Functions that accept `undefined` and silently substitute defaults for required data
- Config objects that merge with defaults instead of validating required fields
- `|| 'default'` on values that must come from the caller

**Before:**
```typescript
function createClient(config?: Partial<ClientConfig>) {
  const baseUrl = config?.baseUrl ?? 'http://localhost:3000';
  const timeout = config?.timeout ?? 5000;
  const retries = config?.retries ?? 3;
  const apiKey = config?.apiKey ?? process.env.API_KEY ?? '';
  // now uses empty string as API key, fails silently later
  return new Client({ baseUrl, timeout, retries, apiKey });
}
```

**After:**
```typescript
function createClient(config: ClientConfig) {
  assert(config.apiKey, 'API key is required');
  assert(config.baseUrl, 'Base URL is required');
  return new Client(config);
}
```

> **Distinction from Directive #5:** Directive #5 says don't check what the type system already guarantees. Directive #6 says DO check at the system boundary where external input enters. These complement each other — trust types internally, validate externally.

---

## Directive #7: Remove Changes Not Strictly Required

**Principle:** A diff should contain only the changes required to accomplish the task. Reformatting, renaming, reordering, or "improving" adjacent code in the same diff creates noise.

**Why:** AI models routinely "improve" code adjacent to their actual changes — renaming variables, reordering imports, reformatting expressions, adding type annotations to functions they didn't change. This makes diffs harder to review, increases merge conflict risk, and obscures the actual change.

**Red Flags:**
- Import reordering in files where only one function changed
- Variable renames in unchanged code
- Type annotation additions to unchanged functions
- Reformatting (whitespace, line breaks) in unchanged blocks
- Comments added to unchanged code
- `console.log` or debugging artifacts left in

**Guidance:** This directive is unusual — it's about the diff, not the code. When reviewing, compare the diff to the stated task. Any change that doesn't directly serve the task should be flagged for removal.

> **Note:** This directive is harder to enforce in automated review because it requires understanding the intent. If the user says "add a login button" and the diff includes reformatting 200 lines, flag it. If the user says "refactor the auth module", broader changes are expected.

---

## Directive #8: Bias for Fewer Lines of Code

**Principle:** When two approaches are equally readable and correct, prefer the one with fewer lines. Less code means less to read, less to maintain, and fewer places for bugs to hide.

**Why:** AI-generated code consistently chooses verbose forms over concise ones. Explicit variable assignments instead of inline expressions, multi-line conditionals instead of ternaries (for simple cases), named intermediate values for trivially understood expressions.

**Red Flags:**
- Intermediate variables used exactly once and whose name just restates the expression
- Multi-line `if/else` returning two values when a ternary is perfectly readable
- Explicit type annotations where inference is unambiguous
- Object destructuring spread across 5 lines for a 2-field object
- `Array.from(x).map(...)` when `x.map(...)` works

**Before:**
```typescript
function getDisplayName(user: User): string {
  const firstName: string = user.firstName;
  const lastName: string = user.lastName;
  const hasLastName: boolean = lastName.length > 0;
  let displayName: string;
  if (hasLastName) {
    displayName = `${firstName} ${lastName}`;
  } else {
    displayName = firstName;
  }
  return displayName;
}
```

**After:**
```typescript
function getDisplayName(user: User): string {
  return user.lastName
    ? `${user.firstName} ${user.lastName}`
    : user.firstName;
}
```

> **Balance with Directive #9:** A ternary is more concise than `if/else` but a *nested* ternary is complex/clever code. The line is: if a single ternary reads clearly, use it. If you need to nest or chain them, use `if/else`.

---

## Directive #9: No Complex or Clever Code

**Principle:** Code should be obvious on first read. If a reader needs to pause and trace through the logic to understand what happens, it's too clever.

**Why:** AI models produce patterns they've seen in training data, including clever one-liners, complex reduce chains, and abstract utility patterns. These work but require significant cognitive load to verify.

**Red Flags:**
- Nested ternary expressions
- `.reduce()` used to build objects or perform multi-step transformations (use a `for` loop)
- Generic utility functions used once (e.g., `pipe()`, `compose()`, `curry()` for a single call chain)
- Recursive solutions for naturally iterative problems
- Bitwise operations for non-performance-critical logic
- Template literal types for runtime string manipulation

**Before:**
```typescript
const grouped = items.reduce((acc, item) => ({
  ...acc,
  [item.category]: [...(acc[item.category] || []), item]
}), {} as Record<string, Item[]>);
```

**After:**
```typescript
const grouped: Record<string, Item[]> = {};
for (const item of items) {
  (grouped[item.category] ??= []).push(item);
}
```

> **Rust note:** In Rust, iterator chains (`.filter().map().collect()`) are idiomatic and preferred over manual loops. Only flag chains that are genuinely hard to follow — e.g., nested `flat_map` with closures over closures.

---

## Directive #10: Don't Over-Split Into Too Many Functions

**Principle:** A function should earn its existence. If a helper is called once, is less than 5 lines, and doesn't improve readability of the caller, inline it.

**Why:** AI models extract functions aggressively — every 3-4 lines become a named helper. This fragments the logic across the file, forcing readers to jump between definitions to understand a linear flow. The cure (indirection) becomes worse than the disease (a slightly long function).

**Red Flags:**
- Functions called exactly once from a single location
- Functions whose name is just a restatement of the single expression they contain
- Wrapper functions that add no logic (`function getData() { return fetchData(); }`)
- "Utility" functions with 1-2 lines that could be inline
- Files with more function definitions than the problem warrants

**Before:**
```typescript
function processUser(user: User) {
  const validated = validateUserName(user);
  const normalized = normalizeUserEmail(validated);
  const enriched = addDefaultRole(normalized);
  return enriched;
}

function validateUserName(user: User): User {
  assert(user.name.length > 0, 'Name required');
  return user;
}

function normalizeUserEmail(user: User): User {
  return { ...user, email: user.email.toLowerCase() };
}

function addDefaultRole(user: User): User {
  return { ...user, role: user.role ?? 'viewer' };
}
```

**After:**
```typescript
function processUser(user: User): User {
  assert(user.name.length > 0, 'Name required');
  return {
    ...user,
    email: user.email.toLowerCase(),
    role: user.role ?? 'viewer',
  };
}
```

> **Balance with Directive #1:** Extract when it makes the parent *skimmable* (Directive #1). Don't extract when the parent is already simple enough to read linearly. The test: does the reader need to jump to the helper to understand the parent? If yes, inline. If the helper abstracts a genuinely separate concern, keep it.

---

## Directive #11: Early Returns Over Nested Conditionals

**Principle:** Handle edge cases and error conditions at the top of a function with early returns. The main logic should live at the top indentation level, not nested inside conditions.

**Why:** AI-generated code wraps the happy path in conditionals: `if (isValid) { if (hasPermission) { if (dataExists) { ...actual logic... } } }`. Each nesting level adds cognitive load. Early returns eliminate the nesting entirely.

**Red Flags:**
- Functions with 3+ levels of nesting from conditionals
- `if (condition) { ...30 lines... } else { return error }` — the `else` should be the early return
- Boolean variables assigned in an `if/else` then used once
- Guard clauses placed after the code they guard

**Before:**
```typescript
function updateProfile(userId: string, data: ProfileData) {
  const user = await getUser(userId);
  if (user) {
    if (user.isActive) {
      if (data.email !== user.email) {
        const emailTaken = await checkEmail(data.email);
        if (!emailTaken) {
          await saveProfile(userId, data);
          return { success: true };
        } else {
          return { success: false, error: 'Email taken' };
        }
      } else {
        await saveProfile(userId, data);
        return { success: true };
      }
    } else {
      return { success: false, error: 'User inactive' };
    }
  } else {
    return { success: false, error: 'User not found' };
  }
}
```

**After:**
```typescript
function updateProfile(userId: string, data: ProfileData) {
  const user = await getUser(userId);
  if (!user) return { success: false, error: 'User not found' };
  if (!user.isActive) return { success: false, error: 'User inactive' };

  if (data.email !== user.email) {
    const emailTaken = await checkEmail(data.email);
    if (emailTaken) return { success: false, error: 'Email taken' };
  }

  await saveProfile(userId, data);
  return { success: true };
}
```

---

## Directive #12: Assert Instead of Try/Catch or Default Values

**Principle:** When a condition should always be true at a given point in the code, assert it. Don't wrap it in try/catch and provide a default, because that silently hides bugs.

**Why:** AI models love `try { ... } catch { return defaultValue }` — it makes the code "safer" by never throwing. But inside the application (not at boundaries), an unexpected error means a bug. Catching and returning a default hides the bug. Asserting surfaces it immediately.

**Red Flags:**
- `try { JSON.parse(x) } catch { return {} }` for data that should always be valid JSON
- `catch (e) { console.log(e); return null }` — logging and swallowing
- `catch (e) { return defaultValue }` for operations that shouldn't fail
- `try` blocks wrapping 30+ lines of code (catch is too broad — which line failed?)
- Catches that don't discriminate between error types

**Before:**
```typescript
function getConfig(): Config {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, 'utf-8');
    const parsed = JSON.parse(raw);
    return {
      port: parsed.port ?? 3000,
      host: parsed.host ?? 'localhost',
      debug: parsed.debug ?? false,
    };
  } catch {
    return { port: 3000, host: 'localhost', debug: false };
  }
}
```

**After:**
```typescript
function getConfig(): Config {
  const raw = fs.readFileSync(CONFIG_PATH, 'utf-8');
  const parsed = JSON.parse(raw);
  assert(typeof parsed.port === 'number', `Invalid port in ${CONFIG_PATH}`);
  assert(typeof parsed.host === 'string', `Invalid host in ${CONFIG_PATH}`);
  return { port: parsed.port, host: parsed.host, debug: parsed.debug ?? false };
}
```

> **Boundary exception:** At HTTP handlers, CLI entry points, and message consumers, catching errors and returning appropriate responses IS correct. This directive targets internal code that should fail fast. See `references/gotchas.md`.

---

## Directive #13: Keep Argument Count Low, Never Pass Unnecessary Overrides

**Principle:** Functions should take as few arguments as possible. If a function takes more than 3 arguments, it's likely doing too much or accepting data it doesn't need.

**Why:** AI models create functions with parameter lists that mirror the *data available at the call site* rather than the *data needed by the function*. The result: functions that take 6 parameters but use 3, or functions where the caller always passes the same value for 2 of the parameters.

**Red Flags:**
- Functions with 4+ parameters
- Parameters that are always passed the same value at every call site
- Parameters passed through a function to an inner function without being used
- Config/options objects with fields the function never reads
- Deconstructed arguments that pull 6+ fields from an object

**Before:**
```typescript
function sendNotification(
  userId: string,
  message: string,
  channel: 'email' | 'sms' | 'push',
  priority: 'low' | 'normal' | 'high',
  retry: boolean,
  maxRetries: number,
  template: string
) {
  // channel is always 'email', priority always 'normal', retry always true
}

// Every call site:
sendNotification(id, msg, 'email', 'normal', true, 3, 'default');
```

**After:**
```typescript
function sendEmailNotification(userId: string, message: string) {
  // channel, priority, retry behavior baked in — they were never varied
}
```

> **Go note:** Go encourages option structs for functions with many parameters. If the struct exists and callers set different fields, that's fine. If every caller sets the same 2 fields, collapse.

---

## Directive #14: Don't Make Arguments Optional if Actually Required

**Principle:** If every caller of a function passes an argument, that argument is required, not optional. The type signature should reflect reality.

**Why:** AI models default to making parameters optional (`arg?: Type`) as a "safe" choice. This widens the type inside the function (now `Type | undefined`), forcing either a null check or a `!` assertion — both are noise created by the wrong type signature.

**Red Flags:**
- `arg?: Type` where every caller passes the argument
- `arg: Type | undefined` where no caller passes `undefined`
- `arg: Type = defaultValue` where no caller relies on the default
- Non-null assertions (`arg!`) inside a function that receives `arg?`
- `if (arg === undefined) throw` — if it throws, it was required

**Before:**
```typescript
function createUser(name: string, email?: string, role?: string) {
  if (!email) throw new Error('Email is required');
  if (!role) throw new Error('Role is required');
  return { name, email, role };
}

// Every call site:
createUser('Alice', 'alice@example.com', 'admin');
createUser('Bob', 'bob@example.com', 'viewer');
```

**After:**
```typescript
function createUser(name: string, email: string, role: string) {
  return { name, email, role };
}
```

> **Library/API exception:** Public APIs and library functions legitimately use optional parameters for backward compatibility and flexibility. This directive targets application code where you control all callers. See `references/gotchas.md` for the boundary between library and application code.

---

## Cross-Directive Interactions

Some directives pull in opposite directions. Use this priority:

| Tension | Resolution |
|---------|-----------|
| #1 (skimmable) vs. #10 (don't over-split) | Extract only when the parent becomes skimmable. Don't extract trivial 2-line helpers. |
| #8 (fewer lines) vs. #9 (no clever code) | Concise is good. Clever is bad. A simple ternary is concise. A nested ternary is clever. |
| #5 (trust types) vs. #6 (assert at boundary) | Trust types inside the system. Assert at the boundary where external data enters. |
| #12 (assert, not catch) vs. boundary code | Assert inside. Catch at boundaries. The boundary is where external data enters your system. |
| #13 (few arguments) vs. #14 (don't make optional) | Both reduce noise. If you have 6 required args, the function is likely doing too much (#13 first). |

When two directives conflict on a specific piece of code, prefer the one that produces fewer lines of code while remaining readable. The goal is always simplicity.
