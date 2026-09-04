# Outbound webhook delivery

**Status:** Draft for review

## Background

Customers who want to react to changes in their account currently poll `GET /v1/events`
on a timer, and the three largest integrators poll every few seconds, which is roughly
40% of our read traffic for almost no new data. Webhooks are a widely used pattern for
this kind of notification. We already have the `jobs` worker pool and the `events` table
(every state change writes one row there), so the pipeline described here consumes that
table rather than adding a new source of truth. This document describes the design.

## Retry schedule

An attempt that fails is retried, as described below, on a fixed schedule: the second
attempt is made 30 seconds after the first, then 2 minutes, 10 minutes, 1 hour, 6
hours and 24 hours after the previous one, for a maximum of 7 attempts per delivery,
so a delivery that never succeeds is given up roughly 31 hours after it was created. The
client times out at 10 seconds, and a timeout is retried like any other failure. After
the seventh failed attempt the delivery moves to `exhausted`; the customer can replay it
(see the replay section) and it counts towards the auto-disable rule for the subscription
described in the next section.

## Endpoints

A customer registers an endpoint with `POST /v1/webhook_endpoints`, giving an `https` URL
(plain `http` is rejected with 422) and one or more event types from the published catalogue
such as `invoice.paid`; the response is 201 with the endpoint object (`endpoint_id`, `url`,
`event_types`, `status`, `created_at`) plus a `secret`, 32 random bytes as base64url, shown
once and never returned again (`GET /v1/webhook_endpoints/{id}` gives the object without
it), so the customer has to store it, and it is the key for the HMAC described below.
`PATCH /v1/webhook_endpoints/{id}` changes `url` and/or `event_types` and returns 200 with
the object; the type list applies to events created after the change, and as the URL is
read from the endpoint row at attempt time a pending delivery goes to the new URL on its
next attempt. Secrets cannot be rotated; a customer who leaks one deletes the subscription
and creates a new one. `status` is `enabled`, `disabled` or `deleted`. A subscription is
disabled automatically when 20 consecutive deliveries to it, in the order they finish,
reach `exhausted` with no delivered delivery in between, which is what `consecutive_exhausted`
counts (how it is kept is in the deliveries section); on disable we email the account
owners, mark the endpoint `disabled`, mark its still-pending deliveries `exhausted` with no
attempt row and no change to any counter, and stop creating deliveries for it; an attempt
already in flight at that moment still writes its attempt row when it finishes but leaves
the delivery `exhausted` and moves no counter. The customer
re-enables with `POST /v1/webhook_endpoints/{id}/enable`, which resets the consecutive
counter to zero and returns 200 with the object, also when it was already enabled; events
that occurred while the endpoint was paused have no delivery row, so there is nothing to
replay, and a customer who needs them backfills from `GET /v1/events`. `DELETE` returns
204, sets `status` to `deleted` and cancels pending deliveries in the same way as pausing
does, except that there is no way back: enable on a deleted endpoint is 409, and the row
is kept for good so that `GET` on the endpoint and on its deliveries keep working for
whatever history retention has not yet removed.

## Deliveries and attempts

A delivery is the obligation to get one event to one endpoint. Its ID is `whd_` followed
by a ULID and is stable for the life of the delivery. An attempt is one HTTP `POST` to
the endpoint URL on behalf of a delivery; a delivery has at most seven attempts, numbered
from 1 and all carrying the same delivery ID, and none at all when a disable or `DELETE`
exhausts it before the first. The body is JSON with `delivery_id`, `event_id` (`evt_`
plus ULID, the ID of the `events` row), `type`, `created_at` (the event's RFC 3339
timestamp) and `data`, the payload as stored on the `events` row. Headers are
`Content-Type: application/json`, `X-Hook-Delivery-Id`, `X-Hook-Event` (the type),
`X-Hook-Timestamp` (Unix seconds when the attempt is made, so it differs between
attempts of one delivery) and `X-Hook-Signature`. An attempt succeeds when the
endpoint returns any 2xx status and the full response has arrived within 10 seconds of
the attempt starting, and fails on any other status including 3xx, which is not followed,
and on DNS failure, TLS failure, connection refused or the timeout; the outcome, status
code, duration and first 1 KB of the response body are written to a `webhook_attempts`
row before the delivery's status is updated, `webhook_attempts_total` is incremented
with an `outcome` label of `success`, `http_error`, `timeout` or `connect_error`
(the last covers DNS, TLS and connection refused), and a failed attempt sets `next_attempt_at` from the
schedule above unless it was the seventh, in which case the delivery becomes `exhausted`,
`webhook_deliveries_exhausted_total` is incremented and the endpoint's `consecutive_exhausted`
goes up by one; a delivery exhausted by disable or `DELETE` touches neither and writes no
attempt row. A successful attempt moves the delivery to `delivered` and zeroes
`consecutive_exhausted`, both counter changes happening in the transaction that sets the
terminal status, which is why the count runs in finishing order and not creation order,
and either way the same update clears the lease described under storage. Delivery is
at-least-once: a receiver may see the same delivery twice if it returned 2xx but we
crashed before recording it, so receivers must treat `delivery_id` as an idempotency key.
Ordering is not guaranteed, neither between events nor between attempts of different
deliveries to the same endpoint; a receiver that needs order sorts by `created_at` on its
side. Up to 8 attempts to one endpoint may be in flight at once from each poller instance
(we run two, so a receiver should be ready for 16); endpoints do not affect each other.

## Signature

The signature is HMAC-SHA256, keyed with the endpoint secret, over the value of
`X-Hook-Timestamp`, a full stop, and the raw request body bytes. The header value is
`v1=` followed by the lowercase hex digest. Because the timestamp changes per attempt
(see above) the signature is recomputed for every attempt. Receivers should compute
the expected value over the raw bytes, compare in constant time, and reject the request
when the timestamp is more than 300 seconds from their own clock in either direction,
which bounds replay of a captured request.

## Replay

A customer can replay any finished delivery, whether it ended `delivered` or `exhausted`
(a `pending` one returns 409), with `POST /v1/deliveries/{delivery_id}/replay`, for 30
days from the event's `created_at`; the window is checked against the clock, not against
whether the rows still exist, so at day 30 the request is a 404 even if the nightly job
has not run yet, and a delivery whose `events` row has already gone is a 404 as well.
Replay returns 201 with a new delivery object, that is a new delivery with a new
`delivery_id` for the same `event_id` and endpoint, with a fresh attempt schedule, and
does not touch the original, so a receiver that wants to ignore replays dedupes on
`event_id` rather than `delivery_id`. Replay against a paused or deleted endpoint returns
409, the window check coming first so that an out-of-window replay is a 404 whatever the
endpoint's status, and replays count towards the auto-disable rule like any other delivery.

## Storage and operations

`webhook_endpoints` holds the URL, the secret (encrypted at rest with the account data
key), the event types, `status` and `consecutive_exhausted`; `webhook_deliveries` holds
one row per delivery with `status` (`pending`, `delivered`, `exhausted`), `attempt_count`,
`next_attempt_at` and `leased_until`, indexed on `(status, next_attempt_at)`; `webhook_attempts`
holds one row per attempt with its number, timing, status code, error code and response
excerpt. Delivery and attempt rows are deleted 30 days after the event's `created_at` by
the nightly retention job, and the `events` rows already have a 30-day retention, which is
why events older than 30 days cannot be replayed; customers find a `delivery_id` to replay
via `GET /v1/webhook_endpoints/{id}/deliveries`, which lists the endpoint's delivery objects
(`delivery_id`, `event_id`, `endpoint_id`, `status`, `attempt_count`, `next_attempt_at`,
`created_at`) newest first, filtered by `status` and `event_id` query parameters, 50 per
page and at most 200, paged with `after=<delivery_id>`. The poller runs in the `jobs` pool,
wakes every second, and claims up to 100 `pending` deliveries whose `next_attempt_at` has
passed and whose `leased_until` is null or in the past with `SELECT ... FOR UPDATE SKIP
LOCKED`, sets `leased_until` 60 seconds ahead and commits before making a single request,
so several instances run without double-sending and a delivery whose poller died
mid-attempt is claimed again once the lease runs out, subject to the per-endpoint limit
of 8 above; a claimed row that cannot start in this tick because its endpoint's 8 slots
are taken has its lease cleared with no attempt made and waits for a later tick. Operators
get the two counters described in the deliveries section, a histogram
`webhook_attempt_duration_seconds`, a counter `webhook_endpoints_disabled_total`, and a
gauge `webhook_delivery_backlog` for pending deliveries whose `next_attempt_at` is in the
past and that are not under a live lease, which is the alerting signal (page at 1,000 for
5 minutes). Exactly one original delivery is created per (event, endpoint) pair, in the
same transaction that inserts the `events` row, for every enabled endpoint subscribed to
the event's type, with `next_attempt_at` set to the creation time so the first attempt is
due at once; replay is the only other thing that creates a delivery. Each attempt
writes one structured log line with the same fields as the attempt row plus `endpoint_id`
and the URL's host, but not its path or query, since customers put tokens in those.

## Verification

Tests must show that an `http` URL is rejected and an `https` URL returns a secret that
a later `GET` does not, that an event creates exactly one `pending` delivery per enabled
subscribed endpoint in the same transaction and none for unsubscribed or disabled ones,
that an attempt carries the four `X-Hook-*` headers and a signature that verifies with
the secret and fails when one body byte changes, that a 2xx within 10 seconds marks the
delivery `delivered` while a 500, a 302, a refused connection and a response after 10
seconds each record a failed attempt with the correct `outcome` and schedule the next
at the documented offset, that the seventh failure marks the delivery `exhausted`, that
the twentieth consecutive exhausted delivery disables the endpoint, exhausts its pending
deliveries and sends the email while a delivered delivery in between resets the count,
that enable resets the counter and new events flow again, that a `PATCH` of the URL is
used by a pending delivery's next attempt, that deliveries exhausted by disable or `DELETE`
have no attempt row and move neither counter, that a deleted endpoint answers 409 to enable
and still answers `GET` and its deliveries listing, that replay creates a new delivery with
the same `event_id` and a different `delivery_id` and returns 409 for a paused endpoint or a
`pending` delivery and 404 at 30 days whether or not the rows are still there, that two
poller instances never both claim one delivery, that a delivery whose lease has expired
mid-attempt is claimed again and one under a live lease is not, that one instance never
has more than 8 attempts to one endpoint in flight, and that the retention job removes
rows older than 30 days and nothing younger.
