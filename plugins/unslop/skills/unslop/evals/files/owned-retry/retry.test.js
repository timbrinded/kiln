import assert from "node:assert/strict";
import { test } from "node:test";
import { loadWithRetry } from "./retry.js";

test("uses the product retry policy and reports failed attempts", async () => {
  let attempts = 0;
  const failedAttempts = [];

  const result = await loadWithRetry(
    async () => {
      attempts += 1;
      if (attempts < 3) {
        throw new Error("temporary");
      }
      return "ready";
    },
    error => failedAttempts.push(error.attemptNumber),
  );

  assert.equal(result, "ready");
  assert.equal(attempts, 3);
  assert.deepEqual(failedAttempts, [1, 2]);
});

test("preserves the error object required by telemetry", async () => {
  const expected = new Error("permanent");
  let reported;

  await assert.rejects(
    loadWithRetry(
      async () => {
        throw expected;
      },
      error => {
        reported = error.error;
      },
    ),
    expected,
  );

  assert.equal(reported, expected);
});
