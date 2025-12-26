// [>]: Match export endpoint.

import { NextResponse } from "next/server";

import { handleApiRequest } from "@/lib/api/handle-request";
import { getMatches } from "@/lib/services/matches";

// [>]: Practical limit for export operations.
const EXPORT_LIMIT = 100_000;

// [>]: GET /api/v1/matches/export - export all matches as JSON.
export const GET = handleApiRequest(async () => {
  const matches = await getMatches({ limit: EXPORT_LIMIT });
  return NextResponse.json(matches);
});
