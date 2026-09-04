---
name: codesaver
description: >-
  This skill should be used when the user asks for "Codesavers", "use
  Codesavers", "clean up", "remove slop", "simplify", "unslop", "reduce
  complexity", "tighten up", "cleanup before PR", "review for unnecessary
  complexity", "too verbose", "over-engineered", "remove unnecessary code",
  "AI generated mess", "simplify this branch", "reduce abstractions", "test
  bloat", "bloated tests", "test case bloat", or tests that only verify library
  or dependency behavior. Also use it for a dedicated simplification pass after
  AI generation. Do not use it as a substitute for correctness, security,
  performance, architecture, or technical-specification review. Report findings
  by default and apply fixes only when explicitly requested.
---

# Codesavers — Post-Generation Code Quality Cleanup

Reviews changed code against 15 simplicity directives and proposes concrete fixes. Targets the specific failure mode of AI-generated code: correct but bloated. Reports findings by default and applies fixes only when explicitly requested.

## Core Philosophy

AI code generators produce code that is usually correct but systematically verbose. The model optimizes for *appearing thorough* — adding defensive checks, optional parameters, helper abstractions, and error handling for conditions that cannot occur. This isn't a bug; it's an alignment artifact. The model would rather include unnecessary code than risk missing something.

The result: code that works but is harder to read, has more state to track, and is more complex than necessary. This skill identifies and removes that accidental complexity.

**For production code, ask: does removing this code change required behavior?** If not, remove it.

**For test code, ask: which behavior owned by this codebase would become unprotected?** If there is no clear answer, remove or consolidate the test.

## Invocation and Change Detection

Treat every invocation as report-only unless the user explicitly asks to apply changes or supplies `--apply`. Accept `--check` as a backward-compatible report-only alias. Accept `--files path1 path2...` to restrict the review and an optional positional base ref.

Build one view of the current working state:

1. Resolve the base ref from the request, then `main` or `master`. Use `git merge-base HEAD <base-ref>` when the ref exists; otherwise use `HEAD`.
2. Get tracked changes with `git diff <base-commit> --name-only` and per-file patches with `git diff <base-commit> -- <file>`. This compares the current working tree with the base and includes committed, staged, unstaged, modified, and deleted tracked content without duplicate patches.
3. Get untracked files with `git ls-files --others --exclude-standard`. Treat the complete contents of each untracked file as added lines. Use `git diff --no-index -- /dev/null <file>` when patch context is useful; exit status 1 means a diff was found.
4. Combine and deduplicate the paths, then apply explicit `--files` restrictions.
5. Filter out lockfiles, `*.generated.*`, `vendor/`, `node_modules/`, images, fonts, `.min.*` files, and the generated or vendored paths listed in `references/gotchas.md`.

If no reviewable changes remain, report "No changed files detected" and stop.

## The 15 Directives — Summary

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
| 15 | Test owned behavior, not dependency behavior | Assertions only repeat an external package's semantics |

For detailed guidance, examples, and before/after code for each directive, load **`references/code-quality-directives.md`**.

## Decision Tree — Which Reference to Load

**"I need detailed guidance on a specific directive"**
→ **`references/code-quality-directives.md`** — Full principle, reasoning, red flags, and before/after examples for all 15 directives.

**"I'm not sure if this is a real issue or a false positive"**
→ **`references/gotchas.md`** — Framework conventions, language idioms, test code exceptions, and cases where complexity is genuinely warranted.

**"I need both"**
→ Load both. The directives file is the primary reference; gotchas is the safety net.

## Output Format

Every review produces findings in this structure:

```
## Codesavers Review

### Summary
- Files reviewed: N
- Findings: N (breakdown by directive)
- Estimated lines removable: N

### File: path/to/file.ts

1. **Directive #N: [Name]** — Lines L1-L2
   - What: [One sentence describing the issue]
   - Why: [The principle violated and the concrete cost]
   - Fix: **[Replace | Delete | Consolidate]** — [Exact change]
   - Resulting code: [Include a fenced code block only for Replace or Consolidate]

### Recommendations
- [Top 3 highest-impact simplifications across all files]
```

**Rules for findings:**
- Only flag code in the diff — unchanged code is out of scope
- Every finding needs a concrete fix — "consider simplifying" is not acceptable
- Use **Replace** with replacement code, **Delete** with an exact target and no artificial code block, or **Consolidate** with the retained code
- Check gotchas before finalizing — false positives destroy trust
- Group related findings that share a root cause
- Estimate lines removable per finding
- For Directive #15, inspect the dependency manifest, tested production code if any, and assertion target; an external import alone is not a finding

## Workflow

### Small diffs (≤10 files)

1. Build the current-state diff
2. Read each existing file and its patch; use the deletion patch for removed files
3. Group all tests for the same behavior with their tested production code, if any, and dependency manifest
4. Evaluate changed lines against the directives
5. Load `references/code-quality-directives.md` for detailed guidance on flagged directives
6. Check `references/gotchas.md` before finalizing
7. Present the report
8. Stop in report-only mode
9. In apply mode, apply the reported fixes, run the project's typecheck and lint commands when present, repair issues introduced by the fixes, and report the validation result without discarding unrelated user changes

### Large diffs (>10 files)

1. Build the current-state diff
2. Spawn `codesaver-reviewer` per file or batch of related files; keep all tests for the same behavior with their tested production code, if any, and dependency manifest
3. Collect reports from subagents
4. Deduplicate and merge findings
5. Present one consolidated report
6. Stop in report-only mode
7. In apply mode, apply fixes sequentially and validate as described above

## What This Skill Does NOT Do

- **Correctness** — Not deciding whether application or dependency behavior is correct. Test review is limited to whether changed tests protect behavior owned by this codebase.
- **Formatting** — Not checking style, indentation, or semicolons. That's the formatter's job.
- **Naming** — Not judging variable or function names. Too subjective, low ROI.
- **Performance** — Not profiling or benchmarking. See the `performance-optimization` skill.
- **Security** — Not scanning for vulnerabilities. Separate concern entirely.
- **Architecture** — Not redesigning the module structure. Just cleaning up within it.
- **Technical specifications** — Not reviewing design documents or requirements. Use Specsavers for specification work.

This skill has one job: reduce accidental complexity in recently changed code.

## All Reference Files

| File | Load when |
|------|-----------|
| **`references/code-quality-directives.md`** | Detailed guidance or examples are needed for a possible finding |
| **`references/gotchas.md`** | Checking every possible finding for framework, language, test, or boundary exceptions |
