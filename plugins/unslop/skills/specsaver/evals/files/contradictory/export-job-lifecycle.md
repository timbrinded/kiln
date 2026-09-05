# Report export job lifecycle

**Status:** Implementation-ready

## Problem

Report exports run in the background and can fail part-way. Support staff need
one durable record of each export's outcome, and the API must let a client poll
for it.

## States

The following table is the authoritative definition of export job states. No
other state value is valid.

| State | Meaning | Terminal |
| --- | --- | --- |
| `queued` | The job is stored and no worker has claimed it. | No |
| `running` | Exactly one worker holds the job's claim. | No |
| `complete` | The export file is stored and its URL is recorded on the job. | Yes |
| `failed` | The last error is recorded on the job. | Yes |

## Behaviour

`POST /exports` stores one job as `queued` and returns its `job_id`. A worker
claims a `queued` job by updating it to `running` in the same statement that
checks it is still `queued`; a claim that affects zero rows is abandoned.

The worker renders the report to a temporary object, then in one transaction
records the object URL on the job and moves the job to `done`. A client polling
`GET /exports/{job_id}` sees the URL only after that transaction commits.

A transient storage or network error causes the worker to release the claim by
returning the job to `queued`. A job may be attempted at most three times in
total. When the limit is reached, the worker records the last error and moves
the job to `failed`.

## Verification

Tests cover a claim race between two workers where only one claim succeeds, a
poll before and after the completing transaction, a transient error that
returns the job to `queued`, and a job whose fifth attempt fails and is marked
`failed` with the last error recorded.
