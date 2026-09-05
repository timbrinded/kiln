# Route manifest publication

This change adds `publishManifest(routes, destination)` to the build library.
The caller supplies an immutable array of route entries and an absolute file
path whose parent directory already exists. Each entry has exactly two string
fields, `path` and `handler`. Calls for the same destination never overlap;
the caller enforces that precondition. All files involved are on the same
filesystem.

## Results and ordering

Success returns `{ count, digest }`. The count is the number of input entries,
and the digest is the lowercase hexadecimal SHA-256 of the bytes published.
The library emits one `manifest_published` log with the destination, count,
and digest after replacement succeeds. It emits no success log on failure.

Entries are ordered by the bytewise ASCII order of `path`, not the input order.
The output is a UTF-8 JSON array without whitespace between tokens, followed
by exactly one LF. Each object has `path` first and `handler` second. JSON
string escaping follows the existing `encodeJsonString` helper. An empty
input is valid and publishes `[]` followed by LF. Input entries are not mutated.

## File notes

The old destination must remain intact until replacement succeeds. A failed
call must leave its contents unchanged, or leave it absent if it did not
exist before the call. The existing `atomicReplace` helper guarantees this:
success atomically replaces the destination with the temporary file, and a
failure leaves both files unchanged. Success consumes the temporary file.
An existing reader may finish reading the old file after replacement.

## Input rules and failure reporting

Validation checks every input entry before performing file operations. Paths
must start with `/` and contain only `/`, lowercase ASCII letters, digits, and
hyphens. A path may consist only of `/`. Handlers must be nonempty and contain
only ASCII letters, digits, and underscores. Duplicate paths are invalid even
when their handlers are equal. An invalid entry or duplicate path returns
`invalid_input` without changing the destination or creating a temporary file.

Once validation passes, the library serializes the sorted entries and computes
the digest. It returns `io_error` if creating, writing, closing, or replacing
the temporary file fails. It does not retry any operation.

## Publication and cleanup

Create a temporary file in the destination's parent using the existing
`createTemp` helper, write all serialized bytes, and close it before calling
`atomicReplace`. The temporary file is private to this invocation. The helpers
report partial writes as failures; the caller must not publish a partial file.
After an I/O failure, attempt to remove a temporary file if one was created.
If this cleanup fails, still return the original `io_error` and add the cleanup
error as diagnostic metadata. This change makes no crash-durability promise.

## Verification

Verify identical bytes and digests for different permutations of the same
routes; correct escaping and field order; an empty manifest; each invalid
input and duplicate path leaving the destination unchanged without file
operations; failures at create, write, close, and replace; cleanup failure
preserving the original error; and an old reader finishing while a new reader
sees the replacement. Verify that replacement precedes the success log, that
failure emits no success log, and that calls never mutate input entries.
