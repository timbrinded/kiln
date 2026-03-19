---
name: unslop
description: >-
  This skill should be used when the user asks to "clean up", "remove slop",
  "simplify", "unslop", "review for quality", "reduce complexity", "tighten up",
  "cleanup before PR", "pre-PR review", "too verbose", "over-engineered",
  "remove unnecessary code", "AI generated mess", "simplify this",
  "reduce abstractions", or mentions "slop", "bloated code", "defensive coding",
  "unnecessary complexity", "too many functions", "over-abstracted".
  Also applicable when reviewing code after an AI generation session,
  preparing a branch for PR, or when code smells like it was written by
  a model that optimizes for looking thorough rather than being correct.
---

# Unslop — Post-Generation Code Quality Cleanup

Reviews git diffs against 14 simplicity directives and proposes concrete fixes. Targets the specific failure mode of AI-generated code: correct but bloated.

## Core Philosophy

AI code generators produce code that is usually correct but systematically verbose. The model optimizes for *appearing thorough* — adding defensive checks, optional parameters, helper abstractions, and error handling for conditions that cannot occur. This isn't a bug; it's an alignment artifact. The model would rather include unnecessary code than risk missing something.

The result: code that works but is harder to read, has more state to track, and is more complex than necessary. This skill identifies and removes that accidental complexity.

**The test is simple: does removing this code change behavior?** If not, remove it.

## How to Detect Changed Code

Use git to find what changed. Try these in order:

1. **Branch diff** (most common): `git diff main...HEAD --name-only` — all changes on this branch
2. **Staged changes**: `git diff --staged --name-only` — about to be committed
3. **Unstaged changes**: `git diff --name-only` — modified but not staged
4. **Explicit files**: User passes `--files path1 path2` — skip detection

Filter out non-code files: lockfiles, `*.generated.*`, `vendor/`, `node_modules/`, images, fonts, `.min.*` files.

For the actual diff content per file: `git diff main...HEAD -- path/to/file.ts`

## The 14 Directives — Summary

| # | Directive | Red Flag |
|---|-----------|----------|
| 1 | Write skimmable code | Long functions requiring full read to understand, poor visual structure |
| 2 | Minimize possible states | Extra arguments, wider types than needed, boolean flags |
| 3 | Use discriminated unions | `type` field + separate checks vs. a single discriminated union |
| 4 | Exhaustively handle multi-type objects | `if/else` chains missing cases, no `default: assertNever()` |
| 5 | Trust the types | Null checks on non-nullable types, redundant `typeof` guards |
| 6 | Assert on load, be opinionated | Permissive defaults, late validation, `?? fallback` for required values |
| 7 | Remove changes not strictly required | Diff includes reformatting, renames, or moves unrelated to the task |
| 8 | Bias for fewer lines | Verbose constructs when concise alternatives exist |
| 9 | No complex or clever code | Nested ternaries, chained reduces, generic abstractions for single use |
| 10 | Don't over-split functions | Helpers called once, 3-line functions wrapping trivial logic |
| 11 | Early returns over nesting | `if/else` chains where early return would flatten the logic |
| 12 | Assert instead of try/catch or defaults | `try { } catch { return default }` hiding real errors |
| 13 | Keep argument count low | Functions taking 4+ parameters, passing unchanged values through |
| 14 | Don't make arguments optional if required | `arg?: Type` where every caller passes the argument |

For detailed guidance, examples, and before/after code for each directive, load **`references/code-quality-directives.md`**.

## Decision Tree — Which Reference to Load

**"I need detailed guidance on a specific directive"**
→ **`references/code-quality-directives.md`** — Full principle, reasoning, red flags, and before/after examples for all 14 directives.

**"I'm not sure if this is a real issue or a false positive"**
→ **`references/gotchas.md`** — Framework conventions, language idioms, test code exceptions, and cases where complexity is genuinely warranted.

**"I need both"**
→ Load both. The directives file is the primary reference; gotchas is the safety net.

## Output Format

Every review produces findings in this structure:

```
## Unslop Review

### Summary
- Files reviewed: N
- Findings: N (breakdown by directive)
- Estimated lines removable: N

### File: path/to/file.ts

1. **Directive #N: [Name]** — Lines L1-L2
   - What: [One sentence describing the issue]
   - Why: [The principle violated and the concrete cost]
   - Fix:
   ```ts
   [replacement code]
   ```

### Recommendations
- [Top 3 highest-impact simplifications across all files]
```

**Rules for findings:**
- Only flag code in the diff — unchanged code is out of scope
- Every finding needs a concrete fix — "consider simplifying" is not acceptable
- Check gotchas before finalizing — false positives destroy trust
- Group related findings that share a root cause
- Estimate lines removable per finding

## Workflow

### Small diffs (≤10 files)

1. Detect changed files via git
2. For each file: read contents, get diff, evaluate against directives
3. Load `references/code-quality-directives.md` for detailed guidance on flagged directives
4. Check `references/gotchas.md` before finalizing
5. Present report
6. Apply fixes → typecheck → lint → report (skip if `--check`)

### Large diffs (>10 files)

1. Detect changed files via git
2. Spawn `unslop-reviewer` subagent per file or batch of related files
3. Collect reports from subagents
4. Deduplicate and merge findings
5. Present consolidated report
6. Apply fixes sequentially → typecheck → lint → report (skip if `--check`)

## What This Skill Does NOT Do

- **Correctness** — Not checking if the code works. That's what tests are for.
- **Formatting** — Not checking style, indentation, or semicolons. That's the formatter's job.
- **Naming** — Not judging variable or function names. Too subjective, low ROI.
- **Performance** — Not profiling or benchmarking. See the `performance-optimization` skill.
- **Security** — Not scanning for vulnerabilities. Separate concern entirely.
- **Architecture** — Not redesigning the module structure. Just cleaning up within it.

This skill has one job: reduce accidental complexity in recently changed code.

## All Reference Files

| File | Content | Lines |
|------|---------|-------|
| **`references/code-quality-directives.md`** | Detailed per-directive guidance with before/after examples | ~900 |
| **`references/gotchas.md`** | False positive prevention, framework exceptions, language idioms | ~250 |
