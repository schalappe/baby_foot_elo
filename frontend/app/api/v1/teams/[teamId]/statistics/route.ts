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

// [>]: GET /api/v1/teams/[teamId]/statistics - get detailed team stats.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: TeamRouteContext) => {
    const { teamId } = await context!.params;
    const id = parseIdParam(teamId, "teamId");

    // [>]: Get team with basic stats.
    const team = await getTeam(id);

    // [>]: Get ELO history for computing additional stats.
    const history = await getTeamEloHistory(id, { limit: 1000 });

    // [>]: Calculate additional statistics.
    let highestElo = team.global_elo;
    let lowestElo = team.global_elo;
    let totalEloChange = 0;

    for (const entry of history) {
      if (entry.new_elo > highestElo) highestElo = entry.new_elo;
      if (entry.new_elo < lowestElo) lowestElo = entry.new_elo;
      totalEloChange += entry.difference;
    }

    const averageEloChange =
      history.length > 0 ? Math.trunc(totalEloChange / history.length) : 0;

    return NextResponse.json({
      team_id: team.team_id,
      player1_id: team.player1_id,
      player2_id: team.player2_id,
      player1: team.player1,
      player2: team.player2,
      global_elo: team.global_elo,
      matches_played: team.matches_played,
      wins: team.wins,
      losses: team.losses,
      win_rate: team.win_rate,
      average_elo_change: averageEloChange,
      highest_elo: highestElo,
      lowest_elo: lowestElo,
    });
  },
);
