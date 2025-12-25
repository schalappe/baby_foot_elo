// [>]: Retry utility for database operations. Matches Python backend pattern.

export interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
}

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_RETRY_DELAY = 500;

type AsyncFunction<T extends unknown[], R> = (...args: T) => Promise<R>;

/**
 * Wraps an async function with retry logic.
 *
 * @param fn - The async function to wrap.
 * @param options - Configuration for max retries and delay between attempts.
 * @returns A wrapped function that retries on failure.
 */
export function withRetry<T extends unknown[], R>(
  fn: AsyncFunction<T, R>,
  options: RetryOptions = {},
): AsyncFunction<T, R> {
  const { maxRetries = DEFAULT_MAX_RETRIES, retryDelay = DEFAULT_RETRY_DELAY } =
    options;

  return async (...args: T): Promise<R> => {
    // [>]: Preserve original error type for instanceof checks in error handlers.
    let lastError: unknown = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn(...args);
      } catch (error) {
        lastError = error;
        const message = error instanceof Error ? error.message : String(error);
        console.warn(`Attempt ${attempt}/${maxRetries} failed: ${message}`);

        if (attempt < maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, retryDelay));
        }
      }
    }

    const message =
      lastError instanceof Error ? lastError.message : String(lastError);
    console.error(`All ${maxRetries} attempts failed. Last error: ${message}`);
    throw lastError;
  };
}
