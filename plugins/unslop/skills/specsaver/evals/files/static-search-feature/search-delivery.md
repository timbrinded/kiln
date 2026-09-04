# Documentation search delivery

**Status:** Approved

**Canonical record:** This feature specification remains under `docs/specs/`
for the lifetime of documentation search. It is the durable record of the
delivery decision and its rationale.

## Problem

Readers need full-text search across the published documentation. The site must
remain deployable as static files through the existing content-delivery host,
and search results need to change only when a new documentation release is
published.

## Decision

Generate a static search bundle during the documentation build. The build reads
the canonical release manifest, indexes the title, headings, and body text of
each public page, and writes a Brotli-compressed `v1` bundle named with the
release identifier and content digest. Draft and excluded pages are absent.

The release manifest references that exact bundle name and digest. The browser
search reader fetches the bundle through the same static host as the site,
rejects a digest mismatch or schema version other than `v1`, and performs
tokenization, ranking, and result highlighting locally. A schema change must
ship its matching reader in the same release. The build fails before release
publication if bundle generation or its verification fails.

The current public corpus produces a 1.4 MB compressed bundle. The release
acceptance limit is 2 MB; exceeding it blocks the release and requires this
decision to be reviewed rather than silently dropping pages or fields.

## Live alternatives

### Build-time static bundle

The selected design preserves the static deployment model, has no search
runtime to operate, and makes the bundle consistent with its documentation
release. It adds a bounded client download and cannot update search between
releases.

### Server-side search service

A server-side service could maintain its own index and expose a query endpoint.
It would support incremental updates and avoid downloading the complete index,
but it would add a stateful deployment, a runtime availability dependency, an
interface to version, and separate operating work. Those costs do not serve the
release-level freshness requirement.

## Consequences

Search remains available whenever the static site and bundle are available.
Clients download the bundle once per release and cache it by its digest. Search
does not provide per-reader ranking or content newer than the active release.
If the measured bundle crosses the acceptance limit, the team must reconsider
partitioning or a server-side service in this canonical specification.

## Verification

Build tests prove deterministic output, inclusion of every public manifest page,
exclusion of drafts, stable ranking fixtures, and failure before publication for
an invalid bundle or a bundle over 2 MB. Browser tests load the manifest and its
matching bundle, reject digest and schema mismatches, return expected title and
body matches, and use the cached digest without another download during the
same release.
