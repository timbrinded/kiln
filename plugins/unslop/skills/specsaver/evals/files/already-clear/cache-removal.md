# Cache removal

`remove(key)` deletes the entry with that exact key and returns `true` if the
entry existed. It returns `false` when the key is absent. Removing an entry
does not change the relative LRU order of the remaining entries.

An empty string is a valid key. Keys are case-sensitive. The method does not
normalize keys or remove entries with matching prefixes.

Verify removal of an existing key, removal of an absent key, an empty-string
key, distinct keys that differ only by case, prefix-related keys, and the
unchanged relative order of the remaining entries.
