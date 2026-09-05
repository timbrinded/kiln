# Gotchas and Worked Examples

Counterweights for the directives, then complete examples of good judgement.
Read the relevant part when a call is uncertain. When it is uncertain whether a
passage carries material information, default to leaving it in. That default
does not apply to a readability rewrite that keeps every fact; there the check
is that each fact survives, not whether to rewrite at all.

## Gotchas

### Technical completeness does not settle readability

A specification can answer every material question and still force readers to
assemble the explanation from scattered sections. The technical reviewer can
correctly find no contract gap while the readability reviewer correctly
recommends a new outline. Adjudicate each against its evidence; do not let one
verdict cancel the other. Conversely, changing headings alone does not prove
that a rewrite improved understanding.

### Repeating a term can help the reader

"The worker creates a delivery. This delivery retains its original payload
across attempts" uses repetition to connect a new rule to its subject. Do not
delete that connection merely because "delivery" appears twice. Remove repeated
assertions that add nothing; preserve precise terms that maintain continuity.

### A fluent connection can invent a decision

"The client retries. The server stores request identifiers" does not establish
deduplication. Rewriting it as "The server stores request identifiers so client
retries cannot create duplicates" introduces a guarantee. Preserve the two
facts and ask about duplicate handling when it is material. Do not select a
mechanism to make the explanation flow.

### Long is not automatically bad

A state table with twelve rows can be dense because every row fixes behaviour.
A protocol section can run three pages and contain nothing removable. Judge
information per unit of reader attention, not word count. Preserve necessary
state, concurrency, protocol, and verification detail in full. Improve how it
reads; do not shorten what it says.

### Short is not automatically good

A small change may need only a problem paragraph, the behavioural contract, and
focused verification. That is complete, not thin. Do not add headings to make
it look thorough. But a short document that leaves the retry model, terminal
state, or source of truth open is incomplete however tidy it looks.

### A good document deserves a short review

The natural output for a complete, well-written specification is a sentence or
two saying so, perhaps with one or two minor notes. A long review of a good
document is a failure of proportion, not a sign of rigour. Distributed and
asynchronous designs always admit further edge cases; before raising one, apply
the completion test in the SKILL.md boundaries. Reserve "blocking" for gaps
where two compliant implementations would differ in that way, and do not
escalate a minor ambiguity to make the review look thorough.

### Rewrite the scope that was asked for

When the user names a section, a concern, or a set of findings, change nothing
outside it. Report defects seen outside that scope, and any inconsistency the
rewrite creates with unchanged sections, in the closing note.

### Preserve meaningful prohibitions

Negative language is not slop. Keep concise prohibitions that constrain
authority, mutation, replay, disclosure, compatibility, or safety, especially
when the positive model would otherwise permit the behaviour. "This retry fix
does not add a mobile app" goes; "MUST NOT reorder manifest entries" stays.

### Do not invent precision

A vague material target is a missing decision, not permission to choose a
number. In a rewrite, place the question in the document where the value
belongs. Never write a plausible default into the specification.

### Do not add inactive sections

Security, migration, observability, rollback, capacity, and internationalisation
are conditional. When a design does activate one, ask for the exact missing
contract or decision; do not replace one empty template with another, and do
not explain why a section is absent.

### Do not create gratuitous ADRs

Importance is not a fork, and following a repository pattern is not
architecture. When the canonical feature specification is durable and
discoverable, a significant decision can live there. Recommend an ADR only when
all four gates in directive 8 hold; create one only when the user asks.

### Exploratory questions are valid

A clear "this choice blocks implementation" in an exploratory note is good, not
a defect. Do not demand owners or dates unless the repository's workflow makes
them material.

### Similar examples can cover different boundaries

Two examples that look alike may prove distinct cases: missing versus explicit
`null`, first versus duplicate delivery, old versus new client. Keep both and
name the boundary each shows. Consolidate examples that differ only in
decorative values.

### External standards can force implementation detail

An algorithm, wire format, cryptographic primitive, or header can be normative
when an external standard or compatibility contract requires it. Do not delete
it as a local mechanic. Ask the document to name the authority if the necessity
is unclear.

### Diagrams and tables are optional

Do not request a diagram because a system has several components. A diagram or
table earns its place when it compresses relationships, order, or state more
clearly than prose and agrees with the normative text. Prose is often clearer.

### Whole-document reading, changed-proposal reporting

When the request is to review a change, read the whole document to understand
terms and detect contradictions, but report only issues introduced by or
materially related to the changed proposal. Unrelated legacy verbosity is not
part of that review unless the user asks for it.

## Worked Examples

### 1. Rewrite a necessary but badly written passage

**Source.**

> ## Notes on deletion
>
> It should be noted that deletion is performed in batches. The batch size is
> 500. Each batch is processed in a single transaction, which deletes the
> rendered output rows and also the build log rows and also the preview rows.
> The metric `preview_cleanup_deleted_total` is incremented. It is incremented
> after the transaction commits. It is incremented by the number of previews in
> the batch that committed. Batches are ordered by `expired_at` and then by
> `preview_id`. It is important to note that the metric is telemetry only and
> that whether deletion happened is determined by the database and not by the
> metric. Previews that became eligible after the run started are not part of
> the set drained by this run and will instead be part of a later run. The set
> drained is the start-of-run set. Batches are at most 500 previews.

**Facts carried.** Batch size at most 500. Order `(expired_at, preview_id)`.
One transaction per batch deleting three row types. Metric incremented after
commit by committed count. Metric is telemetry; database is source of truth.
The drained set is fixed at run start; later-eligible previews wait.

**Rewrite.**

> The worker drains the start-of-run set in batches of at most 500 previews,
> ordered by `(expired_at, preview_id)`. For each batch, one transaction
> deletes the rendered-output rows, build-log rows, and preview rows. After
> commit, the worker adds the committed preview count to
> `preview_cleanup_deleted_total`; the metric is telemetry, and the database
> remains the source of truth for whether deletion committed. Previews that
> become eligible after `run_started_at` wait for the next run.

Every fact survives. Duplicates are merged, the order follows execution, and
the exception follows the rule it modifies. Nothing was invented.

### 2. Find material gaps in a stateful asynchronous specification

**Source.**

> **Status:** Approved for implementation
>
> The Registry API writes a dataset URL, source revision, and checksum to the
> imports table. An Import Worker drains pending rows, downloads each dataset,
> and writes parsed documents to the search index. Transient failures are
> retried. Completed imports are marked `indexed`. Two Import Worker replicas
> run for availability. Maintainers can cancel work that has not started.

**Private model.** The database holds import work. Concurrent workers download
and index it. The document claims implementation readiness but does not define
identity, claiming, retry bounds, cancellation cut-off, or terminal failure.

**Review.**

> ## Specsavers
>
> **Verdict:** Not implementation-ready. Three material decisions are open.
>
> 1. **Import identity and input stability.** The API stores URL, revision,
>    and checksum, but nothing says which of them identify an import or whether
>    a worker must use the values present when work started. Two
>    implementations can index different revisions and both report `indexed`.
>    *Decision needed:* which stored fields identify an import, and whether
>    later changes to the row are rejected or ignored once work begins.
> 2. **Claiming, retry exhaustion, and terminal failure.** Two replicas drain
>    `pending` rows, but the only stated transition is to `indexed`. Nothing
>    prevents both replicas processing one row, bounds retries, or names a
>    failure state. *Decision needed:* how a worker obtains exclusive work,
>    whether retries are bounded, and what state an exhausted or permanently
>    failed import enters.
> 3. **Cancellation cut-off.** "Work that has not started" has no definition in
>    the lifecycle. *Decision needed:* the state or event after which
>    cancellation is refused.

No retry count, lock type, or state name is proposed. Row locks, advisory
locks, and leases are all possible; the document must choose one only if the
choice is externally observable.

### 3. Gratuitous ADR versus genuine fork

**Gratuitous.** "ADR-0042: Add the thumbnail endpoint" records that a required
endpoint follows the existing route, controller, and service pattern. Gate 1
fails: there is no credible alternative approach. The useful content, route
shape and validation ownership, belongs in the feature specification. Delete
the ADR; do not manufacture alternatives to save it.

**Genuine, but already home.** A canonical, durable feature specification
chooses a build-time static search bundle over a server-side search service,
records both options' forces, and states its consequences and the size limit
that would reopen the decision. Gates 1 to 3 hold. Gate 4 fails because the
specification is the durable, indexed record. No separate ADR.

**Genuine, and homeless.** A delivery plan marked "delete after project
closure" selects media-catalogue ownership of original files over
renderer-owned copies. The repository convention records cross-service
data-ownership decisions under `docs/adr/` as the durable record after plans
are removed. All four gates hold. Recommend an ADR, state the gate reasoning,
and create it only when the user asks.

### 4. Leave a concise, complete specification alone

**Source.**

> # Normalise local diagnostic timestamps
>
> ## Problem
>
> The command-line diagnostics package uses the host's local date formatting.
> The same event produces different text across time zones and cannot be
> compared reliably in tests or support records.
>
> ## Design
>
> Format an integer epoch-millisecond value as exactly
> `YYYY-MM-DDTHH:mm:ss.sssZ` in UTC. Accept values whose UTC year is from
> `0001` through `9999`; reject other values with `RangeError`. Existing
> message text, severity, and event-time selection do not change.
>
> ## Verification
>
> Tests cover the Unix epoch, a leap-day value, both accepted year boundaries,
> and one value beyond each boundary. The same input produces the same text
> under two host time zones.

**Review.**

> ## Specsavers
>
> No material findings. The problem, contract, input boundary, and
> verification are complete and clearly stated for a local formatting change.

Do not request goals, non-goals, alternatives, security, observability,
migration, rollback, risks, or a diagram. The document is short because the
design is small.

### 5. Reconcile what the document determines; ask about what it does not

**Source.** A specification declares its state table authoritative, with states
`queued`, `running`, `complete`, and `failed`. One paragraph says a successful
upload moves the job to `done`. The design section allows three attempts; the
verification section tests that the fifth attempt fails terminally.

**Judgement.** The `done` reference is a stale name, and the document names the
table as authority. Reconcile the paragraph to `complete`; this is derivation.
The attempt count has two values and no stated authority. Do not pick one.
Report the contradiction and ask the author which bound is intended, then
reconcile every section to that answer.
