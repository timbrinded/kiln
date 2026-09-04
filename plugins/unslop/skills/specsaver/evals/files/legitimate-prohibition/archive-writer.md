# Export archive integrity requirements

This excerpt defines the integrity boundary between a committed export manifest
and archive creation. The Archive Writer creates one archive containing the
manifest entries in their recorded order.

The key words `MUST` and `MUST NOT` in this document are to be interpreted as
described in BCP 14.

For every write attempt, the Archive Writer MUST reuse the stored `export_id`.
It MUST NOT add, remove, rename, or reorder entries from the committed manifest.

Verification builds the same manifest through initial and retry paths, then
asserts that both archives retain the stored export identifier, entry names,
entry order, and content digests.
