# Include parser mode in local schema-cache identity

## Problem

The TypeScript schema package caches parsed schemas by source hash. The same source has different accepted constructs in `strict` and `compatible` parser modes, so a result parsed in one mode can be returned for the other mode.

## Design

The observable cache identity is the ordered pair `(parserMode, sourceHash)`. Two entries are identical only when both tuple members are equal. Cache lookup and invalidation use this identity. The parser mode remains either `strict` or `compatible`; the source hash remains the existing SHA-256 digest. This design does not prescribe a helper name or string encoding.

## Verification

Tests parse the same source hash in both modes and show that each lookup returns its mode's result. Invalidating one tuple leaves the other tuple present.

## Non-Goals

- This change does not replace the cache with Redis.
- This change does not redesign the parser.
- This change does not add a database.
- This change does not create a command-line interface.
- This change does not change package licensing.

## Security

Not applicable.

## Migration

N/A.

## Observability

Not applicable for this change.

## Rollback

N/A.

## Internationalisation

Not applicable.

## Risks

There are always risks when software changes, but appropriate care and sufficient testing will be used to manage them.
