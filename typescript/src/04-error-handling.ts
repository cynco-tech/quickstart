/**
 * Cynco API Quickstart -- 04: Error Handling
 *
 * Demonstrates how to handle every error type the SDK can throw:
 * - ValidationError (422): invalid input data
 * - AuthenticationError (401): bad or missing API key
 * - PermissionError (403): key lacks required permissions
 * - NotFoundError (404): resource doesn't exist
 * - ConflictError (409): state conflict or duplicate
 * - RateLimitError (429): too many requests
 * - APIError (5xx): server-side errors
 *
 * Run: npm run example:errors
 */

import Cynco from "@cynco/sdk";

const cynco = new Cynco({
  apiKey: process.env.CYNCO_API_KEY,
});

/**
 * Comprehensive error handling with the SDK's typed errors.
 * Each error type has specific properties you can inspect.
 */
async function handleAllErrorTypes(): Promise<void> {
  console.log("=== Error Handling Examples ===\n");

  try {
    // This will fail if the customer ID doesn't exist.
    const customer = await cynco.customers.retrieve("cus_nonexistent");
    console.log("Customer:", customer.name);
  } catch (error: unknown) {
    if (error instanceof Cynco.NotFoundError) {
      // 404 -- the resource doesn't exist.
      console.log("[NotFoundError]");
      console.log(`  Message: ${error.message}`);
      console.log(`  Status:  ${error.status}`);
      console.log(`  Code:    ${error.code}`);
      console.log(`  Request: ${error.requestId}\n`);
    } else if (error instanceof Cynco.ValidationError) {
      // 422 -- input data failed validation.
      // The `details` array tells you exactly which fields are wrong.
      console.log("[ValidationError]");
      console.log(`  Message: ${error.message}`);
      for (const detail of error.details) {
        console.log(`  Field "${detail.field}": ${detail.message}`);
      }
      console.log();
    } else if (error instanceof Cynco.AuthenticationError) {
      // 401 -- the API key is invalid or missing.
      console.log("[AuthenticationError]");
      console.log(`  Message: ${error.message}`);
      console.log("  Action: Check your CYNCO_API_KEY environment variable.\n");
    } else if (error instanceof Cynco.PermissionError) {
      // 403 -- the API key doesn't have permission for this operation.
      console.log("[PermissionError]");
      console.log(`  Message: ${error.message}`);
      console.log(
        "  Action: Check key permissions in Settings > API Keys.\n"
      );
    } else if (error instanceof Cynco.RateLimitError) {
      // 429 -- too many requests.
      // The `retryAfter` property tells you when to retry (in seconds).
      console.log("[RateLimitError]");
      console.log(`  Message:     ${error.message}`);
      console.log(`  Retry after: ${error.retryAfter}s`);
      console.log(`  Limit:       ${error.limit} req/min\n`);
    } else if (error instanceof Cynco.ConflictError) {
      // 409 -- state conflict (e.g., trying to void an already-voided invoice).
      console.log("[ConflictError]");
      console.log(`  Message: ${error.message}\n`);
    } else if (error instanceof Cynco.APIError) {
      // 5xx -- server error. Safe to retry with backoff.
      console.log("[APIError]");
      console.log(`  Status:  ${error.status}`);
      console.log(`  Message: ${error.message}`);
      console.log(`  Request: ${error.requestId}\n`);
    } else {
      // Network errors, timeouts, etc.
      console.error("[Unknown error]", error);
    }
  }
}

/**
 * Retry logic with exponential backoff.
 * Useful for handling transient errors (429, 5xx) in production.
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  options: { maxRetries?: number; baseDelay?: number } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 1000 } = options;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: unknown) {
      const isLastAttempt = attempt === maxRetries;

      // Only retry on rate limits and server errors.
      if (error instanceof Cynco.RateLimitError) {
        if (isLastAttempt) throw error;
        const delay = error.retryAfter * 1000;
        console.log(`Rate limited. Retrying in ${error.retryAfter}s...`);
        await sleep(delay);
      } else if (
        error instanceof Cynco.APIError &&
        error.status >= 500
      ) {
        if (isLastAttempt) throw error;
        // Exponential backoff: 1s, 2s, 4s
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(
          `Server error (${error.status}). Retrying in ${delay}ms...`
        );
        await sleep(delay);
      } else {
        // Don't retry client errors (4xx except 429).
        throw error;
      }
    }
  }

  // TypeScript requires this -- the loop always returns or throws above.
  throw new Error("Unreachable");
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main(): Promise<void> {
  await handleAllErrorTypes();

  // Demonstrate retry logic.
  console.log("=== Retry with Backoff ===\n");

  try {
    const invoices = await withRetry(
      () => cynco.invoices.list({ limit: 5 }),
      { maxRetries: 3, baseDelay: 1000 }
    );
    console.log(
      `Fetched ${invoices.data.length} invoices with retry support.\n`
    );
  } catch (error: unknown) {
    console.error("All retries exhausted:", error);
  }
}

main().catch((error: unknown) => {
  console.error("Error handling example failed:", error);
  process.exit(1);
});
