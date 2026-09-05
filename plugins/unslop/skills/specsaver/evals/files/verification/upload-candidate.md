# Upload job operations

This note defines job operations inside the existing upload service. The
service already provides authentication, job lookup, and organisation
isolation. Its existing job lock serializes operations on each job.

## Lifecycle and cancellation

The states are `queued`, `running`, `complete`, `failed`, and `cancelled`.
The final three are terminal. A worker may move a queued job to running;
publication of its object moves a running job to complete.

Cancellation is accepted while the job is queued or running. It changes the
state to cancelled and returns 204. All other states return 409 without
changing the job. Workers skip cancelled jobs.

## Chunks and failures

A running job accepts chunks of at most 16 MiB (1,048,576 bytes per MiB).
Larger chunks return 413 before any bytes from that chunk are written. Chunk
order, checksums, and final-object assembly use the existing uploader.

A permanent upload error ends the job. The worker marks it failed and
stores the last upload error. If cleanup fails, keep the job running and
surface the cleanup error to the existing operator retry path.

## Logs

Logs contain the job ID, state transitions, error codes, and the bearer
token. A successful state transition emits one log after its transaction
commits. Rejected operations emit no transition log.
