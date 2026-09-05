# Feature brief: locale-aware formatter cache key

The TypeScript formatting package has an in-process `Map` of compiled message formatters. Its current key is the message ID. When one Node.js process formats the same message ID for `en-GB` and `fr-FR`, the second request can reuse the first locale's formatter and return text in the wrong language.

The change is local to this package. `locale` is already supplied as a canonical BCP 47 language tag and cannot contain a colon. Construct the cache key from the existing non-empty `locale` and `messageId` strings, separated by a colon. The formatter lookup and invalidation functions must use the same key helper. Keep the current 1,000-entry LRU behavior and public API. No persisted cache or network service reads these keys.

Tests must demonstrate separate entries for the same message ID in two locales, a cache hit within one locale, and invalidation of only the selected locale and message ID. A delimiter-boundary case uses a message ID that contains a colon and proves that it cannot collide with a different canonical locale and message-ID pair.
