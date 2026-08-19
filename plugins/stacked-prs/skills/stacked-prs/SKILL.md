---
name: stacked-prs
description: Design and operate GitHub stacked pull requests with the official github/gh-stack CLI. Use when deciding whether dependent work should be a stack, splitting work into valid layers, or creating, reviewing, updating, handing off, merging, cleaning up, or recovering a stack. Do not use for unrelated, independent, or fork-based pull requests.
---

# Stacked Pull Requests

Use an ordinary pull request (PR) by default. Use a stack only when the changes
have a required merge order and every mergeable prefix is valid.

A stack is a linear series of dependent branches and PRs. One branch and its PR
form a layer. A prefix starts with the bottom layer and includes zero or more
adjacent upper layers. The bottom layer merges first.

## Tool and Authorization Boundary

Use only the official `github/gh-stack` extension for stack metadata. Do not
combine its local metadata with another stack manager.

Before stack work, run `gh stack --version`. Version 0.1.0 is the minimum for
this workflow. If the extension is missing or older, report the requirement.
Install or upgrade it only when the user authorizes that change.

Use `gh stack <command> --help` as the command authority for the installed
version. This skill contains workflow rules and non-obvious failure behavior,
not a duplicate CLI manual.

Creating branches, rewriting history, pushing, changing PR state, merging, and
deleting branches are separate mutations. The user's request must authorize the
mutation before you perform it. An instruction to inspect, explain, review, or
plan a stack does not authorize a write.

## Repository Preflight

Before you design or change a stack:

1. Read repository instructions and accepted architecture or contribution
   documents that govern the change.
2. Identify the default branch, branch-name convention, remotes, required
   checks, commit-signing policy, merge method or queue, and documentation
   contracts.
3. Inspect the worktree and current stack state. Preserve unrelated changes.
4. If the repository has several remotes, use its configured
   `remote.pushDefault` or pass `--remote <name>` to commands that support it.
5. Treat generated files and accepted design documents as part of the same
   layer as their source when separating them would make a prefix misleading.

Repository policy overrides the defaults in this skill. Do not turn one
repository's check command, path rule, signing policy, or merge method into a
universal requirement.

## Stack Invariants

Every stack must satisfy these conditions:

- It tells one related story. Unrelated work uses another PR or stack.
- Each layer has one stated review question.
- Every prefix passes its applicable checks and preserves security,
  authorization, repository contracts, and recovery safety.
- Dependencies are below their consumers.
- Tests and required documentation stay with the behavior they prove.
- A reviewer can assess a layer without unrevealed upper work.
- One history owner at a time performs rebases, restructuring, and pushes on a
  shared stack.
- The stack stays linear. Parallel dependency branches use separate stacks.

Start with two or three unmerged layers. Keep no more than four unless the
repository has a clear reason. Layer count is a coordination limit, not a line
count rule.

## Non-Interactive Agent Rules

Agent harnesses can allocate a terminal. Always use explicit non-interactive
commands instead of relying on TTY detection.

- Inspect with `gh stack view --json`. Do not run bare `gh stack view`.
- Submit with `gh stack submit --auto`. Do not run bare `submit`.
- Initialize with `gh stack init <branch>...`.
- Add a layer with `gh stack add <branch>`.
- Check out with `gh stack checkout <target>`.
- Navigate with `up`, `down`, `top`, `bottom`, or explicit checkout. Do not
  run `gh stack switch`.
- In version 0.1.0, prepare and verify the merge, then require a human to run
  the `gh stack merge` picker. Do not run headless merge or `gh pr merge`.
- Restructure through an approved non-interactive rebuild. Do not run
  bare `gh stack modify`.

Bare `gh stack modify` and `gh stack switch` open interactive interfaces. An
agent can explain those human workflows, but must not run them. The recovery
forms `gh stack modify --continue` and `gh stack modify --abort` are
non-interactive. Run them only with mutation authorization and after verifying
the interrupted modify state.

Version 0.1.0 has no headless form that binds the exact verified PR set. A bare
number is resolved as a stack number before it is resolved as a PR number. A
no-argument headless merge can include a remote-only layer that local JSON did
not show. Require a human to confirm the displayed PR set and target in the
interactive picker. A future typed target is usable only after the installed
command help proves its semantics. For a direct merge, the human selects the
repository's allowed method. If the base uses a merge queue, the queue selects
the method.

## Core Workflow

1. Decide whether the work needs one PR, independent PRs, or a stack.
2. If it needs a stack, plan the full bottom-to-top dependency order before
   implementation.
3. Create one branch per valid review layer and stage paths deliberately.
4. Submit stable layers early. Keep unstable upper layers as drafts.
5. Review each layer on its own, then review the combined diff.
6. Fix feedback in the layer that owns the problem. Rebase affected upper
   layers and renew any review whose diff changed.
7. Merge only a contiguous ready prefix, from the bottom up.
8. After all PRs merge, remove local tracking and clean branches only when the
   user requests cleanup.

Stop when a prefix is invalid, an unexpected diff or conflict appears, a
signature required by repository policy fails, a push partially fails, the
merge set is wrong, or required checks or approvals are missing. Report the
state before you choose a recovery path.

## Reference Router

Open only the reference needed for the current task:

- For PR structure, layer design, branch names, or boundary changes, read
  [stack-design.md](references/stack-design.md).
- For creation, submission, updates, handoff, review, merge, or cleanup, read
  [lifecycle.md](references/lifecycle.md).
- For conflicts, partial pushes, divergence, checkout failures, interrupted
  operations, or restructuring, read
  [recovery.md](references/recovery.md).

Read [stack-design.md](references/stack-design.md) before creating or
restructuring a stack. Read [lifecycle.md](references/lifecycle.md) before any
remote stack mutation. Read [recovery.md](references/recovery.md) only when a
failure or structural correction requires it.
