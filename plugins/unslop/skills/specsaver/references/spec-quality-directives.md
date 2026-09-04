# Specification Quality Directives

Use this reference to test and repair candidate findings. Read the matching
directive, then check `gotchas.md`. Report only concerns that can cause a
materially wrong implementation, review conclusion, or avoidable cognitive
cost.

The examples are synthetic. An `After` passage may state a decision only when
the hypothetical author or an authoritative source supplied it. If the target
does not establish that decision, use a compact required-decision question
instead of copying the example's value or behavior.

## Contents

1. [Establish the problem before the mechanism](#1-establish-the-problem-before-the-mechanism)
2. [Specify the system positively](#2-specify-the-system-positively)
3. [Bound scope only where ambiguity is plausible](#3-bound-scope-only-where-ambiguity-is-plausible)
4. [Keep statement roles distinct](#4-keep-statement-roles-distinct)
5. [Decide material behavior; leave local mechanics local](#5-decide-material-behavior-leave-local-mechanics-local)
6. [Use one concept, one term, and an explicit actor](#6-use-one-concept-one-term-and-an-explicit-actor)
7. [Write atomic, observable behavioral statements](#7-write-atomic-observable-behavioral-statements)
8. [Define state and material failure behavior](#8-define-state-and-material-failure-behavior)
9. [Quantify material quality attributes](#9-quantify-material-quality-attributes)
10. [Treat interfaces and distributed boundaries as contracts](#10-treat-interfaces-and-distributed-boundaries-as-contracts)
11. [Use normative language precisely and sparingly](#11-use-normative-language-precisely-and-sparingly)
12. [Document only live alternatives and genuine trade-offs](#12-document-only-live-alternatives-and-genuine-trade-offs)
13. [Record ADRs only for architectural forks](#13-record-adrs-only-for-architectural-forks)
14. [Maximize information density; make every sentence and section earn attention](#14-maximize-information-density-make-every-sentence-and-section-earn-attention)
15. [Use supporting representations only to compress complexity](#15-use-supporting-representations-only-to-compress-complexity)
16. [Connect verification and safe evolution to the design](#16-connect-verification-and-safe-evolution-to-the-design)
17. [Maintain one coherent authoritative model](#17-maintain-one-coherent-authoritative-model)

## 1. Establish the problem before the mechanism

**Principle.** Give the reader the current problem, affected actor, and desired
observable outcome before asking them to judge services, tables, queues, or
algorithms.

**Why it matters.** A mechanism has no useful evaluation criteria without a
need. Reviewers cannot tell whether complexity is necessary, and implementers
cannot resolve small gaps consistently with the intended result.

**Red flags.** The document opens with components or libraries; the affected
workflow is absent; success is described only as “implement the new service”;
or a long business case obscures the engineering problem.

**Reviewer test.** In two sentences, identify who experiences what current
failure and what observable state should replace it. If the document does not
support that answer, the problem is underspecified. If it does, do not demand a
separate `Goals` heading.

**Repair patterns.** Add one short problem paragraph derived from established
material. Connect each major mechanism to that problem. Delete mechanisms that
serve no stated outcome. Use **Resolve** when the intended outcome is unknown,
not **Add** with a guessed purpose.

**Before.**

> Add a queue worker, a retry set, and a status endpoint.

**After.**

> Editors currently restart failed media transcodes by hand and can create
> duplicate outputs. A durable worker will retry each source revision under the
> same job identifier and expose its terminal result to editors.

**False-positive boundary.** A ticket-sized change can establish the problem
in one sentence or through clear linked context. Do not require ceremonial
motivation when the reader can already judge the design.

## 2. Specify the system positively

**Principle.** Construct the intended system directly in the reader's mind by
stating what it is, owns, and does. Use a prohibition only when the prohibition
is itself a security, safety, compatibility, data, or scope invariant.

**Why it matters.** A list of exclusions makes the reader retain many negative
facts while still inferring the actual model. A positive responsibility gives
one coherent concept. Precise negative requirements remain essential when a
positive statement permits a dangerous interpretation.

**Red flags.** Clusters of “does not,” “is not,” or “will not”; exhaustive
non-goal lists; a component defined only by responsibilities it lacks; or a
word-level rule that treats every `MUST NOT` as slop.

**Reviewer test.** Ask:

1. Is the prohibition itself an invariant?
2. Does it close a plausible interpretation of the positive model?
3. Could a compliant implementation otherwise exhibit the forbidden behavior?
4. Is this the shortest clear form?

Retain or tighten the prohibition if any of the first three answers is yes. If
all are no, rewrite positively or delete it.

**Repair patterns.** Consolidate exclusions into one positive responsibility.
Retain the shortest material prohibition. Delete fanciful exclusions. Load
`normative-language.md` for the full procedure.

**Before.**

> The Archive Writer does not select records, delete source files, choose
> retention policy, rewrite manifests, or own export status.

**After.**

> The Archive Writer copies approved export batches from the catalog to archive
> storage and records each result. It MUST NOT alter the batch's item paths or
> checksums.

**False-positive boundary.** Never flag a useful security or integrity
prohibition merely because it is negative. The target is negative-definition
slop, not the word `not`.

## 3. Bound scope only where ambiguity is plausible

**Principle.** State goals, boundaries, and non-goals only when they distinguish
credible interpretations or block tempting expansion.

**Why it matters.** Useful scope boundaries prevent two reasonable teams from
building different products. Fanciful exclusions and empty template headings
consume attention without reducing uncertainty.

**Red flags.** Non-goals unrelated to the proposal; a scope section that repeats
the title; a small cache change with `Security: N/A`, `Migration: N/A`, and
`Internationalisation: N/A`; or infinite lists of systems not being redesigned.

**Reviewer test.** Could a competent implementer reasonably include the
excluded behavior from the positive proposal? Would that interpretation affect
delivery or architecture? If either answer is no, the boundary probably does
not earn attention.

**Repair patterns.** Keep one precise boundary beside the relevant design
statement. Delete irrelevant exclusions and `N/A` tombstones. Add a non-goal
only when authoritative context establishes the plausible ambiguity.

**Before.**

> Non-goals: replacing the CDN, redesigning the editor, adding a mobile app,
> changing the analytics stack, and rewriting the content service.

**After.**

> Preview publishing writes to an isolated preview origin; publishing a preview
> does not promote it to the production origin.

**False-positive boundary.** Preserve a genuine non-goal, such as keeping
preview publication separate from production promotion, when replacement is a
credible reading.

## 4. Keep statement roles distinct

**Principle.** Make facts, requirements, decisions, rationale, assumptions,
examples, tasks, and unknowns carry their correct authority.

**Why it matters.** An example mistaken for a contract constrains clients by
accident. An assumption presented as fact hides risk. Rationale written as a
requirement makes the reason difficult to revise without appearing to change
behavior.

**Red flags.** Required fields appear only in sample JSON; “use PostgreSQL
because…” combines decision and contract; a TODO hides a material unknown;
preferences pose as constraints; or task lists substitute for system behavior.

**Reviewer test.** For each material sentence, ask what a compliant
implementation must do if the sentence is normative, and what authority proves
it if descriptive. If its role changes the answer but remains unclear, report
it.

**Repair patterns.** Rewrite the statement in its real role. Move established
facts to context, state requirements as observable behavior, keep rationale
adjacent to the decision, mark true assumptions, and phrase unresolved matters
as answerable questions. Add labels only when prose cannot make authority clear.

**Before.**

> Example: `{ "ingestionId": "123", "sourceRevision": "2026-09" }`. We use a
> UUID so retries work. TODO source handling.

**After.**

> Each import requires an ingestion identifier and source revision. Retries
> reuse the ingestion identifier. UUIDs are the current representation, not
> part of the external contract. Open question: which public feeds may clients
> import, and where is that allow-list authoritative?

**False-positive boundary.** Do not demand visual labels for every sentence.
Normal prose can distinguish context and requirements when the language is
clear.

## 5. Decide material behavior; leave local mechanics local

**Principle.** The author owns material product and architectural choices. The
implementer owns replaceable local mechanics.

**Why it matters.** Leaving trust boundaries, source of truth, externally
observable state, consistency, compatibility, or failure behavior open makes
implementation an unreviewed design exercise. Dictating helper names or method
shape adds brittle detail without controlling the product.

**Red flags.** “The implementer may choose” among behaviorally different retry
or consistency models; unclear authority or persistence; exact filenames,
private helpers, loops, or minor libraries specified without a contract reason.

**Reviewer test.** Could two competent implementations comply while differing
meaningfully in external behavior, security, architecture, interoperability,
persistence, operability, cost, or reversibility? If yes, resolve or explicitly
grant the freedom. If no material consequence exists, leave the choice local.

**Repair patterns.** Resolve the material choice or state the permitted range.
Delete local prescriptions. Explain an implementation technique only when an
external standard, performance bound, safety property, or existing repository
contract forces it.

**Before.**

> Add `src/utils/retry.ts` with a `for` loop and `sleep` helper. The developer
> can choose whether a failed export job is retried forever or marked failed.

**After.**

> Required decisions: are automatic retries bounded? If yes, define the budget
> and terminal result. If no, state the externally relevant indefinite-retry
> behavior. The local retry helper structure remains an implementation choice.

**False-positive boundary.** A specification may intentionally permit multiple
implementations. Do not flag freedom when the allowed differences are explicit
and immaterial to consumers or system qualities.

## 6. Use one concept, one term, and an explicit actor

**Principle.** Give each important concept one stable term and name the actor
responsible for each action.

**Why it matters.** Synonym drift makes readers maintain a mapping that may be
wrong. Passive voice can hide ownership, authority, and failure responsibility.

**Red flags.** `request`, `job`, and `item` refer to the same record; `source`
means both an upstream feed and an ingested dataset; “it” has two possible
referents; “the status is updated” does not say by whom; or a central acronym is
undefined.

**Reviewer test.** Build a short mapping of actors and owned concepts. If one
concept has several names, one name has several meanings, or an important
effect has no responsible actor, a material ambiguity exists.

**Repair patterns.** Consolidate synonyms under the existing canonical term.
Rewrite passive obligations with the responsible actor. Define only central or
unfamiliar domain terms; do not manufacture a glossary.

**Before.**

> Once it succeeds, the request is updated and the item is indexed.

**After.**

> After the search service accepts the document, the Indexer sets the ingestion
> state to `indexed`.

**False-positive boundary.** Ordinary domain terminology does not need a
definition for its own sake. Passive descriptive prose is acceptable when actor
identity cannot affect interpretation.

## 7. Write atomic, observable behavioral statements

**Principle.** A normative statement identifies its condition or trigger,
responsible actor, and observable response. Separate independently testable
obligations.

**Why it matters.** Bundled or vague requirements hide partial compliance and
make verification subjective. Requirements should define behavior, not express
hope through verbs such as `handle` or `ensure`.

**Red flags.** Several duties joined with `and`; “handle errors gracefully”;
“support retries”; no trigger or actor; or an implementation technique with no
observable need.

**Reviewer test.** Can a test or inspection show pass or fail for one
obligation? Can one part succeed while another fails? If so, split it. Can the
reader name the trigger, actor, and response? If not, rewrite or resolve.

**Repair patterns.** Split independent obligations. Replace vague verbs with
observable results. Use EARS-style clauses only when they clarify temporal or
conditional behavior.

**Before.**

> The API must validate, save, process, and gracefully handle bad requests.

**After.**

> When a request fails schema validation, the API returns `400` with the
> invalid field path and does not create an import job. For a valid request, the
> API creates one import job before returning its identifier.

**False-positive boundary.** Do not mechanically split a short sentence whose
parts form one indivisible outcome. Do not rewrite every requirement into EARS.

## 8. Define state and material failure behavior

**Principle.** Describe the nominal flow, legal state transitions, invariants,
ownership, source of truth, and off-nominal cases activated by the design.

**Why it matters.** Stateful and asynchronous systems fail between steps.
Without terminal states and transition rules, implementations invent different
retry, cancellation, duplicate, and partial-success semantics.

**Red flags.** Happy-path-only workers; statuses without legal transitions; no
terminal failure; two writers with unclear authority; no answer for duplicates,
timeout, cancellation, partial success, dependency failure, concurrent claims,
or retry exhaustion when those cases are inherent.

**Reviewer test.** Identify the source of truth, transition owner, allowed
transitions, terminal states, invariants, and each failure created by a real
boundary. If multiple materially different behaviors remain compliant, resolve
them. Do not enumerate failures the design cannot experience.

**Repair patterns.** Add a compact state table when it compresses scattered
prose. Reconcile authority. State retry classes and terminal effects. Preserve
unknown budgets as required decisions instead of choosing values.

**Before.**

> The worker publishes pending pages and retries failures.

**After.**

> Required decisions: define how a worker obtains exclusive work, which failures
> are retryable, whether retries are bounded, any exhaustion result, and which
> states are terminal. The source text does not determine those semantics.

**False-positive boundary.** Explicit state machines are not verbose by
default. Preserve detail needed to define legal transitions. Do not demand a
failure catalogue for a local pure function.

## 9. Quantify material quality attributes

**Principle.** Define important qualities with observable operating conditions,
measurements, thresholds, and tolerances.

**Why it matters.** `Fast`, `reliable`, `scalable`, `recent`, and `available`
permit incompatible interpretations and cannot establish acceptance.

**Red flags.** Latency without percentile or load; capacity without environment;
retention without a period; “eventually” where delay matters; security stated
only as an adjective; or invented precision unsupported by product needs.

**Reviewer test.** Would materially different thresholds change architecture,
cost, or acceptance? If yes, can the reader identify the stimulus, environment,
measurement, bound, and tolerance? If the value is unavailable, report the
decision; do not choose it.

**Repair patterns.** Quantify known values and measurement conditions. Resolve
unknown material targets. Delete subjective qualities that are not actual
requirements.

**Before.**

> The endpoint must be fast and highly available under normal load.

**After.**

> Required decisions: define the relevant load, latency measurement and bound,
> and availability target. Remove either quality claim if it is not a product
> requirement.

**False-positive boundary.** Descriptive prose can use adjectives harmlessly.
Flag them when they carry requirement force or conceal a decision, not whenever
they appear.

## 10. Treat interfaces and distributed boundaries as contracts

**Principle.** At each boundary, state the semantics both sides need for
correct independent action.

**Why it matters.** Endpoint names and component arrows do not define nulls,
units, validation, identity, ordering, atomicity, errors, security, or evolution.
Those gaps create integration failures even when each component works locally.

**Red flags.** An API lists routes without schemas or errors; a queue message has
no identity or duplicate semantics; an asynchronous call has no ordering or
delivery meaning; a database handoff has unclear transaction boundaries; or a
copied schema drifts from its authority.

**Reviewer test.** Inspect activated concerns: schema, units, required and
optional fields, null semantics, validation, errors, authentication,
authorization, idempotency, ordering, delivery, deduplication identity,
atomicity, consistency, versioning, and compatibility. Report only those whose
absence allows material divergence.

**Repair patterns.** Link the authoritative external schema and state local
constraints or deviations. Add boundary semantics beside the interaction.
Resolve choices such as delivery or consistency when no source determines them.

**Before.**

> `POST /imports` creates an import job. Workers can receive it more than once.

**After.**

> Workers may receive an import job more than once. Required decisions:
> identify the authoritative request and response schemas, durable job
> identity, delivery guarantee, duplicate behavior, and retry contract.

**False-positive boundary.** Do not duplicate a normative OpenAPI, Protobuf, or
external standard. Protocol detail required for interoperability is not
implementation slop.

## 11. Use normative language precisely and sparingly

**Principle.** Use requirement force deliberately. Ordinary `must` is valid, as
is declared BCP 14 uppercase usage; consistency matters more than ceremony.

**Why it matters.** Accidental mixtures of `must`, `shall`, `will`, and `should`
make compliance unclear. `SHOULD` without a real exception and `MAY` without
real optionality disguise undecided behavior.

**Red flags.** Accidental modal synonyms; `should` for mandatory behavior;
`MAY` for an unmade product decision; requirements qualified by `generally`,
`where possible`, `as appropriate`, `gracefully`, `reasonable`, `promptly`,
`eventually`, `and/or`, or `etc.` when the qualifier changes compliance.

**Reviewer test.** Ask whether the statement is normative, what behavior it
requires, what exception permits deviation, and how compliance is observed. A
trigger word is not a finding without contextual ambiguity.

**Repair patterns.** Choose one modal convention. Rewrite obligations with
clear actors and outcomes. State the exception and consequence for `SHOULD`.
Use `MAY` only for genuine optional behavior. Quantify material qualifiers or
resolve their value.

**Before.**

> The client should retry promptly where possible and may preserve the same
> import ID.

**After.**

> Required decisions: determine whether a timed-out retry must reuse the
> original import identifier, then define the retry delay and budget. The source
> text does not make identifier reuse mandatory or optional.

**False-positive boundary.** `Normally`, `may`, or `reasonable` can be harmless
descriptive words. Do not use a blacklist. Implementation methods may be
normative when interoperability, an external standard, or safety requires them.

## 12. Document only live alternatives and genuine trade-offs

**Principle.** Include an alternative only when a reasonable engineer could
advocate it under the stated constraints.

**Why it matters.** Straw options and invented rejection narratives add process
theater. Live alternatives explain which forces drove a real decision and help
future reviewers recognize when those forces change.

**Red flags.** `Do nothing` when not viable; `rewrite everything`; a vague third
party option no one considered; rejection because it is “too complex” without
criteria; or an Alternatives heading created solely by a template.

**Reviewer test.** Name the advocate's credible case and the decision-driving
constraint that rejects it. If neither can be stated from evidence, it is not a
live alternative. Do not invent another option to replace deleted theater.

**Repair patterns.** Delete straw alternatives. Consolidate real trade-offs next
to the chosen design. State the forces and consequences concisely. Resolve an
alternative only when the document's maturity requires the choice.

**Before.**

> Alternatives: do nothing; rewrite all services; use a third party. Rejected
> because they are bad or too complex.

**After.**

> We chose a build-time search bundle over a server-side search service because
> the static site needs release-consistent results without a runtime dependency.
> A service could update between releases and reduce the client download, but
> neither benefit is required for this documentation corpus.

**False-positive boundary.** Do not require an `Alternatives` heading. One
sentence of rationale can capture the only real trade-off. Exploratory notes
may retain unresolved live alternatives.

## 13. Record ADRs only for architectural forks

**Principle.** Use an ADR for a real, architecturally significant fork whose
rationale needs durable, separately useful preservation.

**Why it matters.** Calling routine feature work an architectural decision
dilutes the decision record. Duplicating a feature spec creates two authorities
that drift.

**Red flags.** “ADR: add sitemap endpoint”; a route, table, method, test, or
repository-pattern continuation presented as a fork; an ADR recommendation
based only on importance; or a duplicate record demanded when the canonical
feature spec already preserves the rationale.

**Reviewer test.** Load `adr-threshold.md` and require all four gates: a real
fork, architectural significance, durable rationale, and value from a separate
record. “Implement versus do not implement” is not a design fork.

**Repair patterns.** Delete a gratuitous ADR or fold useful feature detail into
the feature spec. Keep durable reasoning in the canonical spec when sufficient.
Recommend a separate ADR only after showing how each gate passes.

**Before.**

> ADR: Add the sitemap route using the existing content-controller pattern.

**After.**

> The feature spec defines sitemap behavior and follows the existing content
> boundary. No architectural fork exists, so no ADR is needed.

**False-positive boundary.** Cross-service data ownership, trust boundaries,
consistency, or persistence choices can meet the threshold. Even then, do not
require duplication when the feature spec is already durable and discoverable.

## 14. Maximize information density; make every sentence and section earn attention

**Principle.** Maximize useful engineering information per unit of reader
attention. Keep nothing that does not constrain the system or materially
explain a design decision. Omit no constraint whose absence forces the
implementer to invent the design. Remove cognitive overhead that adds no design
information.

**Why it matters.** Every sentence adds a proposition that the reader must
retain, classify, and reconcile. Brevity is not inherently good, and detail is
not inherently bad. A long state table can be dense because every row fixes
behavior; a short generic risk section can impose cognitive load without adding
design information.

**Red flags.** Repeated rationale; tautologies; generic risk prose; empty
headings; `Not applicable` tombstones; process narration; tutorial material;
obvious framework conventions or private helper-call sequences; recommendation
sections that repeat findings; or long summaries that duplicate the body.

**Reviewer test.** If removing a sentence would not allow a reasonable
implementer to form a materially different interpretation of the system, remove
it unless it materially explains a design decision whose rationale would
otherwise be lost. Identify the unique constraint or material decision rationale
supplied by each passage. If neither exists, delete or consolidate it.

**Repair patterns.** Delete empty, generic, or tutorial sections. Consolidate
repeated constraints into one canonical statement. Move one necessary
explanation beside the decision it supports. Replace scattered lifecycle prose
with a compact state table when that reduces working memory.

**Before.**

> The diagnostic timestamp is UTC RFC 3339 with millisecond precision.
> Security: N/A. Observability: N/A. Migration: N/A. Rollback: The change can be
> rolled back if needed. Risks: All changes carry implementation risk.

**After.**

> The diagnostic timestamp is UTC RFC 3339 with millisecond precision.

**False-positive boundary.** Do not reward shortness or punish detail. Problem
context, explicit state, protocol semantics, behavior-specific verification,
and a representation that replaces more costly prose can all have high
information density. Descriptive rationale earns attention only when it
materially explains a design decision whose reasoning would otherwise be lost.

## 15. Use supporting representations only to compress complexity

**Principle.** Use an example, table, or diagram only when it makes structure,
behavior, or edge cases clearer than prose.

**Why it matters.** A good state table or sequence view reduces working memory.
A decorative diagram adds another model to reconcile and can silently conflict
with normative prose.

**Red flags.** Unlabeled arrows; mixed abstraction levels; Mermaid added because
it is available; examples that introduce required fields absent from the
contract; repeated examples with no distinct boundary case; or a table that
fragments a simple narrative.

**Reviewer test.** Remove the representation mentally. Is the design harder to
understand? Does each element map to the authoritative prose, and do examples
obey it? If not, delete, simplify, or reconcile it.

**Repair patterns.** Replace scattered lifecycle prose with a small state table.
Label actors and semantics in a sequence diagram. Mark illustrative values as
examples. Delete decorative artifacts. Reconcile contradictions with the
normative source.

**Before.**

> A Mermaid graph shows `Upload API --> Queue --> Transcoder --> Object
> storage`, while prose says the database is the durable handoff and no queue
> exists.

**After.**

> A four-row state table identifies the database states, transition actor, and
> terminal outcomes. No topology diagram is necessary.

**False-positive boundary.** Do not demand a diagram when prose is clearer.
Repeated data examples can each earn their place by showing a different
boundary case.

## 16. Connect verification and safe evolution to the design

**Principle.** State how material behavior will be demonstrated and how an
activated delivery or compatibility risk will be controlled.

**Why it matters.** “Add tests” does not show that contracts or invariants are
verifiable. “Rollback if needed” is false for irreversible data mutation or
incompatible clients.

**Red flags.** Generic unit/integration test tasks; breaking schema changes with
no compatibility path; irreversible migration with a rollback claim; no abort
condition; or an operationally important path with no observable success or
terminal failure.

**Reviewer test.** Map each material behavior and invariant to evidence. Then
inspect only evolution concerns activated by the design: compatibility, data
transition, backfill, version skew, rollout phase, gating, abort, reversal
limits, observability, capacity, and operator action.

**Repair patterns.** Add behavior-specific acceptance evidence. State
preconditions, abort conditions, and completion proof. Reconcile rollback claims
with irreversible steps. Resolve an unknown compatibility or rollout decision;
do not invent it.

**Before.**

> Add unit and integration tests. Roll back the column migration if needed.

**After.**

> Required decisions: define the supported version-skew window, the first
> irreversible step, and the evidence that permits advance, abort, and
> completion. Do not claim rollback until those constraints are known.

**False-positive boundary.** A local pure function may need only one focused
test. Do not require rollout, observability, migration, or rollback sections
when the change creates no such concern.

## 17. Maintain one coherent authoritative model

**Principle.** Keep values, terms, state transitions, ownership, examples, and
authoritative references consistent.

**Why it matters.** Contradictory retry counts, two sources of truth, or stale
decisions make compliance unknowable. Readers should not choose which paragraph
to trust.

**Red flags.** Different retry budgets in two sections; schema copies that
drift; an example violating normative text; two owners for one transition;
superseded choices presented as current; or naked `TBD` values in an approved,
implementation-ready document.

**Reviewer test.** Trace each material term, value, transition, and authority
through the document and linked canonical sources. Can all statements be true
at once? Does the maturity permit remaining unknowns? If not, reconcile or
resolve.

**Repair patterns.** Establish one canonical statement and link to it. Delete
stale copies. Reconcile examples and diagrams. In exploratory documents, keep
real open questions and state whether they block the next decision. In
implementation-ready documents, resolve material `TBD` items without guessing.

**Before.**

> Section 3 allows three retries. The state table says five. The example creates
> a second import ID for the fourth attempt.

**After.**

> Required decisions: select one retry budget and determine whether attempts
> reuse the import identifier. Then reconcile every section and example with
> those canonical decisions.

**False-positive boundary.** Managed open questions are correct in exploratory
documents. Add owners or dates only when the project context makes them useful;
do not manufacture workflow ceremony.
