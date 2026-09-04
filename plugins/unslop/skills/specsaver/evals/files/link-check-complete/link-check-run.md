# Documentation link-check run

**Status:** Implementation-ready

## Problem and boundary

A documentation release can contain stale external links. The Documentation
Builder owns release contents and creates a content-addressed link manifest.
The Link Checker owns check runs and their results. The existing queue provides
at-least-once delivery; it is a transport and is not the source of result
state.

The builder's manifest lists only absolute HTTP and HTTPS links; the builder
checks relative links as part of its existing build validation. A manifest
entry with any other target is therefore a builder defect and is rejected.

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
entry, or non-HTTP target returns `400 invalid_manifest` and creates no run.

The pair (`release_id`, `manifest_sha256`) identifies one run. The Link Checker
assigns that run a UUID `run_id` and returns it with `201`. Repeating a request
with the same pair returns `200` with the existing `run_id`. Reusing
`release_id` with a different manifest digest returns
`409 release_manifest_mismatch` and changes nothing.

Run creation copies the manifest entries into the Link Checker database in one
transaction. The copied source locations and URLs are immutable. A URL is
canonicalised by lowercasing its scheme and host, removing its fragment and a
default port, and preserving its path and query. One result covers every source
location with the same canonical URL. The WHATWG URL serializer supplies all
other normalisation. A result's stable key is
`sha256(run_id + "\n" + canonical_url)`, and it is the result table's primary
key, so one result row exists per key.

## Queue and worker behaviour

Run creation inserts every result as `pending` with an immediate
`next_probe_at` and a null `published_probe_at`. Every two minutes, a dispatcher
selects the `pending` results and the due `retry_wait` results whose
`published_probe_at` differs from `next_probe_at`. For each, it publishes
(`run_id`, result key, `scheduled_probe_at`) with `scheduled_probe_at` equal to
`next_probe_at`, then copies that value to `published_probe_at` only after the
queue accepts the message. A failed publish is retried. A crash after queue acceptance
but before the database update can publish the same scheduled probe twice; this
is expected. Workers read the immutable URL from the result row.

Before it probes a URL, a worker begins a transaction and selects the result row
by its primary key with `FOR UPDATE NOWAIT`. If another transaction holds
the row lock, the worker leaves the message unacknowledged and changes nothing;
the queue redelivers it after its redelivery delay, and the redelivered message
finds a terminal row, acquires the lock, or repeats this no-op while the earlier
probe is still running. The queue redelivers an unacknowledged message until it
is acknowledged; it does not dead-letter. With the lock held, the worker
acknowledges a terminal result or a message whose `scheduled_probe_at` no longer
matches `next_probe_at`. If the message matches `next_probe_at` but the retry is
not yet due, the worker sets `published_probe_at` to null, commits, and then
acknowledges, so the dispatcher republishes the probe when it is due. Otherwise,
it keeps the transaction and row lock open while it probes the URL, writes the
outcome, and commits.

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

The worker classifies the final response after the optional fallback. A final
response from `200` through `299` is `valid`. Any `408`, `429`, or `5xx`
response is retryable. DNS failures, connection failures, and timeouts are also
retryable. All other `4xx` responses, any final `3xx` response, invalid TLS
certificates, redirect loops, more than eight redirects, and any egress-client
rejection of a blocked address or URL credentials are `broken`; an egress
rejection stores the failure class `blocked_by_policy`. Thus, a fallback GET response of
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

The builder polls `GET /runs/{run_id}`. The response carries the run state and,
once the run is terminal, every `broken` or `unreachable` result with its
canonical URL, outcome, and the source page and line of each manifest entry
grouped under it. A `failed` run does not block release publication; the
builder attaches the report to the release.

Metrics count results by state and outcome and report the age of the oldest
`pending` or due `retry_wait` result. Logs for dispatch, probe, and completion
use `run_id` and the result key.

## Verification

Integration tests deliver the same result key concurrently to two workers and
verify that only one probe is active, one terminal row exists, and the losing
delivery is redelivered and then acknowledged against the terminal row. A crash test closes the first worker's transaction
after its probe but before its result commit; PostgreSQL must roll back and
release the row lock, and redelivery must repeat the safe probe and complete the
same result row.

Other tests cover manifest rejection with `400`, idempotent run creation with
`201` then `200`, the run report with grouped source locations, URL
canonicalisation and source-location grouping, a failed queue publication,
each permanent and retryable classification including an egress-policy
rejection, the HEAD-to-GET fallback and its
`405` and `501` outcomes, both retry delays, the third-attempt `unreachable`
transition, empty manifests, and concurrent completion of the last two results.
They verify that terminal run and result states cannot be changed.
