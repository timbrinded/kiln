# Documentation preview cleanup worker

**Status:** Approved and implementation-ready

## Problem

Expired documentation preview records retain build logs and rendered-output
rows that maintainers need for short-term diagnosis. All three record types are
stored in PostgreSQL and must become eligible for deletion after the selected
retention period.

## Design

Deletion is disabled by default. In preview mode, the worker reports the count
and oldest `expired_at` value of eligible previews without changing data. A
maintainer must explicitly enable deletion after reviewing preview output. A
committed deletion is irreversible; recovery requires restoration from an
external database backup.

Once each hour, an enabled worker opens a dedicated PostgreSQL session,
acquires a session-level advisory lock, and records `run_started_at`. If another
session holds the lock, the new invocation exits without selecting or deleting
records. The database releases the lock if the owning session disconnects or
the process crashes. The run's eligible set is the previews whose `expired_at`
is earlier than `run_started_at - retention_period`. Previews that become
eligible after `run_started_at` wait for the next run.

The worker drains that start-of-run set in batches of at most 500 previews,
ordered by `(expired_at, preview_id)`. For each batch, it deletes rendered
output rows, build-log rows, and preview rows in one transaction and increments
`preview_cleanup_deleted_total` by the committed preview count after commit.
The metric is operational telemetry; the database remains the source of truth
for whether deletion committed.

The worker retries a serialization failure against the same deletion batch.
The retry budget is the maximum number of retry attempts after the initial
transaction fails. Exhaustion rolls back the batch, ends the run, and preserves
that batch and all unprocessed previews for a later run. Any other database or
worker error has the same preservation behavior.

## Configuration

- Retry budget: **TBD**
- Expired-preview retention period: **TBD**
- Batch size: 500 previews

## Verification

Integration tests show that a committed batch removes its preview, build-log,
and rendered-output records, while a failed transaction removes none of them.
Records with `expired_at` on or after the cutoff remain present. Tests drain a
start-of-run set larger than 500 across several batches without selecting newly
eligible rows, prove that an overlapping invocation performs no deletion, and
prove that a process exit releases the advisory lock for the next run. They
also prove that serialization retries preserve the batch when the configured
budget is exhausted. Preview and disabled-mode tests prove that neither mode
changes data.
