// [>]: Team match history endpoint.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  getNumericParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getMatchesWithTeamElo } from "@/lib/services/matches";
import { getTeam } from "@/lib/services/teams";

type TeamRouteContext = RouteContext<"teamId">;

// [>]: GET /api/v1/teams/[teamId]/matches - get team's match history with ELO changes.
export const GET = handleApiRequest(
  async (request: NextRequest, context?: TeamRouteContext) => {
    const { teamId } = await context!.params;
    const id = parseIdParam(teamId, "teamId");
    const { searchParams } = new URL(request.url);

    const skip = getNumericParam(searchParams, "skip", 0);
    const limit = getNumericParam(searchParams, "limit", 100);

    // [>]: Verify team exists (throws TeamNotFoundError if not).
    await getTeam(id);

    // [>]: Get matches with team ELO changes for the match history display.
    const matches = await getMatchesWithTeamElo(id, { skip, limit });

    return NextResponse.json(matches);
  },
);
