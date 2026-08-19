# Operate a Stack

Read this reference before a local or remote stack mutation.

## Discover Repository Policy

Do not copy policy from another repository. Inspect the local sources of truth.

- For the default branch and remotes, inspect local Git configuration and
  repository metadata.
- For branch names, inspect repository instructions and contribution guides.
- For commit signing, inspect instructions, existing commits, and Git
  configuration.
- For checks, inspect dependency manifests, task runners, workflows, and
  contribution guides.
- For architecture consistency, inspect accepted decisions, models, indexes,
  diagrams, and generated sources.
- For merge behavior, inspect repository rules and current PR metadata.
- For cleanup, inspect branch policy and the user's request.

If a required policy cannot be discovered and it changes the result, ask the
user before the mutation.

## Prepare the Tool

Check the installed extension and authentication:

```bash
gh stack --version
gh auth status
```

The workflow requires `github/gh-stack` version 0.1.0 or later. Installation
and upgrade commands change the user environment, so run them only with
authorization:

```bash
gh extension install github/gh-stack
gh extension upgrade stack
```

If the repository has several remotes, identify the intended one. Configure
`remote.pushDefault` only when the user authorizes a Git configuration change.
Otherwise pass `--remote <name>` to commands that support it.

`gh stack init` can enable Git rerere. If the command would prompt, ask before
changing repository configuration or tell the user what configuration is
required.

## Create the Stack

Read [stack-design.md](stack-design.md) and agree on the complete
bottom-to-top plan before you write implementation files.

Create the first branch and commit only its paths:

```bash
gh stack init <bottom-branch>
git add <bottom-layer-paths>
git commit -m "<message>"
```

Add each dependent layer from the current top branch:

```bash
gh stack add <next-branch>
git add <next-layer-paths>
git commit -m "<message>"
```

Prefer normal `git add` and `git commit` to `gh stack add -Am`. Deliberate
staging prevents unrelated work from entering a layer. Uncommitted changes
carry to a newly added branch, so commit or stash first when the next layer
must start clean.

If repository policy requires signed commits, verify each commit after it is
created. Do not push a stack that fails its signing policy.

## Submit and Describe the Layers

An agent submits without the interactive editor:

```bash
gh stack submit --auto --remote <remote>
gh stack view --json
```

Omit `--remote` only when one remote is unambiguous or
`remote.pushDefault` is configured.

With `--auto`, new PRs are drafts unless `--open` is present. Use `--open` only
when every included PR is ready. For mixed readiness, submit drafts, then mark
only the valid ready prefix ready with `gh pr ready <PR-URL>`.

Submission is not atomic. Earlier branch or PR updates can remain when a later
step fails. Inspect every branch and PR before a retry.

Do not wait for the full stack before you expose a stable lower layer for
review.

Each PR description needs only the layer-specific context that GitHub's stack
map does not show:

```markdown
## Stack layer

Adds: <one-sentence purpose>
Depends on: <lower PR or none>
Review question: <one question>
Checks: <commands or evidence>
Upper context: <one sentence or none>
```

Preserve repository PR templates and existing descriptions when you add this
block. `submit --auto` cannot set a custom title or body; update them after
submission with the repository's normal GitHub workflow.

If a reviewer must read an unrevealed upper layer to understand the PR, correct
the boundary.

## Routine Sync

Use sync when the user asks to reconcile local branches, GitHub stack state,
trunk changes, and PR state in one operation:

```bash
gh stack sync --remote <remote>
gh stack view --json
```

Sync can fetch, rebase, push, and change stack metadata. Do not run it for a
read-only status request. In non-interactive mode, divergence can print
`Sync aborted` and exit 0 without a sync. Inspect the output and state.

Use `--prune` only when the user requests local branch cleanup. It deletes
local branches for merged PRs.

## Change a Lower Layer

Only the current history owner changes shared stack history.

Start with a clean worktree, inspect the stack, and check out the layer that
owns the change:

```bash
git status --short
gh stack view --json
gh stack checkout <branch-or-PR>
```

Edit, stage, and commit the correction in that layer. Then replay all affected
upper layers:

```bash
gh stack rebase --upstack --remote <remote>
```

Before publication, rebase the complete stack against current remote state and
inspect the combined result:

```bash
gh stack rebase --remote <remote>
gh stack top
git diff <remote>/<trunk>...HEAD
```

If signing is required, verify every rewritten commit before push. If a diff is
unexpected, stop and inspect it.

Do not use plain `git rebase`, `git reset`, or interactive history editing
while `gh-stack` tracks the stack. These commands can desynchronize the saved
layer boundaries.

If repository policy requires the history owner to sign rewritten commits,
use the local CLI rebase. Do not use GitHub's web rebase action, because a
server-side rewrite can fail that signing policy.

Publish only after the diff, checks, and signatures required by repository
policy pass:

```bash
gh stack push --remote <remote>
gh stack view --json
```

`gh stack push` uses a lease for each branch, but the update is not atomic. If
one branch is rejected, stop and follow [recovery.md](recovery.md).

## Transfer History Ownership

Use an explicit handoff when another person must rebase or push the stack.

The current owner must:

1. Stop stack writes.
2. Ask the new owner to stop writes.
3. Rebase, verify, and push the full stack.
4. Share the stack number, one full PR URL, and `gh stack view --json` output.

The new owner must start with a clean worktree, then fetch and check out the
remote stack:

```bash
git status --short
git fetch <remote>
gh stack checkout <stack-number-or-PR-URL>
gh stack view --json
git branch -vv
```

Compare each local head and upstream before the new owner performs a write.
Tell collaborators who now owns stack history.

## Review the Stack

Review stable layers as soon as they are ready. Reviewers can work in parallel,
but the final semantic review moves from bottom to top.

GitHub evaluates required reviews, checks, CODEOWNERS, and pull-request
workflows against the stack trunk, not only the direct parent branch. Apply the
trunk rules to every PR. A CODEOWNERS change in a lower unmerged layer does not
govern an upper PR.

For each layer:

1. Assess its stated review question.
2. Inspect its direct diff against the branch below it.
3. Run the checks required for that prefix.
4. Confirm its contracts, tests, and rollback or forward-recovery evidence.

After a lower-layer diff changes, inspect every upper-layer diff. Renew a
review when its diff changed, even if GitHub still shows an approval.

After the final rebase, perform a separate combined review from trunk to the
top branch. This review finds cross-layer inconsistencies. It does not replace
the required approval on each PR.

Fix feedback in the layer where the defect originates. Do not add a top repair
PR for a defect that leaves a lower prefix invalid.

## Merge a Ready Prefix

Merging requires an explicit user request for the exact prefix.

Before merge, verify that every PR in the prefix:

- is open and ready, not draft;
- has its required approvals and checks;
- has the expected remote head;
- satisfies repository signing policy;
- remains valid in the combined prefix diff.

In version 0.1.0, no headless merge form binds the exact PR set that was
verified:

- A bare numeric target is resolved as a stack number before it is resolved as
  a PR number.
- A no-argument headless merge fetches the current remote stack and can include
  a remote-only layer that `gh stack view --json` did not show.
- A separate preflight cannot remove the race before merge resolution.

An agent must not run `gh stack merge --yes` in this version. Prepare the exact
bottom-to-top merge set and require a human to check out a branch that belongs
only to the intended stack, then run the interactive picker:

```bash
gh stack merge
```

The human must confirm the displayed stack, every selected PR, the highest PR,
and, for a direct merge, the allowed merge method. The method is `merge`,
`squash`, or `rebase`. A merge queue selects the method. Cancel if the displayed
set differs from the authorized set. Do not use `gh pr merge` for a native
stack.

If a later installed version adds a typed PR-set or PR-target option, an agent
can use it only after `gh stack merge --help` proves that it cannot be
interpreted as a stack number and that the server operation binds the verified
set.

A direct stack merge is all-or-nothing. Queue submission is grouped, but the
queue can land PRs in separate groups. Report which behavior applies.

For a merge queue, monitor every selected PR until all are merged or one fails
or is ejected. Enqueueing is not completion. Do not change upper-layer history
while a selected PR is still queued or merging. Report a failed or ejected PR
and stop before another mutation.

After the complete prefix lands, reconcile any remaining upper layers only with
authorization:

```bash
gh stack sync --remote <remote>
gh stack view --json
```

Then re-run affected checks, inspect changed layer and combined diffs, and renew
reviews whose diffs changed before the next prefix merge.

## Clean Up

After every PR in the stack is merged, remove local stack tracking:

```bash
gh stack unstack --local
git switch <trunk>
git pull --ff-only <remote> <trunk>
```

`unstack --local` does not delete PRs or branches. Before deleting any local or
remote branch, confirm its PR is merged and confirm that the user requested
branch cleanup.

A completed stack cannot be extended. Start a new stack for later work.
