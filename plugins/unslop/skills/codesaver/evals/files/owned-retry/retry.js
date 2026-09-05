import pRetry from "p-retry";

export function loadWithRetry(load, onAttemptFailure) {
  return pRetry(load, {
    onFailedAttempt: onAttemptFailure,
    retries: 2,
  });
}
