import { runWithRetries } from "retry-driver";

export async function deliver(operation, { maxAttempts, onRetry }) {
  let attempts = 0;
  return runWithRetries(async () => {
    attempts += 1;
    try {
      return await operation();
    } catch (error) {
      if (attempts < maxAttempts) onRetry({ attempt: attempts, error });
      throw error;
    }
  }, maxAttempts - 1);
}
