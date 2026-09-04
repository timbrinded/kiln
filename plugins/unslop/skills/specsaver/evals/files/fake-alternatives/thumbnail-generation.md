# Thumbnail generation placement

**Status:** Decision-ready

## Problem

The thumbnail behavior and external contract are established in the
authoritative feature specification. This note decides only where that behavior
runs. The media service owns source-image metadata and derived-media records and
is the existing deployment boundary for image processing. The product must
remain self-hosted.

## Design

Place the established thumbnail behavior in the existing media service. This
keeps source lookup, rendering, and derivative ownership with the component that
already owns them.

## Alternatives considered

- Do nothing. This does not satisfy the established thumbnail contract.
- Rewrite the complete media platform. This would be too complex for this
  placement decision.
- Use a third party. A third party might solve the problem, but none was
  evaluated and the product must remain self-hosted.

## Rationale

The existing media service is the only placement consistent with current data
ownership and the self-hosting constraint.
