---
name: specsaver
description: >-
  Review, rewrite, or author software specifications for technical completeness
  and readability. Use for Specsavers requests, design documents, RFCs,
  requirements, API or protocol contracts, migration plans, and ADR judgements.
  Review existing documents by default; rewrite only when asked. Do not
  substitute for code, security, performance, or architecture review.
---

# Specsavers — Technical Specification Quality

Make the specification as easy as possible for a competent engineer to
understand and implement. Preserve its meaning, not its original wording.

A technically complete document can still need substantial restructuring.
Rewrite difficult prose even when its information is necessary. Delete
non-information; preserve every material constraint, decision, and rationale.

## Modes

**Review** is the default for an existing document, or explicit with `--check`.
Report material technical and readability findings without editing the file.

**Rewrite** applies when the user asks to rewrite, edit, tighten, fix, or apply
changes, or supplies `--apply`. Rewrite only the named scope; report relevant
defects outside it in the closing note. With no narrower scope, rewrite the
complete document. Leave unresolved material decisions as concise questions.

**Author** applies when the user asks to write, draft, or create a
specification. Draft from the supplied brief and sources, then review and
revise it through the same workflow. State material unknowns as questions.

Accept `--files path...` to name targets. Do not implement the described system.

## Core Loop

1. Establish the requested mode and scope. Read the whole specification and
   linked schemas, decisions, conventions, and code where they establish
   meaning or reveal a contradiction. Preserve the original before rewriting;
   retain the brief and supporting sources when authoring.
2. Model the actors, owned state, boundaries, and lifecycle. Read the matching
   artifact lens in [directives](references/directives.md#artifact-lenses).
   Use the questions relevant to this design, not as mandatory headings or a
   classification to report. Load the directive explanations only when needed
   to sharpen a judgement.
3. Review from both technical and readability perspectives. For substantial
   work, follow the delegation workflow below.
4. Check findings against the original sources and resolve conflicts through
   evidence. Group findings with the same cause. In rewrite or author mode,
   the parent alone produces one coherent document from accepted findings.
   Reviewer agreement does not establish an unstated fact.
5. Verify the complete result against the original sources. After substantial
   edits, return it to the same specialists. Correct concrete defects and
   recheck affected passages; stop broad style reviews once checks pass.
   Before replacing a target, reconcile any intervening user edits.

## Independent Review

Delegate automatically when the work involves interacting sections, linked
documents, substantial lifecycle or contract reasoning, or document-wide
restructuring. For small, self-contained passages, the parent applies both
perspectives directly. Honour explicit requests to use or avoid delegation.

Load [the review workflow](references/review-workflow.md) when delegating or
preparing a substantial rewrite or draft. Use two read-only specialists:

- **Technical:** load [technical reviewer](references/technical-reviewer.md)
  to check material behaviour, contracts, contradictions, and missing decisions.
- **Structure and readability:** load
  [readability reviewer](references/readability-reviewer.md) to check how the
  reader learns the design, including organization and sentence connections.

Use native subagent tools with the packaged roles and inherited model and
reasoning settings. Give both reviewers the same unchanged source, authority,
mode, and scope, without the parent's diagnoses or either reviewer's findings.
Wait for both initial reviews before adjudicating. Reviewers neither edit nor
delegate further; they return findings only to the parent. The original remains
authoritative; findings never substitute for it.

For large sets, keep dependent documents together and review coherent groups
within available concurrency. Reconcile findings across groups before editing.

If delegation or a specialist pass cannot complete, apply the missing
perspective in the parent and disclose the missing independent check.

## Directives

1. **Write for the human reader.** Order material by execution or learning
   dependencies. Keep related rules together and make important claims and
   sentence connections clear. Use the readability reference for diagnostics.
2. **Preserve semantics, not prose.** Wording, order, and representation may
   change freely while every material fact survives.
3. **Describe the system positively.** Establish what components own and do
   before adding necessary prohibitions. Keep a prohibition when it is itself an
   integrity, security, compatibility, or scope invariant that the positive
   model does not close.
4. **Remove non-information.** Delete repetition, ceremony, fake alternatives,
   fanciful non-goals, generic caveats, empty or `N/A` headings, and
   implementation narration that constrains nothing.
5. **Decide material behaviour.** Do not leave product, architectural, state,
   ownership, failure, or compatibility decisions to the implementer. Do leave
   replaceable local mechanics to implementation.
6. **Make behaviour precise.** Use stable terms, explicit actors, observable
   outcomes, legal transitions, and measurable qualities where material.
   Distinguish requirements, decisions, rationale, assumptions, examples, and
   questions. Make material behaviour verifiable.
7. **Treat boundaries as contracts.** Specify the subset of identity, schema,
   ordering, atomicity, retries, errors, authority, and compatibility needed
   for correct interaction across each boundary the design creates. Where a
   boundary touches persisted data, public compatibility, or deployed
   components, that includes migration, coexistence, rollout, and reversal
   semantics.
8. **Use real rationale only.** Document alternatives only when reasonable
   engineers could advocate them under the stated constraints. Recommend a
   separate ADR only for a genuine architectural fork with durable,
   non-obvious reasoning that the canonical specification does not already
   preserve.
9. **Do not invent.** When the source does not determine a material answer,
   state the question plainly. A plausible answer is not an established one.
   Polishing must not introduce causation, guarantees, or changes to condition
   scope, obligation strength, or ordering.
10. **Check the finished document as a whole.** Reconcile terminology, values,
    examples, diagrams, and verification with the design.

## Boundaries

- Leave already-clear prose alone. Judge reader effort, not word count; do not
  impose house style or lint grammar and Markdown.
- Do not add sections, caveats, or mitigations for concerns the design does not
  activate.
- Do not fail an exploratory document because decisions remain open. Do flag
  unknowns disguised as decisions and approved documents that still defer
  material behaviour.
- Do not require a universal template, assign a score, or create an ADR unless
  the user asks for that record.
- Raise an edge case, or call a gap blocking, only when two compliant
  implementations could differ materially in a way the stated problem cares
  about. Equivalent observable behaviour is sufficient; local mechanics may
  differ. Do not manufacture findings for a complete document.

## Reporting

Begin a review with `## Specsavers`. Lead with a one-line verdict. Give each
finding its evidence, consequence, and source-supported correction or author
question. Include replacement prose when useful. Do not praise, recap
irrelevant checks, or reproduce the document. With no material findings, say
so in one or two sentences.

After rewriting or authoring, briefly explain substantive changes, implied
readings made explicit, unresolved decisions, and incomplete independent checks.

For uncertain judgements about deleting detail, prohibitions, ADRs, or quality
targets, consult [gotchas and examples](references/gotchas-and-examples.md).
