# Optional CSV report export

**Status:** Decision-ready; not implementation-ready

## Problem

Reports can currently be downloaded only as JSON. Spreadsheet users need a CSV
form without losing the existing machine-readable export.

## Design

An export request selects `csv` or `json`. A CSV export reads the same committed
report snapshot as a JSON export, writes UTF-8, and uses the report schema's
field order for its header and rows. The existing export worker creates and
delivers both formats.

## Managed decisions

- Select whether a report can have one active CSV export or several concurrent
  exports. This must be resolved before implementation.
- Select whether a repeated request for the same report snapshot and format
  creates a new file or reuses the existing file. This must be resolved in the
  export contract.

## Non-goal

CSV export does not replace JSON export.

## Verification

Tests cover CSV header and row ordering, JSON export after CSV is enabled, and
both outcomes of the two managed decisions once selected.
