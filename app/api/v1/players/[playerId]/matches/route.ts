// [>]: Player match history endpoint.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  getNumericParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getPlayerById } from "@/lib/db/repositories/players";
import { getMatchesByPlayer } from "@/lib/services/matches";

type PlayerRouteContext = RouteContext<"playerId">;

// [>]: GET /api/v1/players/[playerId]/matches - get player's match history.
export const GET = handleApiRequest(
  async (request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");
    const { searchParams } = new URL(request.url);

    const limit = getNumericParam(searchParams, "limit", 10);
    const skip = getNumericParam(searchParams, "skip", 0);
    const startDate = searchParams.get("start_date") ?? undefined;
    const endDate = searchParams.get("end_date") ?? undefined;

    // [>]: Verify player exists (throws PlayerNotFoundError if not).
    await getPlayerById(id);

    const matches = await getMatchesByPlayer(id, {
      limit,
      skip,
      startDate,
      endDate,
    });

    return NextResponse.json(matches);
  },
);
