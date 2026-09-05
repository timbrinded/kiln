# Upload job operations

This note defines the job operations inside the existing upload service.
Authentication, job lookup, and organisation isolation are already provided
by the service. Operations on a job are serialized by the existing job lock.

The stored states are `queued`, `running`, `complete`, `failed`, and
`cancelled`. The final three states are terminal. A worker may move a queued
job to running. A running job becomes complete after publishing its object.

Cancellation is accepted only while the job is `queued`. An accepted
cancellation changes the state to `cancelled` and returns 204. Every other
state returns 409 without changing the job. Workers skip cancelled jobs.

While a job is running, it accepts chunks of at most 8 MiB, where one MiB is
1,048,576 bytes. A larger chunk is rejected with 413 before writing any of
that chunk. Chunk order, checksums, and final-object assembly use the existing
uploader unchanged.

A permanent upload error ends the job. The worker must delete that job's
temporary chunks before marking it `failed`. If cleanup fails, keep the job
`running` and surface the cleanup error to the existing operator retry path.
The last upload error is stored when the job becomes failed.

Logs include `job_id`, state transitions, and error codes. Logs must not
contain the bearer token. Each successful state transition emits one log
after its transaction commits. A rejected operation emits no transition log.
