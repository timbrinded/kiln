# Brief: async report export API

Notes from Tuesday's planning session. This is what we agreed; write the API spec from it. One item is still open and is flagged near the end. Everything else is decided, so do not re-open it in the spec.

## Context

Reports today render synchronously in the dashboard and time out somewhere above 50k rows. We want an API where a client asks for an export, we build the file in the background, and they fetch it when it is ready. Same product, same tenants, same auth as the rest of the API.

## Decisions

- Auth: existing bearer tokens, nothing new. The organisation comes from the token and every export belongs to the caller's org. An export ID that belongs to another org behaves exactly like a missing one (404), never 403, so we do not leak IDs across tenants.
- Paths live under `/v1/`. Within a major version we only make additive changes (new optional fields, new endpoints). A breaking change means `/v2/`. Same rule the rest of the API already follows.
- Operations:
  - `POST /v1/exports` creates an export and returns 202 with the export object. Body: `report_id` (string), `format` (`csv` or `json`, nothing else), and an optional `filters` object with only these fields: `date_from`, `date_to`, `project_ids`, `include_archived`. Omitting `filters` is fine; sending `filters: null` or a non-object is a `validation_error` like any other wrong type. Unknown fields anywhere in the body, top level or inside `filters`, are rejected with the existing `validation_error`. We never silently drop input; a typo should not look like it worked.
    - `date_from` / `date_to` are full RFC 3339 timestamps (see below), not calendar dates, despite the names, which we inherited from the dashboard. The window is `date_from` inclusive to `date_to` exclusive. Either may be omitted. If both are present `date_from` must be earlier than `date_to`, otherwise `validation_error`.
    - `project_ids` is an array of strings, 1 to 50 entries, no duplicates. An empty array or a duplicate is a `validation_error`. An ID that does not exist or belongs to another org is also a `validation_error`, with the offending IDs named in the message; we do not silently filter them out. Omit the field to mean all projects.
    - `include_archived` defaults to false when omitted.
  - `GET /v1/exports/{id}` returns one export. This is the poll endpoint.
  - `GET /v1/exports` lists the org's exports newest first. Cursor pagination with `cursor` and `limit` query params; `limit` defaults to 25, max 100 (anything above 100, or below 1, is a `validation_error`). Response body is `{ "data": [...], "next_cursor": "..." }`: `data` is the array of export objects, `next_cursor` is null on the last page. Cursors are opaque keyset cursors and do not expire; a `cursor` we cannot decode is a 400 `validation_error`, not an empty page. List items are the same export object as the single GET except that `download_url` and `download_url_expires_at` are always null in a list. We are not signing up to 100 URLs per page, and the client only needs a URL for the one it is about to download; it fetches `GET /v1/exports/{id}` for that.
  - `POST /v1/exports/{id}/cancel` cancels an export that has not started, i.e. status `queued`. Any other status gets 409 `export_not_cancellable`. On success it returns the export with status `cancelled`.
- Idempotency on create: the `Idempotency-Key` header is required (missing gives 400 `idempotency_key_missing`). The value is 1 to 255 characters of printable ASCII; anything else is a `validation_error`. We recommend a UUID but do not enforce it. Keys are scoped to the org and remembered for 24 hours from the original create. Only a 202 stores the key: a create rejected with `validation_error`, `report_not_found` or `too_many_active_exports` does not burn it, so the client can fix the body or wait and retry with the same key. Same key and byte-identical body inside that window replays the stored response: same 202, same body as first returned (so status `queued` even if the job has since finished; poll the export for current state), no new job. Same key with a different body gives 422 `idempotency_key_reused`. Two concurrent creates with the same key and body: whichever stores first wins and the other replays its 202; no second job. After 24 hours the key is forgotten and reusing it creates a new export.
- Lifecycle: `queued` -> `running` -> `complete` or `failed`; `queued` -> `cancelled`. `complete`, `failed` and `cancelled` are terminal and never change again. `running` cannot be cancelled because a worker has already claimed it.
- Export object fields: `id`, `report_id`, `format`, `filters`, `status`, `created_at`, `started_at` (null until running), `finished_at` (null until terminal), `download_url`, `download_url_expires_at`, `file_expires_at`, and `error`. Every field is always present; we use null rather than omitting keys.
  - `filters` echoes what the client sent, normalised: always an object with all four keys, missing ones filled with their defaults (`date_from`, `date_to` and `project_ids` null, `include_archived` false). A create with no `filters` at all comes back as that all-defaults object, never null.
  - `error` is an object with `code` and `message` on `failed`, null otherwise. `code` is one of `render_failed` (the renderer threw; details are in our logs, not the message), `timeout` (the job ran past the 1 hour worker limit, which also covers a worker that died mid-run and never reported back: the export is marked `failed` with `timeout` once the hour is up) or `report_deleted` (the report went away between queue and run). New codes are additive, so clients should treat an unknown code as a generic failure.
  - `download_url` is a signed URL and is non-null only when status is `complete` and the file has not yet been deleted (next point); null in every other case. Each `GET /v1/exports/{id}` mints a fresh URL valid for 15 minutes and `download_url_expires_at` says when it dies. `download_url_expires_at` is null whenever `download_url` is null.
  - The file is kept for 7 days after completion and then deleted. `file_expires_at` is that moment; it is set when the export reaches `complete` and is null in every other state, including `failed` and `cancelled`. After deletion the record stays, status stays `complete`, and `download_url` goes back to null.
  - Records themselves live for 90 days from `created_at` whatever their status, then a nightly job hard-deletes them. They drop out of the list and the single GET returns 404 `export_not_found`. So the list does not grow forever and we do not need a delete endpoint.
- Concurrency: at most 5 exports per org may be in `queued` or `running` at the same time. A create that would exceed this gets 429 `too_many_active_exports` and nothing is queued. No `Retry-After` header on this one because it is not time-based; the client waits for one of its active exports to finish or cancels one.
- Errors use the existing envelope, `{ "error": { "code", "message", "request_id" } }`, same as everywhere else. New codes this API adds: `report_not_found` (404, the report ID does not exist or the org cannot see it), `export_not_found` (404), `export_not_cancellable` (409), `idempotency_key_missing` (400), `idempotency_key_reused` (422), `too_many_active_exports` (429). Body, query and header validation keeps using the existing `validation_error` (400).
- All timestamps are RFC 3339 in UTC with a `Z` suffix, in requests and responses alike.

## Not decided yet

Per-organisation rate limiting on `POST /v1/exports` (requests per minute, separate from the concurrency cap above). Product wants to see real usage for a few weeks before picking a number. The spec must record this as open and must not invent a limit.

## Out of scope

- Scheduled or recurring exports. That is its own project with its own scheduler work; nothing here should pre-empt it.
- Webhook or email notification on completion. We do not have a webhook delivery system yet, so this is poll-only for now.
- Formats beyond CSV and JSON. The report renderer cannot produce XLSX and we are not adding that here.
