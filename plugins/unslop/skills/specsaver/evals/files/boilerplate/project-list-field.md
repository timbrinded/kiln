# Include owner display names in project summaries

## Problem

The project list returns only `owner_id`. The web client must request each
owner record before it can label a project, which adds requests and lets the
list change between reads. The same project-list caller can already read each
display name from the owner endpoint.

## Design

`GET /projects` adds a required, nullable `owner_display_name` field to every
project summary. Its value is the current `display_name` from the owner record
read in the same database snapshot as the project list. It is `null` when the
owner has no display name. Existing authorization, filters, ordering, and
pagination do not change. Version 1 clients must ignore response members that
they do not recognize.

The HTTP handler calls `projectRepository.listWithOwners`, passes the returned
rows to `projectSummaryMapper`, and passes the mapped objects to `sendJson`.
The mapper copies each owner's display name into the response object.

## Verification

Contract tests cover a non-null display name, a null display name, two projects
with different owners, stable pagination, and an existing client that ignores
the new member. A concurrency test changes an owner's display name while the
list is read and confirms that the project and owner values come from one
database snapshot.

## Non-Goals

- This change does not redesign user profiles.
- This change does not add GraphQL.
- This change does not replace PostgreSQL.
- This change does not create an administrative console.
- This change does not change account recovery.

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

All software changes have risk. Appropriate care and sufficient testing will
be used to manage it.
