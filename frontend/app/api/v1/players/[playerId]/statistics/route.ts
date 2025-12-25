// [>]: Player statistics endpoint.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getPlayer, getPlayerEloHistory } from "@/lib/services/players";

type PlayerRouteContext = RouteContext<"playerId">;

// [>]: GET /api/v1/players/[playerId]/statistics - get detailed player stats.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: PlayerRouteContext) => {
    const { playerId } = await context!.params;
    const id = parseIdParam(playerId, "playerId");

    // [>]: Get player with basic stats.
    const player = await getPlayer(id);

    // [>]: Get ELO history for computing additional stats.
    const history = await getPlayerEloHistory(id, { limit: 1000 });

    // [>]: Calculate additional statistics.
    let highestElo = player.global_elo;
    let lowestElo = player.global_elo;
    let totalEloChange = 0;

    for (const entry of history) {
      if (entry.new_elo > highestElo) highestElo = entry.new_elo;
      if (entry.new_elo < lowestElo) lowestElo = entry.new_elo;
      totalEloChange += entry.difference;
    }

    const averageEloChange =
      history.length > 0 ? Math.trunc(totalEloChange / history.length) : 0;

    return NextResponse.json({
      player_id: player.player_id,
      name: player.name,
      global_elo: player.global_elo,
      matches_played: player.matches_played,
      wins: player.wins,
      losses: player.losses,
      win_rate: player.win_rate,
      average_elo_change: averageEloChange,
      highest_elo: highestElo,
      lowest_elo: lowestElo,
    });
  },
);
