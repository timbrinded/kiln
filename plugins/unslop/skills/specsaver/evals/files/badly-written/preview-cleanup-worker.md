# Documentation preview cleanup worker

**Status:** Approved and implementation-ready

## Background and configuration

The retention period for expired previews is 14 days, and the retry budget is
3. The retry budget is the budget for retries, i.e. the number of retries that
are permitted, after the initial one, for the same batch. Batches are 500. It
should be noted that all of these values are configuration. Batches are at most
500 previews. The retention period is the period after which an expired preview
is eligible, meaning that its `expired_at` is earlier than the cutoff, where the
cutoff is defined below in the notes.

## Problem

There are three kinds of records: preview records, build logs, and rendered
output rows. Maintainers need them for a while for short-term diagnosis after a
preview expires. They are all in PostgreSQL. After the retention period they
should be able to be deleted. Deletion is irreversible.

## Design

A dedicated PostgreSQL session is opened by the worker once per hour, and a
session-level advisory lock is acquired and `run_started_at` is recorded.
Deletion is disabled by default, and while it is disabled the worker still runs
on the same schedule but in preview mode. Whether deletion happened is
determined by the database and not by the metric. In the case that
the lock is held by another session then the new invocation will exit, and it
will not select records and it will also not delete records. It is important to
note that if the owning session disconnects, or if the process crashes, then
the lock is released, by the database.

Deletion is performed in batches. Each batch is processed in a single
transaction, which deletes the rendered output rows and also the build log rows
and also the preview rows. The metric `preview_cleanup_deleted_total` is
incremented. It is incremented after the transaction commits. It is incremented
by the number of previews in the batch that committed. Batches are ordered by
`expired_at` and then by `preview_id`. The metric is telemetry only. Previews
that became eligible after the run started are not part of the set drained by
this run and will instead be part of a later run. The set that is drained is
the start-of-run set.

In preview mode nothing is changed, and the count of eligible previews and the
oldest `expired_at` among them is written to the worker log, the eligible set
being selected in the same way as when deletion is enabled. Deletion has to be explicitly enabled
by a maintainer, who should first have reviewed the preview output. A committed
deletion cannot be undone; the only recovery is restoring from an external
database backup, which is to say that it is irreversible.

When a serialization failure occurs the batch is retried. The same batch is
retried, not a different one. If the retries are exhausted (see the retry
budget, above) then the batch is rolled back and the run ends, and the batch is
preserved, and so are all previews that had not yet been processed, so that a
later run can process them. Other errors, whether from the database or from the
worker itself, also end the run and also preserve the batch and the unprocessed
previews in the same way as exhaustion does.

## Notes

The cutoff is `run_started_at - retention_period`. A preview is in the run's
eligible set if its `expired_at` is earlier than the cutoff. See also the
retention period in the background section, which is 14 days.

## Verification

Integration tests show that a committed batch removes its preview, build-log,
and rendered-output records, while a failed transaction removes none of them,
and records with `expired_at` on or after the cutoff remain present, and tests
drain a start-of-run set larger than 500 across several batches without
selecting newly eligible rows, and prove that an overlapping invocation
performs no deletion, and prove that a process exit releases the advisory lock
for the next run, and they also prove that serialization retries preserve the
batch when the budget of 3 is exhausted, and preview-mode tests prove that a
run with deletion disabled logs the count and oldest `expired_at` and changes
no data.
