---
description: Review changed code for AI-generated verbosity, unnecessary complexity, and defensive coding patterns — then apply concrete simplifications
argument-hint: "[base-branch] [--check] [--files file1 file2...]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Review changed code for AI slop using the unslop skill.

**Parse arguments from `$ARGUMENTS`:**

- `--check` → Report-only mode: present findings without applying any fixes (dry run)
- `--files file1 file2...` → Only review these specific files instead of auto-detecting from git
- First positional argument → Base branch for git diff (default: auto-detect main/master)
- No arguments → Auto-detect changed files, review, and apply fixes

**Step 1: Detect changed files**

If `--files` was provided, use those files directly. Otherwise:

1. Detect the base branch: check if `main` or `master` exists, or use the merge-base
2. Get the list of changed files:
   - `git diff --name-only <base>...HEAD` for committed changes on the branch
   - `git diff --name-only` for unstaged changes
   - `git diff --name-only --staged` for staged changes
   - Combine and deduplicate
3. Filter to code files only (exclude lockfiles, generated code, vendored dependencies, images, etc.)
4. If no changed files found, report "No changed files detected" and exit gracefully

**Step 2: Load the unslop skill**

Load the unslop skill's SKILL.md for the review framework and directive summary.

**Step 3: Review each file**

For each changed file (or batch of related files):

1. Read the file contents
2. Get the diff for that file: `git diff <base>...HEAD -- <file>`
3. Focus review ONLY on changed lines and their immediate context
4. Evaluate against the 14 directives from the skill
5. Load `references/code-quality-directives.md` for detailed guidance on flagged directives
6. Check `references/gotchas.md` before finalizing — remove false positives
7. For each finding, record: directive number, line range, what's wrong, why, concrete fix

For large diffs (>10 files), spawn the unslop-reviewer subagent per file or batch for parallel review.

**Step 4: Present report**

Output findings in the skill's format:

```
## Unslop Review

### Summary
- Files reviewed: N
- Findings: N (by directive breakdown)
- Estimated lines removable: N

### File: path/to/file.ts

1. **Directive #N: [Name]** — Lines L1-L2
   - What: [Observable issue]
   - Why: [Principle violated and the cost]
   - Fix: [Concrete code change]

...

### Recommendations
- [Top 3 highest-impact simplifications]
```

**Step 5: Apply fixes (default) or skip (--check)**

Unless `--check` was passed, apply the fixes:

1. Apply each suggested fix using the Edit tool
2. After all edits, run the project's typecheck command (detect from package.json scripts or tsconfig)
3. Run the project's lint command if available
4. Report any issues introduced by the fixes
5. If typecheck/lint fails, revert the problematic edit and note it in the report

If `--check` was passed, skip this step — the report is the final output.
