# Review, Adjudication, and Verification

This is the parent workflow for substantial Specsavers work. The two reviewer
references define bounded assignments; they do not start this workflow again.

## Prepare a shared source

Read the source before dispatching. Preserve exact originals in a temporary
workspace outside the target document set before any rewrite. Do not create
review scaffolding in the user's specification. Retain the original path for
each snapshot so relative links can be resolved against their original location.
Both reviewers inspect the same version; if a material supporting source
changes, reconcile that change before finalizing.

For authoring, keep the brief and authoritative supporting sources unchanged.
The parent writes a first draft in the temporary workspace. The draft is the
review target, but the brief and supporting sources determine what it may say.

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

Use native subagent dispatch, wait, and follow-up tools. Inherit model and
reasoning settings. Request read-only operation, and select a read-only tool
surface where the host supports one. Do not install personal agent definitions
or invoke an external agent runner. On Claude Code, the two packaged specialist
adapters load these same references.

## Findings and adjudication

Each specialist returns a concise internal report. For each finding include
the source location, evidence, reader or implementation consequence, and a
concrete proposed correction. If the source does not determine the correction,
state the missing decision instead. A restructuring finding may span sections
and include a proposed outline. No findings is a valid result.

Wait for both initial reports. Judge each finding against the full source;
do not count votes or splice reports into a new specification. Merge findings
with a common cause. Reject speculative gaps and stylistic preferences that
do not establish reader difficulty. Preserve the distinction between a contract
gap and a complete contract that is difficult to follow.

In review mode, return one consolidated review without changing the target.
In rewrite mode, the parent writes one candidate covering only the authorized
scope. In author mode, the parent revises its draft. Preserve all material
constraints and real rationale, using the original sources throughout.
Reviewer summaries cannot capture every fact and are never the rewrite source.

If evidence establishes a correction, make it. If it leaves competing material
interpretations, put a concise question where the decision belongs. Do not
close an explicit open decision merely because a contextual source states a
value; establish which source has authority over that decision. Do not invent
a hierarchy between prose, tables, examples, and verification obligations from
their format or position. An unresolved conflict remains an author decision.
Keep
findings outside a scoped rewrite in the closing report; do not fix them
uninvited, including changes that would require extending the authorized scope.

## Verification and delivery

Send the candidate and original sources back to the same specialists using
their verification instructions. The technical reviewer checks preservation
and the readability reviewer checks that the intended improvements work as
one document. Reuse the reviewers; a fresh team is not required for this pass.

Only the parent edits. Resolve concrete defects, then recheck affected passages
with the relevant reviewer. Do not reopen settled design choices or ask for
another broad style review after the checks pass. Report material questions
that remain open instead of fabricating answers to obtain a clean verdict.

Before applying the candidate, compare the target with the saved original. If
the user has edited it, preserve those edits and reconcile the candidate with
the new source; repeat checks affected by that reconciliation. Ask only when
conflicting material intentions cannot be resolved from the source.

For a failed or unavailable specialist pass, complete the corresponding
perspective in the parent and state which independent check did not happen.
Do not claim independent verification from a parent's self-check or from a
reviewer's initial report that never examined the candidate.

Apply the candidate only in rewrite or author mode. For an authored response
without a requested file, return the verified text. The user receives one
result, with substantive changes, explicit interpretations, and unresolved
decisions noted briefly. Temporary snapshots and internal reports are not new
sections of the specification.
