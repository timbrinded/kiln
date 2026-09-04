---
name: specsaver
description: >-
  This skill should be used when the user asks for "Specsavers", to "review
  this technical spec", "check this design document", "tighten this RFC",
  "rewrite this spec for clarity", "find ambiguity", "make this
  implementation-ready", "remove documentation slop", "write a technical
  specification", "review these requirements", "check this API or protocol
  spec", "review this migration plan", "decide whether this needs an ADR", or
  otherwise improve a software engineering design document. It reviews,
  rewrites, and authors technical specifications so that a competent engineer
  can understand and implement them with the least effort. Existing documents
  are reviewed by default and rewritten only when the user asks. Do not use it
  as a substitute for code, security, performance, or architecture review
  merely because the target is Markdown.
---

# Specsavers — Technical Specification Quality

Make the specification as easy as possible for a competent engineer to
understand and implement. Preserve its meaning, not its original wording.

A specification has two ways to fail. It can leave out a decision the
implementer should never have had to make, or it can bury a correct design
under prose that is harder to read than it needs to be. Specsavers treats both
as defects. A passage can be necessary and still be badly written; preserve its
information while rewriting its language, order, or representation. Technical
readability is not cosmetic. A specification fails when its design is correct
but unnecessarily difficult to understand.

Rewrite awkward, dense, repetitive, badly ordered, or indirect prose even when
its underlying information is necessary. Delete prose that conveys no material
information. Never delete a material constraint, decision, or rationale.

## Modes

**Review** is the default for an existing document. Read the complete
specification. Identify missing decisions, contradictions, weak requirements,
and prose that unnecessarily burdens the reader. Show replacement prose when
that is the clearest way to state the fix. Do not edit the file.

**Rewrite** applies when the user asks to rewrite, edit, tighten, fix, or apply
changes, or supplies `--apply`. Read the whole document for context, then
rewrite only the scope the user named and leave the rest as it is; report
defects you see outside that scope instead of fixing them uninvited. When the
request covers the whole specification or names no narrower scope, rewrite the
complete document. Rewrite for clarity, structure, precision, and economy.
Preserve every material constraint, decision, and rationale. Do not invent
unresolved decisions; leave them as concise questions in the document.

**Author** applies when the user asks to write, draft, or create a
specification. Produce the smallest document that clearly transfers the known
design. Include only the concerns the design activates. State real unknowns as
questions.

Accept `--check` as an explicit review-only convention and `--files path...`
to name targets. Do not implement the system the specification describes.

## Core Loop

1. Read the whole specification and the local context it depends on: linked
   schemas, decisions, conventions, and code only where they establish meaning
   or reveal a contradiction.
2. Understand the system the author intends. Form a short private model of its
   actors, owned state, boundaries, and lifecycle.
3. Identify what the document primarily is: a design specification, a
   requirements document, an API or protocol contract, a migration or rollout
   plan, an ADR, or a composite of these. Use the matching artifact lens in
   `references/directives.md` to see which of that kind's questions the design
   activates and whether it answers them. Lenses are questions to consider, not
   classifications to report, templates, checklists, or mandatory headings.
4. Apply the directives below using engineering and editorial judgement. They
   overlap and feed one holistic judgement; they are not gates to pass.
5. Remove prose that conveys no material information.
6. Rewrite necessary prose that is harder to understand than it needs to be.
7. Identify missing material decisions without inventing them.
8. Re-read the result as one coherent document.

## Directives

1. **Write for the human reader.** Make the design easy to scan, understand,
   and retain. Order material the way the system executes or the way a reader
   must learn it. Rewrite necessary information when its current expression is
   difficult.
2. **Preserve semantics, not prose.** Do not delete material constraints, but
   do not treat their wording, order, or paragraph structure as sacred.
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
   outcomes, clear state transitions, and measurable qualities where they
   matter. Keep requirements, decisions, rationale, assumptions, examples, and
   open questions distinguishable, and make every material behaviour
   verifiable.
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
10. **Check the finished document as a whole.** Reconcile terminology, values,
    examples, diagrams, and verification with the design.

## What Readability Licenses

Specsavers may, without changing meaning:

- break an overloaded paragraph into stages;
- turn verification prose into a scannable list of test obligations;
- move a buried invariant beside the behaviour it constrains;
- reorder material into execution order;
- replace circular or indirect explanation with direct statements;
- use a small table where prose creates needless working-memory load;
- merge duplicated facts into one authoritative statement; and
- name the actor where passive voice hides responsibility.

It does not impose house style, lint grammar or Markdown, or rewrite prose
that is already clear.

## Boundaries

- Do not invent values, policies, boundaries, alternatives, or decisions.
- Do not add sections, caveats, or mitigations for concerns the design does not
  activate. Visible completeness is not evidence of rigour.
- Do not fail an exploratory document because decisions remain open. Do flag
  unknowns disguised as decisions and approved documents that still defer
  material behaviour.
- Do not require a universal template, assign a score, or create an ADR unless
  the user asks for that record.
- Do not replace a requested code, security, performance, or architecture
  review because the target is a document.
- Long is not automatically bad. Short is not automatically good. Judge
  information per unit of reader attention.
- Keep the review proportionate to the defects. A specification is complete
  when competent implementers would make the same material product,
  architectural, and contract decisions from it and produce materially
  equivalent observable behaviour; local mechanics may differ. It does not need
  to pre-empt every operational edge case. When a document decides its material
  behaviour, say so briefly. Raise an edge case only when two compliant
  implementations would differ in a way the stated problem cares about, and
  call a gap blocking only when it meets that test.

## Reporting

Begin a review with `## Specsavers`. Lead with a one-line verdict. Give each
finding its evidence, its consequence for an implementer or reader, and a
concrete fix. Show replacement prose when the source determines it. When it
does not, state the decision the author must make. Group findings that share a
root cause. Do not praise, recap checked-but-irrelevant concerns, or reproduce
the document. If there are no material findings, say so in one or two
sentences.

After a rewrite or authored document, add a short note listing what changed in
substance, any implied reading you made explicit, and which decisions remain
unresolved.

For a large document set, delegate coherent groups to `specsaver-reviewer`
agents, keeping documents together when their meanings depend on each other,
then merge and deduplicate their findings.

## Reference Files

| File | Load when |
|---|---|
| `references/directives.md` | Core loop step 3 reads the artifact lens for the document's type; load the rest when the reasoning or a worked example for a directive would sharpen a judgement |
| `references/gotchas-and-examples.md` | A judgement is uncertain; most often when deleting detail, flagging a prohibition, recommending an ADR, or quantifying a quality |
