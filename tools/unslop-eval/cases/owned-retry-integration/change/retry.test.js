import assert from "node:assert/strict";
import test from "node:test";

import { deliver } from "./retry.js";

test("uses the application max-attempt contract and reports retries", async () => {
  const retries = [];
  let calls = 0;

  const result = await deliver(
    async () => {
      calls += 1;
      if (calls < 3) throw new Error(`failure-${calls}`);
      return "sent";
    },
    {
      maxAttempts: 3,
      onRetry: ({ attempt, error }) => retries.push([attempt, error.message])
    }
  );

  assert.equal(result, "sent");
  assert.equal(calls, 3);
  assert.deepEqual(retries, [
    [1, "failure-1"],
    [2, "failure-2"]
  ]);
});

test("does not report a retry after the final compatible attempt", async () => {
  const retries = [];

  await assert.rejects(
    deliver(
      async () => {
        throw new Error("offline");
      },
      {
        maxAttempts: 2,
        onRetry: ({ attempt }) => retries.push(attempt)
      }
    ),
    /offline/
  );

  assert.deepEqual(retries, [1]);
});
