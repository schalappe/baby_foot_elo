// [>]: Team rankings endpoint.

import { NextRequest, NextResponse } from "next/server";

import { handleApiRequest, getNumericParam } from "@/lib/api/handle-request";
import { rankByElo } from "@/lib/api/ranking";
import { getActiveTeamRankings } from "@/lib/services/teams";

// [>]: GET /api/v1/teams/rankings - teams sorted by ELO.
// Filters to active teams (played within days_since_last_match days).
export const GET = handleApiRequest(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);
  const limit = getNumericParam(searchParams, "limit", 200);
  const daysSinceLastMatch = getNumericParam(
    searchParams,
    "days_since_last_match",
    180,
  );

  // [>]: Fetch active teams with filtering done at service layer.
  const activeTeams = await getActiveTeamRankings({
    daysSinceLastMatch,
  });
  const ranked = rankByElo(activeTeams, limit);

  return NextResponse.json(ranked);
});
