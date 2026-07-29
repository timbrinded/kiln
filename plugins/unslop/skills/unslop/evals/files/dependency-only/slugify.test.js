import assert from "node:assert/strict";
import { test } from "node:test";
import slugify from "slugify";

const cases = [
  ["Hello World", "hello-world"],
  ["Multiple   Spaces", "multiple-spaces"],
  ["Trim!", "trim"],
  ["déjà vu", "deja-vu"],
  ["Rock & Roll", "rock-and-roll"],
];

for (const [title, expected] of cases) {
  test(`slugifies ${title}`, () => {
    assert.equal(slugify(title, { lower: true, strict: true }), expected);
  });
}
