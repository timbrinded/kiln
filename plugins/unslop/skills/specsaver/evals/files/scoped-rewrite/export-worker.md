# Export worker

The exporter renders an immutable report snapshot in the background. The
API and report-rendering contracts are unchanged by this note.

## State definitions

This table is authoritative for stored state names. Other descriptions must
use these names.

| State | Meaning |
| --- | --- |
| `queued` | Available for a worker to claim. |
| `running` | Held by one worker. |
| `complete` | The result URL is stored and visible. |
| `failed` | The last error is stored; no further work is scheduled. |

## Worker processing

The result URL becomes visible to polling clients after the transaction
commits. The transaction records the URL and moves the job to `done`. Before
that a worker will render the report to a temporary object. Before that it
will claim the job, which is to say that the job becomes `running`, with a
conditional update from `queued`, and a claim that updates no rows means
that worker will not render anything. The renderer returns a stored object
URL on success and a classified error on failure.

A transient error sends the job to `queued` again by releasing its claim.
When the total attempt limit is reached instead, the worker records the
last error and changes the state to `failed` in one transaction. The total
attempt limit has not been decided. A permanent error does the same failure
transaction immediately and does not schedule another attempt.

## Verification

Verify a claim race with exactly one winner, a zero-row claim that does not
render, polling on either side of the success commit, transient requeueing,
failure at the eventual attempt limit, and immediate permanent failure.
