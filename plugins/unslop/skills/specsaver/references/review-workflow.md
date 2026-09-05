# Review, Adjudication, and Verification

## Prepare a shared source

Read the source before dispatching. Preserve exact originals in a temporary
workspace outside the target document set before any rewrite. Do not create
review scaffolding in the user's specification. Retain the original path for
each snapshot so relative links can be resolved against their original location.
Reconcile any material supporting-source changes before finalizing.

For authoring, review the parent's draft against the unchanged brief and
supporting sources.

Resolve role and source locations from the loaded skill, not the process's
working directory or a hard-coded installation path. Use the host's resource
reader for resource-backed skills. Give each reviewer:

- its role reference and the shared Specsavers directives and boundaries;
- the mode, initial-review or verification phase, and authorized edit scope;
- the full target snapshot or draft and original locations;
- the relevant authoritative sources, including the authoring brief;
- for verification, the candidate and accepted findings it should check.

Do not provide the parent's preferred interpretation or the other reviewer's
findings during the initial independent reviews. Reviewers may consult linked
sources where necessary; they must distinguish source evidence from inference.
Start reviewers with fresh, focused context instead of forking the parent's
deliberation. When the dispatch tool supports history selection, select no
inherited conversation (for example, `fork_turns: "none"`) and supply the
assignment and source locations explicitly. Omit model and reasoning overrides
so the host inherits the parent's settings. If history cannot be excluded,
defer proposed diagnoses and outlines until both initial reviews have returned.

Use native subagent tools and a read-only tool surface where supported.
Do not install personal agent definitions or invoke an external agent runner.
On Claude Code, the packaged specialist adapters load these same references.

## Findings and adjudication

Wait for both initial reports. Judge each finding against the full source;
do not count votes or splice reports into a new specification. Merge findings
with a common cause. Reject speculative gaps and stylistic preferences that
do not establish reader difficulty. Preserve the distinction between a contract
gap and a complete contract that is difficult to follow.

The parent writes the consolidated review or authorized candidate using the
original sources. Reviewer summaries are never the rewrite source.

If evidence establishes a correction, make it. If it leaves competing material
interpretations, put a concise question where the decision belongs. Do not
close an explicit open decision merely because a contextual source states a
value; establish which source has authority over that decision. Do not invent
a hierarchy between prose, tables, examples, and verification obligations from
their format or position. An unresolved conflict remains an author decision.
Report findings outside the rewrite scope without editing those passages.

## Verification and delivery

Send the candidate and original sources back to the same specialists using
their verification instructions. The technical reviewer checks preservation
and the readability reviewer checks that the intended improvements work as
one document.

Only the parent edits. Resolve concrete defects, then recheck affected passages
with the relevant reviewer. Do not reopen settled design choices or ask for
another broad style review after the checks pass. Report material questions
that remain open instead of fabricating answers to obtain a clean verdict.

Before applying the candidate, compare the target with the saved original. If
the user has edited it, preserve those edits and reconcile the candidate with
the new source; repeat checks affected by that reconciliation. Ask only when
conflicting material intentions cannot be resolved from the source.

An initial review that never examined the candidate is not verification.
Disclose failed or unavailable independent checks as required by `SKILL.md`.
Return one result in the requested mode and location; keep snapshots and
internal reports out of the specification.
