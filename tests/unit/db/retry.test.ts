import { describe, expect, it, vi } from "vitest";
import { withRetry } from "@/lib/db/retry";

describe("withRetry", () => {
  it("should return result on first successful call", async () => {
    const fn = vi.fn().mockResolvedValue("success");
    const wrapped = withRetry(fn);

    const result = await wrapped();

    expect(result).toBe("success");
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("should retry on failure and succeed", async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new Error("fail 1"))
      .mockRejectedValueOnce(new Error("fail 2"))
      .mockResolvedValue("success");

    const wrapped = withRetry(fn, { retryDelay: 10 });

    const result = await wrapped();

    expect(result).toBe("success");
    expect(fn).toHaveBeenCalledTimes(3);
  });

  it("should throw after exhausting all retries", async () => {
    const fn = vi.fn().mockRejectedValue(new Error("persistent failure"));
    const wrapped = withRetry(fn, { maxRetries: 3, retryDelay: 10 });

    await expect(wrapped()).rejects.toThrow("persistent failure");
    expect(fn).toHaveBeenCalledTimes(3);
  });
});
