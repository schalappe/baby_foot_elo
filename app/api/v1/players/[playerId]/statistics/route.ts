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
    // History is ordered by date DESC (newest first).
    const history = await getPlayerEloHistory(id, { limit: 1000 });

    // [>]: Extract ELO values and differences from history.
    const eloValues = history.map((entry) => entry.new_elo);
    const eloDifference = history.map((entry) => entry.difference);

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

    // [>]: Calculate recent stats from last 10 matches.
    const recentHistory = history.slice(0, 10);
    let recentWins = 0;
    let recentLosses = 0;
    const recentEloChanges: number[] = [];

    for (const entry of recentHistory) {
      recentEloChanges.push(entry.difference);
      if (entry.difference > 0) recentWins++;
      else if (entry.difference < 0) recentLosses++;
    }

    const recentMatchesPlayed = recentWins + recentLosses;
    // [>]: Calculate win rate as decimal (0-1) for consistency with other stats.
    const recentWinRate =
      recentMatchesPlayed > 0 ? recentWins / recentMatchesPlayed : 0;
    const recentAvgEloChange =
      recentEloChanges.length > 0
        ? recentEloChanges.reduce((a, b) => a + b, 0) / recentEloChanges.length
        : 0;

    return NextResponse.json({
      player_id: player.player_id,
      name: player.name,
      global_elo: player.global_elo,
      matches_played: player.matches_played,
      wins: player.wins,
      losses: player.losses,
      win_rate: player.win_rate,
      elo_values: eloValues,
      elo_difference: eloDifference,
      average_elo_change: averageEloChange,
      highest_elo: highestElo,
      lowest_elo: lowestElo,
      creation_date: player.created_at,
      recent: {
        matches_played: recentMatchesPlayed,
        wins: recentWins,
        losses: recentLosses,
        win_rate: recentWinRate,
        average_elo_change: Math.round(recentAvgEloChange * 100) / 100,
        elo_changes: recentEloChanges,
      },
    });
  },
);
