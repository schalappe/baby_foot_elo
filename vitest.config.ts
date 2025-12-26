import path from "path";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  // [>]: Load .env file for integration tests that need Supabase.
  const env = loadEnv(mode, process.cwd(), "");

  return {
    test: {
      globals: true,
      environment: "node",
      include: ["tests/**/*.test.ts"],
      env,
      // [>]: Run integration tests sequentially to avoid DB conflicts.
      // [!]: Integration tests share a real Supabase instance and can interfere with each other.
      sequence: {
        shuffle: false,
      },
      fileParallelism: false,
    },
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
  };
});
