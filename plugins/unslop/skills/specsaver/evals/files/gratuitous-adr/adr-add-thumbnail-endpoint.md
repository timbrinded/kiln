# ADR-0042: Add the thumbnail endpoint

**Status:** Accepted

## Context

The thumbnail feature specification requires an HTTP operation that accepts an
asset identifier, width, height, and output format. The existing
`ThumbnailService` owns source lookup, dimension limits, format selection,
rendering, and derivative-cache writes. The media service already exposes asset
operations through its route, controller, and domain-service pattern.

## Decision

Add `GET /v1/assets/{assetId}/thumbnail` by following the existing media-route
pattern. The controller validates the request shape and calls
`ThumbnailService`; it does not duplicate rendering or cache behavior.

## Consequences

The feature adds one route, one controller method, service tests, and an HTTP
contract test. Route wiring leaves `ThumbnailService` ownership unchanged. It
introduces no new dependency, service boundary, data owner, or construction
technique.
