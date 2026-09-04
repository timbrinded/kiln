# Documentation link-check run

**Status:** Implementation-ready

## Problem and boundary

A documentation release can contain stale external links. The Documentation
Builder owns release contents and creates a content-addressed link manifest.
The Link Checker owns check runs and their results. The existing queue provides
at-least-once delivery; it is a transport and is not the source of result
state.

The Link Checker checks absolute HTTP and HTTPS links. The builder checks
relative links as part of its existing build validation.

All probes use the existing public-web egress client without cookies or
application credentials. That client rejects URL credentials and any literal,
resolved, or redirected destination outside public unicast address space. It
repeats the address check before each connection.

## Run input and identity

The builder starts a run with `release_id`, `manifest_uri`, and
`manifest_sha256`. A manifest entry contains the source page, source line, and
target URL. `manifest_uri` addresses an object whose content cannot be
replaced. Before creating a run, the Link Checker reads the complete manifest
and verifies `manifest_sha256`. A missing object, digest mismatch, malformed
entry, or non-HTTP target rejects the request without creating a run.

The pair (`release_id`, `manifest_sha256`) identifies one run. The Link Checker
assigns that run a UUID `run_id`. Repeating a request with the same pair returns
the existing `run_id`. Reusing `release_id` with a different manifest digest
returns `409 release_manifest_mismatch` and changes nothing.

Run creation copies the manifest entries into the Link Checker database in one
transaction. The copied source locations and URLs are immutable. A URL is
canonicalised by lowercasing its scheme and host, removing its fragment and a
default port, and preserving its path and query. One result covers every source
location with the same canonical URL. The WHATWG URL serializer supplies all
other normalisation. A result's stable key is
`sha256(run_id + "\n" + canonical_url)`. A unique constraint permits one result
row per key.

## Queue and worker behaviour

Run creation inserts every result as `pending` with an immediate
`next_probe_at` and a null `published_probe_at`. A dispatcher scans `pending`
results and due `retry_wait` results every two minutes when
`published_probe_at` differs from `next_probe_at`. It publishes (`run_id`,
result key, `scheduled_probe_at`) with `scheduled_probe_at` equal to
`next_probe_at`, then copies that value to `published_probe_at` only after the
queue accepts it. A failed publish is retried. A crash after queue acceptance
but before the database update can publish the same scheduled probe twice; this
is expected. Workers read the immutable URL from the result row.

Before it probes a URL, a worker begins a transaction and selects the result row
by its full primary key with `FOR UPDATE NOWAIT`. If another transaction holds
the row lock, it acknowledges the duplicate delivery without changing state.
With the lock held, the worker also acknowledges a terminal result, a message
whose `scheduled_probe_at` no longer matches `next_probe_at`, or a retry that is
not yet due. Otherwise, it keeps the transaction and row lock open while it
probes the URL, writes the outcome, and commits.

A worker acknowledges its queue delivery only after it commits the outcome.
If the process or database connection fails first, PostgreSQL rolls back the
transaction and releases the row lock; the queue then redelivers the message.
Repeating a probe after a crash is permitted because link probes are read-only.
The system does not need to infer whether the earlier probe reached the remote
server.

Each probe attempt starts with `HEAD`, follows at most eight redirects, and uses
a 12-second timeout for each request. If the final HEAD response is `405` or
`501`, the worker makes one fallback `GET` with `Range: bytes=0-0`; it does not
repeat the fallback within that attempt. The HEAD request and its optional GET
are one probe attempt. Each later scheduled attempt starts with HEAD again.

The worker classifies the final response after the optional fallback. A
response from `200` through `399` is `valid`. Any `408`, `429`, or `5xx`
response is retryable. DNS failures, connection failures, and timeouts are also
retryable. All other `4xx` responses, invalid TLS certificates, redirect loops,
and more than eight redirects are `broken`. Thus, a fallback GET response of
`405` is `broken`, while a fallback GET response of `501` is retryable.

After the first retryable outcome commits, `next_probe_at` is two minutes after
that commit time. After the second retryable outcome commits, `next_probe_at` is
twelve minutes after that commit time. In both cases the result enters
`retry_wait` and sets `published_probe_at` to null. A third retryable outcome
becomes `unreachable`. Only a committed probe outcome counts as an attempt; a
worker crash does not consume the retry budget.

## State and completion

Result states are `pending`, `retry_wait`, `valid`, `broken`, and `unreachable`.
The last three are terminal. An active probe is represented by its database row
lock rather than a durable state. Each terminal result stores the canonical URL,
final response or failure class, completed-attempt count, and completion time.

Run states are `checking`, `passed`, and `failed`. A nonempty run is created as
`checking`. When a worker writes a terminal result, the same transaction locks
the run row. It changes the run to `passed` when all results are `valid`, or to
`failed` when all results are terminal and at least one is `broken` or
`unreachable`. A manifest with no external links is created directly as
`passed`. `passed` and `failed` are terminal.

Metrics count results by state and outcome and report the age of the oldest
`pending` or due `retry_wait` result. Logs for dispatch, probe, and completion
use `run_id` and the result key.

## Verification

Integration tests deliver the same result key concurrently to two workers and
verify that only one probe is active, one terminal row exists, and the duplicate
delivery is acknowledged. A crash test closes the first worker's transaction
after its probe but before its result commit; PostgreSQL must roll back and
release the row lock, and redelivery must repeat the safe probe and complete the
same result row.

Other tests cover manifest digest rejection, idempotent run creation, URL
canonicalisation and source-location grouping, a failed queue publication,
each permanent and retryable classification, the HEAD-to-GET fallback and its
`405` and `501` outcomes, both retry delays, the third-attempt `unreachable`
transition, empty manifests, and concurrent completion of the last two results.
They verify that terminal run and result states cannot be changed.
