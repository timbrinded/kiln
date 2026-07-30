import assert from "node:assert/strict";
import test from "node:test";

import { articlePath } from "./article.js";

test("builds an owned article path", () => {
  assert.equal(articlePath("release-notes"), "/articles/release-notes");
});
