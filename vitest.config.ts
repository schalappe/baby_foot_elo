import path from "path";
import { defineConfig } from "vitest/config";
import dotenv from "dotenv";
import fs from "fs";

export default defineConfig(() => {
  // [>]: Load .env.test for tests (local Supabase), .env for dev (remote Supabase).
  // [>]: Tests use local Supabase instance, development uses remote production instance.
  const testEnvPath = path.resolve(process.cwd(), ".env.test");
  const envPath = path.resolve(process.cwd(), ".env");

  // [>]: Check if we should use test environment.
  const useTestEnv = fs.existsSync(testEnvPath);

  // [>]: Load appropriate environment file.
  if (useTestEnv) {
    dotenv.config({ path: testEnvPath });
  } else if (fs.existsSync(envPath)) {
    dotenv.config({ path: envPath });
  }

  return {
    test: {
      globals: true,
      environment: "node",
      include: ["tests/**/*.test.ts"],
      // [>]: Run integration tests sequentially to avoid DB conflicts.
      // [>]: Local Supabase provides isolation, but sequential runs are more reliable.
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
