// [>]: Single match endpoints: GET, DELETE.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getMatchWithPlayerElo, deleteMatch } from "@/lib/services/matches";

type MatchRouteContext = RouteContext<"matchId">;

// [>]: GET /api/v1/matches/[matchId] - get match with ELO changes.
// Consolidated endpoint returning both player and team ELO data.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: MatchRouteContext) => {
    const { matchId } = await context!.params;
    const id = parseIdParam(matchId, "matchId");
    const match = await getMatchWithPlayerElo(id);
    return NextResponse.json(match);
  },
);

// [>]: DELETE /api/v1/matches/[matchId] - delete match.
// [!]: Does not reverse ELO changes (matches Python behavior).
export const DELETE = handleApiRequest(
  async (_request: NextRequest, context?: MatchRouteContext) => {
    const { matchId } = await context!.params;
    const id = parseIdParam(matchId, "matchId");
    await deleteMatch(id);
    return new NextResponse(null, { status: 204 });
  },
);
