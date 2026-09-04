# Sitemap refresh retries

**Status:** Implementation-ready

## Problem

The documentation build refreshes `sitemap.xml` from an immutable source
snapshot. A failed refresh must leave the sitemap from the previous successful
build intact.

## Design

The build selects one source manifest by `source_revision`. The manifest lists
the canonical public URL and last-modified date for every published page. The
refresher reads that manifest once per attempt, sorts entries by URL, and writes
deterministic UTF-8 sitemap bytes to a staging file beside the live sitemap.

The refresher validates the complete staging file before it replaces the live
file. Validation checks XML structure, entry count, unique URLs, URL syntax,
ordering, and the SHA-256 digest calculated while writing. A successful
validation closes and flushes the staging file, then atomically renames it over
`sitemap.xml`. The staging file and live file are on the same filesystem. No
attempt changes the live sitemap before that rename.

The refresher should retry temporary failures where appropriate.

A temporarily unavailable source snapshot, file-lock contention, or interrupted
local read or write is retryable. Before retrying, the refresher deletes the
partial staging file, waits 250 milliseconds, and starts again from the same
`source_revision`. An invalid manifest, invalid URL, permission error,
validation failure, or cross-filesystem output path is nonretryable. The
refresher deletes the staging file and returns the stable error code without
another attempt. A successful atomic rename completes the refresh.

The retry budget is the maximum number of attempts after the first retryable
failure. When the budget is exhausted, the refresher deletes the staging file,
returns `retry_exhausted`, and leaves the live sitemap unchanged. It makes no
more attempts for that build. The retry budget has not been selected.

## Verification

Filesystem tests inject each retryable and nonretryable error before the atomic
rename. They prove that retryable errors use the same source revision after the
250-millisecond delay, nonretryable errors stop immediately, and every failed
attempt removes its staging file while preserving the previous live sitemap.
An exhaustion test proves that the refresher returns `retry_exhausted`, stops,
and leaves the live sitemap unchanged. Success tests verify deterministic
bytes, every validation rule, and one atomic replacement of the live file.
