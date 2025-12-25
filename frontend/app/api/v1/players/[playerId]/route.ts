// [>]: Single player endpoints: GET, PUT, DELETE.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import {
  getPlayer,
  updateExistingPlayer,
  deletePlayer,
} from "@/lib/services/players";
import { PlayerUpdateSchema } from "@/lib/types/schemas/player";

type PlayerRouteContext = RouteContext<"playerId">;

// [>]: GET /api/v1/players/[playerId] - get player with stats.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");
    const player = await getPlayer(id);
    return NextResponse.json(player);
  },
);

// [>]: PUT /api/v1/players/[playerId] - update player.
export const PUT = handleApiRequest(
  async (request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");
    const body = await request.json();
    const validated = PlayerUpdateSchema.parse(body);
    const player = await updateExistingPlayer(id, validated);
    return NextResponse.json(player);
  },
);

// [>]: DELETE /api/v1/players/[playerId] - delete player.
export const DELETE = handleApiRequest(
  async (_request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");
    await deletePlayer(id);
    return new NextResponse(null, { status: 204 });
  },
);
