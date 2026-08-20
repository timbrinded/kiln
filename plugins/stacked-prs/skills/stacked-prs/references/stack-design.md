# Design a Stack

Read this reference before `gh stack init` or before a structural rebuild.

## Choose the PR Structure

Use the smallest structure that represents the dependency.

- Use one ordinary PR for one change with one review question.
- Use independent PRs when changes can merge safely in either order.
- Use a stack when changes have a required merge order.
- Use separate stacks for parallel dependency branches.
- Use one PR, a compatibility step, or a feature flag when no safe
  intermediate state exists.
- Use an ordinary PR for a fork-based contribution.

A common project label or preferred review order does not create a dependency.
Use a stack only when a higher layer must not merge before a lower layer.

The saved review time must exceed the extra rebase, continuous integration,
and coordination cost. If it does not, use one PR.

## Require a Valid Prefix

A prefix contains the bottom layer and zero or more adjacent upper layers.
Every prefix that the team can merge must:

- pass its applicable checks;
- preserve security and authorization invariants;
- keep accepted documentation and repository contracts consistent;
- support a safe stop, rollback, or forward recovery;
- include tests and documentation that prove its behavior.

A prefix does not need to expose a complete user feature. It can add an unused,
compatible foundation behind a feature flag. It must not leave a broken,
insecure, or contradictory repository state.

If no safe prefix exists, keep the work in one PR or redesign it before you
create branches.

## Define Each Layer

State one review question for each layer. A layer can contain several commits
and can need several reviewers. It must not mix unrelated questions.

Do not split work only by directory, file type, task item, or line count.

Start a new layer when all of these facts are true:

1. The next change has a different review question.
2. It depends on the current valid prefix.
3. Its evidence and rollback boundary can stand on their own.

Useful split signals include:

- a stable provider-to-consumer dependency;
- a different risk owner or specialist reviewer;
- a mechanical change that hides a semantic change;
- a current diff that no longer fits one focused review session.

Keep work together when:

- the parts implement one invariant;
- tests are required to prove the changed behavior;
- a migration is unsafe without its compatibility code;
- generated output proves the source change;
- a reviewer needs both parts to assess the design;
- a split makes rollback unsafe;
- proposed layers repeatedly edit the same files.

## Order Dependencies

Put stable providers below their consumers. Typical order is:

```text
(trunk) <- <topic>/model <- <topic>/api <- <topic>/ui <- <topic>/integration
```

This example is not a template to copy. Infer names and layers from the real
change.

Provider-first order is necessary but not always sufficient. If a reviewer
cannot assess a public contract without its first real use, keep the contract
and a small consumer in one layer. Do not add a speculative lower abstraction
with no proved use.

Use these patterns with care:

- Keep behavior with its focused tests. Do not delay proof to a later PR.
- A characterization test can be a lower layer. Do not change behavior there.
- Put a proved refactor below a behavior change. Avoid unused abstractions.
- Put a compatible public contract below its consumer only when it can be
  assessed alone.
- For data migration, expand, migrate, verify, then contract. Do not merge an
  incompatible schema before its repair.
- Keep generated output consistent with its source.
- Keep one security boundary and its tests together.
- Put an end-to-end test above focused lower proof. Do not treat a top-only
  test as proof of lower prefixes.

## Preserve Repository Contracts

Inspect the target repository before you select boundaries. Accepted
architecture documents, indexes, diagrams, schemas, generated artifacts, and
glossaries can form one consistency unit.

If a lower prefix would mislead a reader or contradict an accepted contract,
keep all required updates in one layer. A later optional explainer can be a
separate layer when the earlier prefix remains correct without it.

Do not treat research or generated output as accepted architecture only because
it appears in a lower layer.

## Limit the Stack

Start with two or three layers. Keep two to four unmerged layers.

Keep only one upper layer above an unapproved architecture, security, or schema
decision. If four layers remain unmerged, merge a ready prefix before adding
another layer.

There is no universal line-count limit. Split only when the new layer has one
review question and every prefix remains valid.

## Name Branches

Repository conventions take precedence. If the repository has no convention,
use a conventional change type and a shared topic:

```text
<type>/<topic>-01-<concern>
<type>/<topic>-02-<concern>
<type>/<topic>-03-<concern>
```

Examples of types include `feat`, `fix`, `docs`, `refactor`, and `test`.
`gh-stack` uses branch names exactly as supplied.

## Produce the Stack Plan

Before implementation, show the proposed chain from trunk to top. For each
layer, state:

- branch name;
- one-sentence purpose;
- dependency on the layer below;
- review question;
- checks or evidence;
- initial draft or ready state.

Also state why one PR or independent PRs would be worse for this dependency.
If that reason is weak, do not create a stack.
