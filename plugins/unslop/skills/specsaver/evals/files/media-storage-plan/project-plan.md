# Media-original storage delivery plan

**Status:** Delivery plan; delete after project closure

## Product requirement

The thumbnail renderer and archive exporter must read one canonical original
for each media asset without creating divergent source copies.

## Architectural choice

Two credible ownership models were evaluated:

1. Keep original files under the media catalogue and let rendering services
   read immutable object references.
2. Copy original files into renderer-owned storage and make the renderer the
   owner of those copies.

The project selects media-catalogue ownership. This prevents the renderer and
archive exporter from retaining divergent originals and keeps replacement and
deletion in one component. It adds a read dependency on catalogue-issued object
references and requires the catalogue to preserve a referenced version while a
render or export is active.

This choice defines the data-ownership boundary between the media catalogue,
thumbnail renderer, and archive exporter. Reversing it after delivery would
require moving stored objects, changing reference schemas, reconciling existing
copies, and coordinating all three components.

## Delivery tasks

- Add immutable version identifiers to catalogue object references.
- Update the renderer and exporter to read those references.
- Add cross-service replacement and deletion tests.
- Remove this delivery plan after the rollout retrospective.
