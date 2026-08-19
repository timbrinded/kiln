# Recover or Restructure a Stack

Read this reference after a failed command, unexpected stack state, or invalid
layer boundary. Preserve branches, PRs, and unrelated work until the cause is
known.

## Read the Exit Code

Branch on the command exit code and stderr. Do not infer success from friendly
text alone.

- Code 0 means success or a non-interactive sync abort. Check the result for
  `Sync aborted`.
- Code 1 is a generic error. Read stderr and inspect state.
- Code 2 means the stack was not found. Confirm the target.
- Code 3 is a rebase conflict. Use the conflict procedure below.
- Code 4 is a GitHub API failure. Check authentication and network state.
- Code 5 means invalid arguments. Read `gh stack <command> --help`.
- Code 6 means the branch belongs to several stacks. Check out a branch that
  is unique to the intended stack.
- Code 7 means a rebase is active. Continue after resolution or abort.
- Code 8 means the stack file is locked. Wait, then retry once.
- Code 9 means stacked PRs are unavailable. Offer an ordinary PR workflow.
- Code 10 means a modify session was interrupted. Verify its state before an
  authorized `gh stack modify --continue` or `gh stack modify --abort`.

Repeated failure is not permission to use destructive Git commands or to
change remote state. Stop after the documented recovery path fails once and
report the exact state.

## Rebase Conflicts

`rebase` and `sync` both exit 3, but they leave different states.

After `gh stack rebase`, the operation pauses at the conflict. Inspect the
listed paths, resolve only the intended conflict, and stage only those paths:

```bash
git add <resolved-paths>
gh stack rebase --continue
```

Repeat only for another expected conflict. If unrelated commits or conflicts
appear, abort the complete stack rebase:

```bash
gh stack rebase --abort
```

After a failed `gh stack sync`, the command restores the branches to their
pre-sync state. Run `gh stack rebase` to reproduce the conflict in a resumable
operation, then resolve and continue as above.

Do not use plain `git rebase --continue` for a `gh-stack` rebase.

## Partial Push or Submit Failure

`gh stack push` and `gh stack submit` are not atomic. A branch whose lease
passes can update even when another branch or later PR operation fails.

After any rejection:

1. Stop all stack writes.
2. Fetch the selected remote.
3. Compare every local stack head with its remote head.
4. Identify which branches moved and who moved them.
5. Choose one history owner before a retry.
6. Rebase or reconcile the complete affected stack, verify it, then retry once.

Do not force-push without a lease. Do not retry blindly.

## Local and Remote Divergence

The local stack and the GitHub stack diverge when their branch chains change in
different ways. In non-interactive mode, `gh stack sync` can print both chains,
make no changes, print `Sync aborted`, and exit 0.

Choose which chain is authoritative before changing state.

To keep the remote chain, remove only local tracking and check out the remote
stack again:

```bash
gh stack unstack --local
gh stack checkout <stack-number-or-PR>
```

To keep the local chain, first record its trunk and exact bottom-to-top branch
order, then confirm the exact remote stack with the user. Remove its GitHub
grouping and inspect the result. If queued or auto-merge PRs keep part of the
remote stack in place, stop without rebuilding. If the stack is fully
dissolved, restore local tracking before submission:

```bash
gh stack unstack <stack-number>
gh stack init --base <trunk> <bottom-branch> <next-branch> <top-branch>
gh stack view --json
gh stack submit --auto --remote <remote>
gh stack view --json
```

Remote unstacking changes GitHub state. It does not delete branches or PRs, but
it still requires explicit authorization. Verify the rebuilt chain and every PR
base before the submit. Do not submit if the chain differs from the recorded
authoritative chain.

## Checkout Conflict

`gh stack checkout <remote-target>` cannot overwrite different local tracking
for the same branches. There is no non-interactive force flag.

Inspect both chains. If the remote chain is authoritative and the worktree is
clean, remove only local tracking, then retry:

```bash
gh stack unstack --local
gh stack checkout <stack-number-or-PR>
```

Do not use bare `gh stack unstack` for local recovery because it also changes
the GitHub stack.

## Restructure Invalid Layers

Correct a bad boundary early. Do not preserve it only because PRs exist.

A human operator can use the interactive `gh stack modify` workflow. An agent
must not open that terminal interface. The agent has two safe restructuring
choices:

1. Explain the exact human modification and stop.
2. With authorization, perform a non-interactive rebuild.

For a rebuild:

1. Start with a clean worktree.
2. Record branch tips, parent ranges, stack number, PR URLs, and remote heads.
3. Confirm whether only local tracking or the GitHub grouping must change.
4. Unstack at the approved scope.
5. Rewrite ancestry only after tracking is removed and the replay ranges are
   explicit.
6. Reinitialize existing branches in the corrected bottom-to-top order.
7. Submit with `--auto`, verify every PR base, and renew changed reviews.

For a local tracking rebuild that preserves the intended GitHub composition:

```bash
gh stack unstack --local
gh stack init --base <trunk> <bottom-branch> <next-branch> <top-branch>
gh stack submit --auto --remote <remote>
gh stack view --json
```

If the approved restructure must replace the GitHub grouping, use the exact
stack number and remove that grouping before reinitialization:

```bash
gh stack unstack <stack-number>
gh stack init --base <trunk> <bottom-branch> <next-branch> <top-branch>
gh stack submit --auto --remote <remote>
gh stack view --json
```

Remote unstacking can leave merged, merging, or queued PRs in the stack.
Inspect the result before reinitialization.

This sequence does not correct Git ancestry by itself. If the ancestry is
wrong, design the commit-range replay for the actual branches. Do not copy a
generic `git rebase --onto` sequence without proving each old parent and range.

After a restructure, re-run checks and review every changed layer and the
combined diff.

## Interrupted Modify Session

An agent must not start bare `gh stack modify`. If an interrupted session has
the expected conflicts, an authorized human or agent can resolve them, stage
only the intended paths, and run:

```bash
gh stack modify --continue
```

With authorization, restore the pre-modify state instead:

```bash
gh stack modify --abort
```

Exit code 10 means this recovery is required before normal stack work.

## Locked Stack State

Exit code 8 means another `gh-stack` process owns the stack lock. Wait for that
process to finish, then retry once after approximately five seconds. If the
lock persists, identify the writer and stop. Do not delete lock files while a
writer can still be active.

## Squash-Merge Recovery

After a parent PR is squash-merged, its original commits are absent from trunk.
Use `gh stack sync`; it detects the merged layer and replays remaining layers
onto the new trunk state.

If that sync conflicts, it restores the previous branch state and exits 3.
Start `gh stack rebase`, resolve the conflict there, and continue through the
documented rebase flow.

## Merge Failure

A direct `gh stack merge` is all-or-nothing. If GitHub rejects one PR, none in
the selected set merge. Read the reported repository-rule failure, correct it,
and repeat all prefix checks before another merge request.

When a merge queue is active, the selected PRs enter the queue together but can
land in separate groups. Do not report queue submission as an atomic completed
merge.
