# Delivery inputs

This note defines when an existing webhook worker obtains its inputs. The
delivery lifecycle, retries, and HTTP outcomes are specified elsewhere and
are unchanged.

Each delivery stores `delivery_id`, `event_id`, `endpoint_id`, and `payload`.
An endpoint stores `url` and `secret`. A delivery's payload is serialized JSON
captured when the delivery is created. Endpoint edits can change the URL.
The delivery's payload remains unchanged across every attempt. Endpoint edits
cannot change the secret. The worker reads the endpoint URL before each
attempt. The worker reads the endpoint secret before each attempt. A delivery
keeps the same `delivery_id` and `event_id` across all attempts.

An attempt has a timestamp in Unix seconds. The worker generates that
timestamp immediately before signing the request. The signature covers the
timestamp, a full stop, and the delivery's exact payload bytes. Retries use
the original payload bytes. The timestamp is sent in `X-Hook-Timestamp`.
The `delivery_id` is sent in `X-Hook-Delivery`. The signature is HMAC-SHA256
using the endpoint secret and is sent as lowercase hex in `X-Hook-Signature`.

Tests edit the URL between attempts and inspect the next destination. Tests
compare payload bytes and delivery identifiers across attempts. Tests check
that the signed timestamp equals the header timestamp for the same attempt.
Tests reject an endpoint edit that tries to change the secret.
