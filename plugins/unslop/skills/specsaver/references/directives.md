# Specsavers Directives

The reasoning and examples behind the ten directives in `SKILL.md`. Use them
to sharpen a judgement, not to classify one. The examples are synthetic. An
`After` passage states a decision only because the hypothetical author supplied
it; when a real target does not establish that decision, write the question
instead of copying the example's value.

## 1. Write for the human reader

**Principle.** A specification transfers a design from one engineer's head into
another's. Optimise for the reader's comprehension and retention, not for the
author's order of discovery.

**Why it matters.** Every sentence is a proposition the reader must classify,
retain, and reconcile. Scattered facts, buried invariants, and prose that runs
against execution order force the reader to rebuild the model themselves. A
design can be correct and still fail because it is hard to hold in one's head.

**What to look for.** A rule stated far from the behaviour it governs. Steps
described out of order. One paragraph that mixes trigger, action, failure, and
telemetry. Verification written as a wall of prose. A fact the reader must
already know before the sentence that introduces it. Circular explanation that
restates a term instead of defining it.

**Before.**

> The metric is incremented after commit, by the committed count. Deletion of
> rendered output, build logs, and previews happens in one transaction per
> batch, and batches are at most 500, and the set that is drained is the one
> selected at the start of the run, not previews that became eligible later
> (those wait). Ordering of the drain is by `(expired_at, preview_id)`.

**After.**

> The worker drains the start-of-run set in batches of at most 500 previews,
> ordered by `(expired_at, preview_id)`. For each batch, one transaction
> deletes the rendered-output rows, build-log rows, and preview rows. After
> commit, the worker adds the committed preview count to
> `preview_cleanup_deleted_total`. Previews that become eligible after
> `run_started_at` wait for the next run.

Nothing was removed. The facts now appear in the order the worker performs
them, and the exception sits after the rule it modifies.

**Boundary.** Do not rewrite prose that is already clear, and do not impose a
house style. Readability is a property of the reader's effort, not of sentence
length or heading count.

## 2. Preserve semantics, not prose

**Principle.** The material content of a specification is its constraints,
decisions, and the rationale that would otherwise be lost. Its wording,
paragraph structure, and section order are means to convey that content and
may be replaced freely.

**Why it matters.** A reviewer who treats every semantically loaded sentence as
protected will leave a badly written document badly written. A reviewer who
treats wording as disposable but meaning as sacred can rewrite freely and
safely.

**What to look for.** Before rewriting a passage, list the facts it carries.
After rewriting, check that each fact survives. A rewrite that drops a fact is
a defect. A rewrite that keeps every fact and reads better is the job.

**Boundary.** Preserve deliberate precision. A `MUST NOT` with a specific
object, a named state, an exact value, or a defined order of operations is
semantics. Rephrase around it; do not soften it.

## 3. Describe the system positively

**Principle.** State what a component is, owns, and does before stating what it
does not do. Keep a prohibition only when it is itself an integrity, security,
compatibility, or scope invariant that the positive model does not already
close.

**Why it matters.** A list of exclusions forces the reader to hold many negative
facts and still infer the actual responsibility. One positive statement of
actor, input, action, and effect gives them the model directly. Precise
prohibitions remain essential when the positive statement would otherwise
permit a dangerous or plausible wrong behaviour.

**Deciding whether a prohibition earns its place.** Ask:

1. Is the prohibition itself an invariant?
2. Does it close a plausible interpretation of the positive model?
3. Could a compliant implementation otherwise exhibit the forbidden behaviour?

Keep or tighten it when any answer is yes. Otherwise rewrite positively or
delete it.

**Before.**

> The Archive Writer does not select records. It does not delete source files.
> It does not choose retention policy. It is not authoritative for export
> status. It does not rewrite manifests.

**After.**

> The Archive Writer copies approved export batches from the catalogue to
> archive storage and records each result. It MUST NOT alter an item's path or
> checksum from the committed manifest.

The five exclusions collapse into one responsibility. The one prohibition that
protects manifest integrity stays, because the positive sentence alone would
permit a writer that "helpfully" renames entries.

**Boundary.** Negative language is not slop. The target is a component defined
through what it is not, not the word `not`.

## 4. Remove non-information

**Principle.** Delete text that constrains nothing, explains no decision, and
resolves no plausible ambiguity.

**Why it matters.** Ceremony hides the design. A reader who has just skipped
four `N/A` headings and a generic risk paragraph is less alert when the one
material sentence arrives.

**What to look for.** Empty or `Not applicable` headings. Non-goals that no
reasonable implementer would have inferred. Alternatives that no engineer would
advocate: `do nothing`, `rewrite everything`, `use some third party`. Generic
caveats: `appropriate care will be taken`. Restated summaries. Narration of
private handler calls that the contract does not fix. Rationale repeated in
three places.

**Before.**

> ## Security
>
> Not applicable.
>
> ## Non-goals
>
> This change does not replace PostgreSQL, add GraphQL, or create an admin
> console.
>
> ## Risks
>
> All software changes have risk. Appropriate care and sufficient testing will
> be used to manage it.

**After.**

Nothing. The three sections are deleted. The remaining design is unchanged.

**Boundary.** A non-goal earns its place when it blocks a plausible reading:
"publishing a preview does not promote it to production" is material in a
publishing change. Rationale earns its place when it stops a future reader
from reopening a rejected live option. Do not replace deleted ceremony with a
paragraph explaining why the ceremony was absent.

## 5. Decide material behaviour

**Principle.** The author owns product, architectural, state, ownership,
failure, and compatibility decisions. The implementer owns replaceable local
mechanics.

**Why it matters.** When a specification leaves the retry model, the source of
truth, or the terminal failure state open, implementation becomes an unreviewed
design exercise, and two compliant implementations can behave materially
differently. When a specification dictates helper names and loop structure, it
adds brittle detail that controls nothing the product cares about.

**Test.** Could two competent implementations both comply while differing in
externally observable behaviour, security, persistence, interoperability,
operability, or reversibility? If yes, the decision is material and belongs to
the author. If the only differences are internal, leave the choice local.

**Common material gaps in stateful or asynchronous designs.** Work identity and
whether it binds a stable input snapshot when the referenced data can change.
Delivery semantics and duplicate handling. Who may claim work and how exclusion
is achieved. Which failures are retryable, whether retries are bounded, and
what exhaustion produces. Terminal states and who owns each transition.
Cancellation cut-off. Consistency between two writers.

**Before.**

> Add `src/utils/retry.ts` with a `for` loop and a `sleep` helper. The
> developer can decide whether a failed export is retried forever or marked
> failed.

**After.**

> Open question: are automatic export retries bounded? If so, what is the
> budget and what terminal result does exhaustion produce? The retry helper's
> internal structure is an implementation choice.

**Boundary.** A specification may deliberately permit several implementations.
Do not flag explicit, immaterial freedom. Do not demand a failure catalogue for
a pure local function.

## 6. Make behaviour precise

**Principle.** Use one stable term per concept, name the actor responsible for
each effect, state observable outcomes, define legal state transitions, and
give material quality attributes a measurable form.

**Why it matters.** Synonym drift makes the reader maintain a mapping that may
be wrong. Passive voice can hide who owns a transition. `Handle gracefully`
and `fast` cannot be tested, so they cannot be implemented consistently.

**Terms and actors.** If `request`, `job`, and `item` are one record, use the
repository's canonical term. If `source` means both an upstream feed and an
ingested dataset, give each a name. Rewrite "the status is updated" as "the
Indexer sets the state to `indexed`" when responsibility matters.

**Observable behaviour.** A useful behavioural statement names its trigger when
one is relevant, its actor, and one observable response. Split obligations that
can pass or fail independently. `Handle`, `support`, `manage`, and `ensure`
are fine when the surrounding text makes the result observable; flag them only
when it does not.

**Normative force.** Ordinary `must` is valid. Declared BCP 14 uppercase is
valid. Consistency matters more than convention. Use `should` only when a real
exception exists and the reader can understand its consequences. Use `may`
only for genuinely optional behaviour. A `should` on an integrity invariant is
a defect; make it `must`.

**Qualifiers.** `Generally`, `where possible`, `as appropriate`, `promptly`,
`eventually`, `sufficient`, and `gracefully` are not banned. Flag them when
they carry requirement force and leave compliance undefined. Leave them alone
in descriptive context.

**Quality attributes.** When a quality claim would change architecture, cost,
or acceptance under different thresholds, it needs an operating condition, a
measurement, and a bound. If the value is unknown, ask for it. Never choose it.
Delete adjectives that are not actually requirements.

**Before.**

> The API must validate, save, process, and gracefully handle bad requests. It
> should be fast under normal load.

**After.**

> When a request fails schema validation, the API returns `400` with the
> invalid field path and creates no import job. For a valid request, the API
> stores one import job before returning its identifier.
>
> Open question: is response latency a requirement? If so, under what load,
> measured how, with what bound?

**Boundary.** Do not run a word blacklist. Do not demand a glossary for
ordinary domain terms. Do not rewrite every sentence into a template such as
EARS; use such forms only where they clarify timing or condition.

## 7. Treat boundaries as contracts

**Principle.** At each boundary the design creates, state the semantics both
sides need to act correctly and independently.

**Why it matters.** Route names and component arrows do not define nulls,
units, validation, identity, ordering, atomicity, errors, authority, or
evolution. Those gaps produce integration failures even when each component is
locally correct.

**What to inspect, only where the design activates it.** Schema authority and
where it lives. Required, optional, and null semantics. Validation and error
shape. Authentication and authorisation. Identity and idempotency. Delivery,
ordering, and duplicate handling. Transaction and atomicity boundaries.
Versioning and the compatibility window.

**Before.**

> `POST /imports` creates an import job. Workers can receive it more than once.

**After.**

> Workers may receive an import job more than once. Open questions: which
> schema is authoritative for the request and response; what durable identity
> a job carries; how a worker recognises and discards a duplicate delivery;
> and whether a retry reuses the original identity.

**Boundary.** Do not copy an authoritative OpenAPI, Protobuf, JSON Schema, or
ABI into the document. Link it and state local semantics or deviations.
Protocol detail required for independent implementation is not slop, however
long it runs.

## 8. Use real rationale only

**Principle.** Record an alternative only when a reasonable engineer could
advocate it under the stated constraints. Recommend a separate ADR only for a
genuine architectural fork with durable, non-obvious reasoning that the
canonical specification does not already preserve.

**Why it matters.** Straw alternatives are process theatre; they teach the
reader nothing about the forces that drove the decision. A gratuitous ADR
dilutes the decision log and creates a second authority that drifts from the
feature specification.

**Live alternatives.** For each option, can you state the advocate's credible
case and the constraint that defeats it? If not, delete it. Do not invent a
replacement option to fill the gap. One sentence of rationale beside the chosen
design is often the whole trade-off.

**ADR threshold.** All four must hold:

1. A real fork exists between at least two credible approaches. "Implement"
   versus "do not implement" is not a fork when the feature is required.
2. The choice is architecturally significant: it changes structure, quality
   attributes, dependencies, interfaces, trust or data boundaries, or the cost
   of reversal.
3. The rationale has durable value that future engineers cannot infer from the
   code.
4. A separate record adds discoverability or longevity beyond the canonical
   specification. If the feature specification is itself durable and
   indexed, keep the decision there.

Stop at the first failed gate. Do not manufacture significance to continue.

**Before.**

> Alternatives: do nothing; rewrite all services; use a third party. Rejected
> because they are bad or too complex.

**After.**

> We chose a build-time search bundle over a server-side search service. The
> service would allow updates between releases and a smaller client download,
> but it adds a stateful deployment and a runtime dependency that the
> release-level freshness requirement does not justify.

**Boundary.** Cross-service data ownership, trust boundaries, consistency
models, and persistence choices often meet gates 1 to 3. They still do not
need a separate ADR when the canonical specification is the durable home.
Exploratory documents may keep unresolved live alternatives.

## 9. Do not invent

**Principle.** When the source does not determine a material answer, state the
question. A plausible answer is not an established one.

**Why it matters.** A reviewer who fills gaps with reasonable defaults produces
a document that looks complete and is wrong in ways no one will check. The
author's intent is the only authority.

**What this looks like in practice.** A vague retry rule becomes an open
question about the budget, not a chosen number. Two contradictory values with
no authority become a request for the author to pick one, not a silent
selection. A missing state name is asked for, not coined. In a rewrite, the
question goes into the document as a concise open question where the decision
belongs.

**Boundary.** Inference from the document itself is not invention. If a
document declares its state table authoritative and one paragraph uses a stale
state name, reconciling the paragraph to the table is derivation, not a guess.
If a document defines retryable and non-retryable error classes and a fixed
delay, rewriting "retries where appropriate" in terms of those classes is
derivation. The line is whether the source determines the answer.

## 10. Check the finished document as a whole

**Principle.** After reviewing or rewriting, read the result once more as one
coherent document. Values, terms, ownership, state transitions, examples,
diagrams, and verification must agree with the design and with each other.

**Why it matters.** Piecewise edits introduce new inconsistencies. A rewritten
paragraph may now use a term the state table does not. A deleted section may
have been the only place a value was defined.

**What to look for.** The same quantity with two values. A state used in prose
but absent from the table. An example that violates normative text. A diagram
that shows a component the design removed. Verification that tests behaviour
the document no longer specifies, or fails to test behaviour it does. `TBD`
markers in a document that claims implementation readiness.

**Boundary.** Managed open questions are correct in exploratory documents.
Only an approved or implementation-ready document is defective for leaving
material behaviour open.

## Optional Lenses: Document Profiles and Maturity

These are mental models for deciding which concerns a document activates. They
are not headings, templates, or a required classification step.

**Profiles** by primary question:

- *Design or feature specification:* what system will be built, and why this
  design? Inspect problem, positive model, responsibilities, activated
  contracts and state, real trade-offs, verification.
- *Requirements:* what observable behaviour must hold? Inspect actors,
  triggers, responses, invariants, measurable qualities, verifiability.
- *API or protocol:* what exact contract permits independent implementation?
  Inspect schema authority, null semantics, errors, identity, ordering,
  delivery, versioning, compatibility.
- *Migration or rollout:* how does the system move safely between states?
  Inspect preconditions, compatibility window, first irreversible step, abort
  criteria, completion proof.
- *ADR:* which architectural fork was chosen, and why? Apply the four gates.
- *Composite:* one coherent model that borrows from several of the above.

**Maturity** from explicit status, then language and context:

- *Exploratory:* open questions and live alternatives are expected. Flag only
  assumptions dressed as facts, hidden blockers, and contradictions.
- *Decision-ready:* the problem, constraints, and options let an owner choose.
  Flag missing decision criteria and straw alternatives.
- *Implementation-ready:* no material choice remains for the implementer. Flag
  `TBD` values and deferred material behaviour. Do not over-specify local
  mechanics.
- *As-built:* claims about deployed behaviour must agree with the code. Inspect
  code only to verify the document's material claims.

A document can be exploratory in one bounded area and implementation-ready in
another. Say so only when it changes a finding.
