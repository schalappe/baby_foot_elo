// [!]: Server-only module. Do not import from client components.

import { createClient, SupabaseClient } from "@supabase/supabase-js";

let supabase: SupabaseClient | null = null;

/**
 * Returns a singleton Supabase client for server-side operations.
 * Throws if environment variables are missing.
 *
 * Supports both publishable key (recommended) and legacy anon key (for local dev).
 */
export function getSupabaseClient(): SupabaseClient {
  if (supabase) {
    return supabase;
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  // [>]: Prefer publishable key; fall back to anon key for local Supabase.
  const key =
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY) must be set",
    );
  }

  supabase = createClient(url, key);
  return supabase;
}
