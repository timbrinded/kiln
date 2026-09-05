# Thumbnail Key Builder responsibility

**Status:** Implementation-ready component note

The Media Renderer stores a thumbnail record with immutable `thumbnail_id` and
`format` fields and mutable source filename and caption fields. `format` is one
of `jpeg`, `png`, or `webp`.

The Thumbnail Key Builder is not a media-library editor. It does not render
images. It does not upload objects. It does not select a delivery provider. It
will not generate HTML. It is not responsible for usage billing. Because an
object key must remain stable when editorial metadata changes, it must not
include the source filename or caption.

Given a thumbnail record, the Thumbnail Key Builder returns an ASCII object key
that is unique for `(thumbnail_id, format)`. Repeating the same tuple returns the
same key. Different supported tuples return different keys.

Tests change the filename and caption without changing the returned key, cover
all three formats, repeat a tuple, and compare distinct tuples.
