import assert from "node:assert/strict";
import test from "node:test";

import { isFeatureEnabled } from "./feature.js";

test("returns the configured boolean", () => {
  assert.equal(isFeatureEnabled({ enabled: true }), true);
  assert.equal(isFeatureEnabled({ enabled: false }), false);
});
