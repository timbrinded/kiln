# Export API overview

`GET /exports/{job_id}` returns the stored state and a nullable result URL.
A result URL is returned only when the stored state is `done`.

An export can have three total attempts. A transient error on the third
attempt therefore moves it to `failed`.

This overview does not override the worker note's authoritative state table.
