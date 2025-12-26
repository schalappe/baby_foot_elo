// [>]: Player rankings endpoint.

import { NextRequest, NextResponse } from "next/server";

import { handleApiRequest, getNumericParam } from "@/lib/api/handle-request";
import { filterActiveEntities, rankByElo } from "@/lib/api/ranking";
import { getAllPlayersWithStats } from "@/lib/services/players";

// [>]: GET /api/v1/players/rankings - players sorted by ELO.
// Filters to active players (played within days_since_last_match days).
export const GET = handleApiRequest(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);
  const limit = getNumericParam(searchParams, "limit", 100);
  const daysSinceLastMatch = getNumericParam(
    searchParams,
    "days_since_last_match",
    180,
  );

  const players = await getAllPlayersWithStats();
  const activePlayers = filterActiveEntities(players, daysSinceLastMatch);
  const ranked = rankByElo(activePlayers, limit);

  return NextResponse.json(ranked);
});
