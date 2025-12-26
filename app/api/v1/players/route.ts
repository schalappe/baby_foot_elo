// [>]: Player collection endpoints: GET list, POST create.

import { NextRequest, NextResponse } from "next/server";

import { handleApiRequest, getNumericParam } from "@/lib/api/handle-request";
import {
  getAllPlayersWithStats,
  createNewPlayer,
} from "@/lib/services/players";
import { PlayerCreateSchema } from "@/lib/types/schemas/player";

// [>]: GET /api/v1/players - list all players with stats.
export const GET = handleApiRequest(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);
  const limit = getNumericParam(searchParams, "limit", 50);
  const skip = getNumericParam(searchParams, "skip", 0);

  const players = await getAllPlayersWithStats();

  // [>]: Apply pagination in-memory (service returns all players).
  const paginated = players.slice(skip, skip + limit);
  return NextResponse.json(paginated);
});

// [>]: POST /api/v1/players - create new player.
export const POST = handleApiRequest(async (request: NextRequest) => {
  const body = await request.json();
  const validated = PlayerCreateSchema.parse(body);
  const player = await createNewPlayer(validated);
  return NextResponse.json(player, { status: 201 });
});
