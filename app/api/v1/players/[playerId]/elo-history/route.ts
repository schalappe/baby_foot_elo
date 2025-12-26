// [>]: Player ELO history endpoint.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  getNumericParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getPlayerEloHistory } from "@/lib/services/players";

type PlayerRouteContext = RouteContext<"playerId">;

// [>]: GET /api/v1/players/[playerId]/elo-history - get player's ELO history.
export const GET = handleApiRequest(
  async (request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");
    const { searchParams } = new URL(request.url);

    const limit = getNumericParam(searchParams, "limit", 20);
    const offset = getNumericParam(searchParams, "offset", 0);

    const history = await getPlayerEloHistory(id, { limit, offset });

    return NextResponse.json(history);
  },
);
