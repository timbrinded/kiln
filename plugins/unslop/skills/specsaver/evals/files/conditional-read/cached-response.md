# Cached responses

`lookup(key, now)` returns the stored payload when the key exists and `now`
is strictly earlier than the entry's `expires_at`; it returns `miss` when the
key is absent or the entry has expired.

`now` and `expires_at` are integer milliseconds on the same clock, and an
entry is expired when `now >= expires_at`. Keys use exact, case-sensitive
matching. Lookup changes neither the stored entries nor their LRU order.

Verification covers a present entry immediately before, exactly at, and
immediately after expiry; an absent key; keys that differ only by case; and
unchanged cache contents and LRU order after each lookup.
