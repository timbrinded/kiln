# Worked Examples

Use these complete patterns when a fragment is not enough to judge structure,
maturity, or repair scope. Adapt only the concerns activated by the target
document. Do not turn these examples into templates.

## 1. Tighten a Bloated Service Spec into a Positive Model

### Source document

```markdown
# Media Transcode Worker

## Goals

The goal is to build a Media Transcode Worker.

## Non-goals

The worker does not edit the media catalog. It does not create uploads. It does
not replace object storage. It does not alter source objects. It does not choose
editorial policy. It does not add a streaming service. It is not the source of
truth for media metadata.

## Proposed design

We will add a robust and scalable service. It will generally find jobs in the
database, handle media, and ensure that errors are handled gracefully. It will
have a WorkerManager, RetryManager, MediaProcessor, StorageManager, and
TelemetryManager. Each manager will have a factory and interface.

## Security

The service will be secure.

## Migration

Not applicable.

## Observability

Telemetry will be added as appropriate.

## Rollback

The change can be rolled back if needed.
```

### Review

```markdown
## Specsavers

**Verdict:** Not implementation-ready — 2 blockers, 2 majors.

### Findings

1. **[BLOCKER] Directive 8 — Job state and failure behavior are absent**
   - **Evidence:** The design says only that the service finds and handles jobs.
   - **Consequence:** Implementations can choose incompatible claim, retry,
     duplicate-output, and terminal-state behavior.
   - **Fix: Resolve** — define the source job, claim semantics, retry identity
     and classes, and terminal outcomes.
   - **Required decision:** The document does not determine those semantics.

2. **[BLOCKER] Directive 9 — The material quality claims are unverifiable**
   - **Evidence:** `robust`, `scalable`, and `secure` have no behavior or bound.
   - **Consequence:** The design cannot establish acceptance or justify its
     component structure.
   - **Fix: Resolve** — identify which quality attributes are requirements and
     supply their operating conditions and acceptance thresholds.
   - **Required decision:** The source does not identify which qualities are
     material or what acceptance thresholds they must meet.

3. **[MAJOR] Directive 2 — The worker is defined through exclusions**
   - **Evidence:** The Non-goals section lists seven things the worker does not
     do, while the design never states its positive responsibility.
   - **Consequence:** Ownership of transcoding and result writing remains hard
     to infer.
   - **Fix: Rewrite** — state that the worker transforms immutable source media
     under catalog-defined jobs and records each output; retain the prohibition
     against modifying source objects.

4. **[MAJOR] Directive 14 — Template sections and managers add no design
   information**
   - **Evidence:** Migration and rollback are generic, telemetry is undefined,
     and five manager abstractions have no material responsibility.
   - **Consequence:** Ceremonial prose obscures the incomplete processing model.
   - **Fix: Delete** — remove the `N/A` and generic sections and the unmotivated
     class list; add only concerns resolved by findings 1 and 2.
```

### Minimal apply result after the author supplies the missing decisions

```markdown
# Media Transcode Worker

## Problem

Editors currently start failed derivative generation by hand. Repeated starts
can create duplicate outputs and do not provide a durable terminal result.

## Design

The Transcode Worker processes immutable jobs from the media catalog, writes
derivatives to object storage, and records each result. It must not modify a
source object or its catalog checksum.

One worker atomically claims a `pending` job. Every attempt reuses its job
identifier and output path. A stored derivative moves the job to `complete`; a
permanent decoder failure or four exhausted transient attempts moves it to
`failed`. Another worker can reclaim a job only after its 90-second claim
expires.

The job table is the source of truth. It stores the claim expiry, attempt count,
output checksum when available, terminal state, and last error.

## Verification and delivery

Tests demonstrate exclusive claiming, identifier and output-path reuse,
unchanged source checksums, transient retry, claim recovery, and both terminal
states. Editors can count jobs by state and inspect the last failure without
access to worker logs.
```

The values in this result are legitimate only because the hypothetical author
supplied them after the review. Specsavers must not infer `four` or `90 seconds`
from the source document.

## 2. Find Material Gaps in a Stateful Asynchronous Spec

### Source document

```markdown
# Public dataset ingestion

**Status:** Approved for implementation

The Registry API writes a dataset URL, source revision, and checksum to the
imports table. An Import Worker drains pending rows, downloads each dataset,
and writes parsed documents to the search index. Transient failures are
retried. Completed imports are marked `indexed`.

Two Import Worker replicas run for availability. Maintainers can cancel work
that has not started.

Verification will include unit and integration tests.
```

### Private system model

The database holds public-dataset import work. Concurrent workers download and
index it. The approved document does not define the authority, identity, claim,
retry, cancellation, or terminal-failure contracts needed to preserve that
model.

### Review

```markdown
## Specsavers

**Verdict:** Not implementation-ready — 3 blockers.

### Findings

1. **[BLOCKER] Directive 5 — Source identity can change during an import**
   - **Evidence:** The Registry API writes a URL, revision, and checksum, but the
     worker contract does not identify which values are authoritative or
     whether they remain fixed after work starts.
   - **Consequence:** Two implementations can index different source revisions
     while reporting the same import as complete.
   - **Fix: Resolve** — decide which stored source fields define an import and
     whether a worker must reject or ignore later changes.
   - **Required decision:** The available text does not establish that data
     ownership boundary.

2. **[BLOCKER] Directive 8 — The lifecycle has no claim or terminal-failure
   semantics**
   - **Evidence:** Two replicas drain `pending` rows, but the only stated
     transition is to `indexed`; cancellation races and retry exhaustion are
     undefined.
   - **Consequence:** Replicas can process the same import concurrently, and
     implementations can retry forever, stop silently, or invent states.
   - **Fix: Resolve** — define legal claims and transitions, cancellation's
     cutoff, retry exhaustion, and the terminal failure record.
   - **Required decision:** No claim strategy, retry budget, or failure state is
     derivable.

3. **[BLOCKER] Directive 10 — Retry and duplicate identity are undefined**
   - **Evidence:** Transient failures are retried, but neither import nor
     document identity is specified after an uncertain index response.
   - **Consequence:** A retry can create duplicate documents or combine results
     from different source revisions.
   - **Fix: Resolve** — define the idempotency identity and required behavior
     after an unknown indexing outcome.
   - **Required decision:** The document does not determine the identity or
     reconciliation rule.
```

Do not invent a retry count, lock type, claim duration, state name, or indexing
algorithm. Row locks, advisory locks, and leases are possible local mechanics
until a material behavior requires one.

## 3. Remove a Gratuitous ADR for Routine Feature Work

### Source document

```markdown
# ADR-0024: Add a sitemap endpoint

## Context

Search crawlers need the current list of public pages.

## Decision

Add `GET /sitemap.xml` through the existing content router, page query, XML
renderer, and route-registration pattern.

## Alternatives

1. Do not publish a sitemap.
2. Rewrite the static-site publisher.
3. Use the established pattern.

## Consequences

We must implement and test the endpoint.
```

### Four-gate assessment

- **Real fork:** fails. The approved requirement and repository architecture
  leave one ordinary implementation path. `Do nothing` and `rewrite` are not
  live alternatives.
- **Architectural significance:** fails. No ownership, boundary, dependency, or
  costly-reversal change is proposed.
- **Durable rationale:** not reached.
- **Separate value:** not reached.

### Review

```markdown
## Specsavers

**Verdict:** Not an architectural decision — 1 major.

### Findings

1. **[MAJOR] Directive 13 — Routine feature work is presented as an ADR**
   - **Evidence:** The endpoint follows the existing content query, renderer,
     and routing pattern; the other listed options are not credible.
   - **Consequence:** The ADR catalog gains no durable architectural rationale
     and makes routine work appear to be a new fork.
   - **Fix: Move** — put the required sitemap behavior and verification in the
     feature spec, then delete this ADR.
```

No replacement ADR is created. The useful feature contract can be only a few
paragraphs.

## 4. Keep a Genuine Fork in the Feature Spec, Then Separate It Only When Useful

### Durable feature spec

```markdown
# Documentation search delivery

## Problem

Readers need full-text search, while the documentation site must remain
deployable as static files. Search results need to change only with a published
documentation release.

## Decision

Generate a versioned, compressed search bundle during the documentation build.
The release manifest names the bundle and its digest. The browser loads the
matching bundle and performs search locally.

We considered a server-side search service. It would support updates between
releases and avoid a complete client download, but it would add a stateful
deployment, runtime availability dependency, and separately versioned query
interface. Those costs do not serve the release-level freshness requirement.

The static bundle preserves the site's existing deployment model and is
consistent with its release. The current compressed bundle is 1.4 MB against a
2 MB release limit. Exceeding that limit blocks release and reopens the design.

## Consequences

Search has no runtime service to operate and remains available with the static
site. Clients download one bundle per release. Search cannot provide content
newer than the active release or per-reader ranking.
```

### Gate assessment when this spec is canonical

- A real fork exists: a build-time bundle and server-side search are credible.
- Deployment topology, runtime dependencies, update cadence, and client cost
  are architectural.
- The rationale has durable value.
- A separate record adds no value because this feature spec is durable,
  canonical, indexed with architecture documents, and already owns the full
  rationale.

Result for the ADR threshold: no Directive 13 finding and no separate ADR. The
rest of the specification still requires its ordinary directive review.

### Changed context where a separate ADR adds value

Assume instead that the text above exists only in a transient launch plan that
will be removed after delivery. The repository's indexed ADR catalog is the
durable source for deployment-model decisions. Several documentation sites will
reuse this search-delivery model. Gate 4 now passes.

Only after the user asks to create the record, a compact ADR can be:

```markdown
# Use a build-time bundle for documentation search

## Context

Documentation search can ship as a static bundle with each release or run as a
server-side search service. The site uses static hosting, and search freshness
is required only at release boundaries.

## Decision

Build a versioned, compressed search bundle from the release manifest and load
it in the browser. Reconsider the decision if the bundle exceeds the release
size limit.

## Alternatives

A server-side service supports incremental updates and smaller client
downloads, but it adds a stateful deployment, runtime dependency, and query
interface that the release-level freshness requirement does not need.

## Consequences

Search remains part of the static release and has no runtime service. Clients
download one bundle per release, and search cannot update between releases.
Future documentation sites use the same delivery model unless their measured
bundle size or freshness requirement reopens the decision.
```

The feature spec should link the ADR instead of keeping a second drifting copy
of the rationale.

## 5. Leave a Concise High-Quality Spec Alone

### Source document

```markdown
# Include render mode in local template-cache identity

## Problem

The static-site publisher caches compiled templates by template path. Preview
and production modes compile the same path with different output rules, so one
build can receive a template compiled for the other mode.

## Design

Key every entry by the tuple `(renderMode, templatePath)`. The selected build
target is the authoritative source of `renderMode`; callers cannot supply a
different value. Cache eviction and compiled-template values are unchanged.

## Verification

A test compiles the same template path in preview and production modes and
confirms that each subsequent lookup returns its own value. Existing same-mode
cache-hit and eviction tests remain unchanged.
```

### Applicability and review result

This is an implementation-ready local design. It has no network protocol,
persisted-data migration, asynchronous state, or rollout risk. The problem,
positive design, authority, externally important key behavior, and verification
are complete.

```markdown
## Specsavers

No material findings. The specification fixes the render-mode isolation
behavior and verification without adding concerns that the local cache change
does not activate.
```

Do not request goals, non-goals, alternatives, security, observability,
migration, rollback, risks, diagrams, numerical qualities, or an ADR. The
document is short because the design is small, not because it is incomplete.
