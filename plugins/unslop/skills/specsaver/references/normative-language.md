# Normative Language and Positive Specification

Use this reference for negative prose, actor ambiguity, unstable terminology,
atomic requirements, requirement force, vague qualifiers, and subjective
qualities. Review meaning in context; do not run a word blacklist.

## Describe the Positive Model First

State the component's responsibility, owned state, inputs, actions, and outputs
as one coherent model. Use exclusions after that model only when they close a
plausible and consequential interpretation.

Weak:

> The Archive Writer does not select records. It does not delete source files.
> It does not choose retention policy. It is not authoritative for export
> status.

Precise:

> The Archive Writer copies approved export batches from the catalog to archive
> storage and records each result.

The second form reduces the facts a reader must retain and establishes actor,
input, action, and effect.

## Decide Whether a Prohibition Earns Its Place

For each material negative statement, ask:

1. Is the prohibition itself a security, safety, compatibility, or data
   invariant?
2. Does it close a plausible interpretation of the positive design?
3. Could an implementation otherwise satisfy the positive requirements while
   exhibiting the forbidden behavior?
4. Is the sentence the shortest clear way to state the constraint?

Retain or tighten the prohibition when any of the first three answers is yes.
If all three are no, rewrite positively or delete it.

Delete or rewrite:

> This retry change does not redesign the catalog service, replace object
> storage, introduce video streaming, or create a mobile application.

Those outcomes are not credible interpretations of a narrow retry change.

Retain:

> Retrying an export MUST reuse the original export identifier and MUST NOT
> create a second archive batch.

The negative clause defines duplicate and batch-identity semantics that the
positive retry requirement does not close.

## Name the Actor and Stabilize Terms

Prefer an active actor when responsibility, authority, or ordering matters.

Ambiguous:

> The record is updated after it succeeds.

Precise:

> After object storage confirms multipart completion, the Archive Writer sets
> the export state to `complete`.

Use one term for one concept. If `request`, `job`, and `export` mean the same
durable record, select the repository's canonical term. If `source` means both
an upstream feed and an ingested dataset, give each a distinct term. Define an
acronym only when it is central and not obvious to the expected reader.

Do not reject passive voice as grammar style. Report it only when it hides a
material actor or source of truth.

## Make Requirements Atomic and Observable

A useful behavioral statement contains:

- a condition, event, or trigger when one is relevant;
- the responsible actor;
- one observable response or one indivisible outcome; and
- enough precision to verify compliance.

Split obligations that can pass or fail independently.

Weak:

> The API must validate requests, store them, submit them, and handle failures
> gracefully.

Precise:

> When request validation fails, the API returns `400` with the invalid field
> path and creates no import job.
>
> For a valid request, the API stores one import job before returning its
> identifier.

`Handle`, `support`, `manage`, and `ensure` are useful only when the surrounding
text makes the result observable. Do not flag the verb alone.

## Use EARS Only When It Clarifies Timing

EARS-style clauses are optional tools, not a required house style:

- **Ubiquitous:** “The worker records every terminal publication result.”
- **Event-driven:** “When object storage confirms an upload, the worker marks
  the page `published`.”
- **State-driven:** “While an asset is claimed, no second worker may transform
  it.”
- **Unwanted behavior:** “If the renderer rejects invalid source markup, the
  worker records a permanent failure.”
- **Optional feature:** “Where preview publishing is enabled, the publisher
  writes output to the preview prefix.”

Use ordinary prose when it is clearer. Never rewrite every bullet mechanically
to fit a pattern.

## Choose One Normative Convention

A document can use ordinary lowercase `must`, or declare that uppercase
`MUST`, `SHOULD`, and `MAY` carry BCP 14 meanings. It does not need uppercase
keywords to be normative.

Within one contract:

- Do not use `must`, `shall`, `will`, and `should` as accidental synonyms.
- Use `must` or `MUST` for a mandatory behavior.
- Use `SHOULD` or `should` only when a real exception exists and readers can
  understand the consequences of taking it.
- Use `MAY` or `may` only for genuinely optional behavior whose presence or
  absence remains compliant.
- Do not give requirement force to a helper, filename, library, or algorithm
  unless behavior, interoperability, an external standard, or safety requires
  it.

Weak `should`:

> The worker should not alter the source checksum.

This is an integrity invariant, not advice.

Precise:

> The worker MUST NOT alter the source checksum.

Legitimate `SHOULD`:

> A client SHOULD retain the export identifier for support queries. A client
> that discards it can still query by output URL after completion, but cannot
> identify a pending export.

The exception and consequence are understandable.

Legitimate `MAY`:

> A client MAY attach a display label. The service does not use the label for
> identity, deduplication, or ordering.

Optionality is real and bounded.

## Inspect Qualifiers in Context

Review these terms when they carry requirement force:

`generally`, `normally`, `typically`, `ideally`, `where possible`, `as
appropriate`, `if necessary`, `when feasible`, `reasonable`, `adequate`,
`sufficient`, `gracefully`, `and/or`, `etc.`, `including but not limited to`,
`promptly`, and `eventually`.

They are not globally banned.

Material ambiguity:

> The worker must eventually mark failed imports and retain sufficient
> diagnostic data.

The timing and data are part of acceptance but remain undefined. Quantify known
bounds or report the required decisions.

Harmless description:

> Editors normally investigate terminal failures through the existing
> publishing console.

If this sentence provides context and does not constrain compliance, `normally`
does not create a finding.

Material subjective quality:

> The service must be fast, scalable, highly available, and handle failures
> gracefully.

Ask which qualities are real requirements, then define their environment,
stimulus, measurement, threshold, and tolerance. Delete adjectives that are not
requirements. Never invent the target values.

Harmless adjective:

> The local cache keeps recent schema metadata to reduce repeated parsing.

If `recent` is explanatory and cache freshness cannot affect correctness, no
numerical bound is required.

## Reviewer Boundary

Report only when wording permits a materially different interpretation, hides
authority, or makes an activated requirement unverifiable. Do not report
grammar, punctuation, capitalization, or style trivia. Preserve useful
prohibitions, necessary protocol detail, and clear ordinary language.
