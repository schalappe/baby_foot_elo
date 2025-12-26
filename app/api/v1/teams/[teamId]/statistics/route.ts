// [>]: Team statistics endpoint.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getTeam } from "@/lib/services/teams";
import { getTeamEloHistory } from "@/lib/db/repositories/team-elo-history";

type TeamRouteContext = RouteContext<"teamId">;

const RECENT_MATCHES_COUNT = 10;

// [>]: GET /api/v1/teams/[teamId]/statistics - get detailed team stats.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: TeamRouteContext) => {
    const { teamId } = await context!.params;
    const id = parseIdParam(teamId, "teamId");

    // [>]: Get team with basic stats.
    const team = await getTeam(id);

    // [>]: Get ELO history for chart display (last 100 matches).
    // [>]: History is ordered by date DESC (most recent first).
    const history = await getTeamEloHistory(id, { limit: 100 });

    // [>]: Calculate additional statistics.
    let highestElo = team.global_elo;
    let lowestElo = team.global_elo;
    let totalEloChange = 0;

    // [>]: Build arrays for charts (history is DESC, so reverse for chronological order).
    const eloValues: number[] = [];
    const eloDifference: number[] = [];

    for (const entry of history) {
      if (entry.new_elo > highestElo) highestElo = entry.new_elo;
      if (entry.new_elo < lowestElo) lowestElo = entry.new_elo;
      totalEloChange += entry.difference;
      eloValues.push(entry.new_elo);
      eloDifference.push(entry.difference);
    }

    const averageEloChange =
      history.length > 0 ? Math.trunc(totalEloChange / history.length) : 0;

    // [>]: Calculate recent stats (last N matches).
    const recentHistory = history.slice(0, RECENT_MATCHES_COUNT);
    const recentWins = recentHistory.filter((h) => h.difference > 0).length;
    const recentLosses = recentHistory.filter((h) => h.difference < 0).length;
    const recentMatchesPlayed = recentHistory.length;
    // [>]: Calculate win rate as decimal (0-1) for consistency with other stats.
    const recentWinRate =
      recentMatchesPlayed > 0 ? recentWins / recentMatchesPlayed : 0;
    const recentTotalChange = recentHistory.reduce(
      (sum, h) => sum + h.difference,
      0,
    );
    const recentAverageEloChange =
      recentMatchesPlayed > 0
        ? Math.trunc(recentTotalChange / recentMatchesPlayed)
        : 0;

    return NextResponse.json({
      team_id: team.team_id,
      player1_id: team.player1_id,
      player2_id: team.player2_id,
      player1: team.player1,
      player2: team.player2,
      global_elo: team.global_elo,
      total_matches: team.matches_played,
      matches_played: team.matches_played,
      wins: team.wins,
      losses: team.losses,
      win_rate: team.win_rate,
      elo_values: eloValues,
      elo_difference: eloDifference,
      average_elo_change: averageEloChange,
      highest_elo: highestElo,
      lowest_elo: lowestElo,
      created_at: team.created_at,
      last_match_at: team.last_match_at,
      recent: {
        matches_played: recentMatchesPlayed,
        wins: recentWins,
        losses: recentLosses,
        win_rate: recentWinRate,
        average_elo_change: recentAverageEloChange,
        elo_changes: recentHistory.map((h) => h.difference),
      },
    });
  },
);
