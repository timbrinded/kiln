# Gotchas and False-Positive Controls

Read this file before finalizing every Specsavers finding. Default to no finding
when evidence is uncertain. False positives make the skill less useful faster
than missed minor issues.

## Concise Does Not Mean Incomplete

Do not flag a document merely because it is short. A small pure-function change
may need only the problem, behavioral contract, and focused verification. Apply
profile and maturity, then ask whether an omitted fact permits a materially
different implementation.

Do not add common headings to make a document look complete. Empty Security,
Migration, Observability, Risks, and Rollback sections are not evidence of rigor.

Optimize for information density, not word count. A long state table or
protocol contract can be dense because every row constrains behavior. A short
section of generic caveats can waste attention without adding design
information. Preserve necessary detail and remove cognitive overhead.

## Exploratory Questions Are Valid

An exploratory note can contain live alternatives and managed open questions.
Do not demand implementation decisions at that maturity. Flag only questions
disguised as decisions, contradictions, or unknowns whose blocking effect is
hidden.

A clear statement such as “Archive compression remains open and blocks
selection of the streaming writer” is useful. Do not require an owner or date
unless project context makes that workflow information material.

## Preserve Security and Integrity Prohibitions

Negative language is not itself slop. Keep concise prohibitions that constrain
authority, mutation, replay, disclosure, compatibility, or safety.

Useful:

> The Archive Writer MUST NOT alter item paths or checksums from the approved
> export manifest.

This closes a credible and dangerous behavior permitted by the positive
execution model. Use the decision procedure in `normative-language.md`.

## Preserve Genuine Non-Goals

A non-goal earns attention when it blocks a plausible scope interpretation.

Useful:

> Publishing a preview does not promote it to the production origin.

Promotion is plausible in a publishing change, so the boundary is material.
Delete exclusions such as “this retry fix does not add a mobile app” when no
reasonable implementer would infer them.

## Ordinary Domain Terms Need No Glossary

Do not demand definitions for familiar terms shared by the intended readers.
Request a definition only when a central term is unfamiliar, overloaded, or
used inconsistently. A short document with obvious vocabulary needs no glossary.

## Explicit State Can Be Necessary

A state table is not over-specification when legal transitions, terminal states,
or transition owners affect behavior. Stateful asynchronous and concurrent
systems often need explicit lifecycle detail. Flag only duplicate,
contradictory, or non-material representation.

Do not require a state machine for a pure local transformation with no durable
or externally observable lifecycle.

## Protocol Detail Is Not Slop

Schema, units, null semantics, identity, validation, errors, ordering,
idempotency, delivery, authentication, authorization, versioning, and
compatibility can be essential at a boundary. Preserve the subset required for
independent implementation.

Do not duplicate an authoritative OpenAPI, Protobuf, JSON Schema, ABI, or other
contract. Link it and state only local semantics or deviations.

## External Standards Can Force Implementation Detail

An algorithm, wire representation, cryptographic primitive, header, or library
interface can be normative when an external standard or compatibility contract
requires it. Do not delete that detail as a local mechanic. Require the document
to identify the authority if the necessity is otherwise unclear.

## Similar Examples Can Cover Different Boundaries

Do not consolidate repeated-looking examples when each proves a distinct case,
such as missing versus explicit `null`, first versus duplicate delivery, or old
versus new client versions. Mark the boundary each example illustrates.

Consolidate examples that only vary decorative values and add no new meaning.

## Important Does Not Mean Separate ADR

An architecturally significant decision can remain in its canonical feature
spec when that document is durable and discoverable. A missing separate ADR is
not a finding unless all four gates in `adr-threshold.md` pass.

Routine feature work, repository-pattern continuation, and the only approach
permitted by a prior decision do not warrant ADRs.

## Diagrams Are Optional

Do not request a diagram because the system has several components. Prefer
prose when it communicates topology or flow more directly. A diagram earns its
place only when it compresses relationships, order, or state and agrees with
the authoritative text.

## Operational Sections Are Conditional

Do not ask for observability, capacity, rollout, migration, version skew,
rollback, or operator procedures when the change creates no related concern.
A local pure function or compile-time type correction can need only focused
verification.

When a design does activate an operational concern, ask for the exact missing
contract or decision. Do not replace one empty template with another.

## Whole-Document Review Does Not Mean Legacy Cleanup

Read unchanged text to understand terms and detect contradictions. In diff mode,
report only issues introduced by or materially related to the changed proposal.
Do not add unrelated historical verbosity to the report.

## Rationale Can Earn Attention

Descriptive text need not constrain compliance to be useful. Preserve rationale
that materially explains a design decision or prevents a future reader from
reopening a rejected live option under unchanged constraints. Preserve an
invariant because it constrains the system, not as generic explanation.

Delete generic justification and repeated summaries, not every non-normative
sentence.

## A Plausible Repair Is Not an Established Repair

Do not select one reasonable answer merely because it would make the document
coherent. When two material repairs fit the available evidence, report the
decision with **Resolve** or **Reconcile**. Supply replacement text only after an
authoritative source selects the answer.

## Do Not Invent Precision

A vague material target is a missing decision, not permission to choose a
number. Ask for the retry budget, percentile, load, retention period,
consistency model, or compatibility window. In apply mode, add a compact open
question only when useful.

## Final Finding Gate

Before reporting, confirm all six points:

1. Exact text or omission is identified.
2. A materially wrong interpretation, decision, or cognitive cost follows.
3. One directive applies.
4. One concrete repair verb fits.
5. The repair is either derivable or marked as a required decision.
6. The concern is activated by the actual design and appropriate to maturity.

If any point is uncertain, omit the finding.
