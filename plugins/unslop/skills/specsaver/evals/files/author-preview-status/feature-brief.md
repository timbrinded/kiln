# Preview list status

We need to stop presenting stale previews as current. A preview can be out of
date because its build revision is old or because its expiry time has passed.

The list will call `classifyPreview(preview, currentRevision, now)`, a pure
helper. The caller supplies a validated preview with `revision` and
`expires_at`, the current revision string, and `now`. Times are integer
milliseconds on the same clock; revisions are opaque, case-sensitive strings.

We first check whether `now >= expires_at`. If so, we're done: the status is
`expired`, even if the revision also differs. Otherwise we compare the two
revisions. Matching revisions mean `current`; different revisions mean
`outdated`. The helper should not read the clock itself or change its inputs.

The UI will keep its existing labels and layout. Let's cover equal and
unequal revisions before expiry, the exact expiry boundary, and a time after
expiry. Include an expired preview whose revision differs, and check that
inputs remain unchanged.
