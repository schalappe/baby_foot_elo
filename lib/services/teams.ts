// [>]: Team service - business logic layer for team operations.
// Orchestrates repositories and applies validation rules.

import {
  createTeamByPlayerIds,
  getAllTeams,
  getActiveTeamsWithStats,
  getTeamsByPlayerId as getTeamsByPlayerIdRepo,
  updateTeam,
  deleteTeamById,
} from "@/lib/db/repositories/teams";
import { getPlayerById } from "@/lib/db/repositories/players";
import { getTeamStats } from "@/lib/db/repositories/stats";
import {
  InvalidTeamDataError,
  TeamOperationError,
  PlayerNotFoundError,
} from "@/lib/errors/api-errors";
import { mapToTeamResponse } from "@/lib/mappers/entity-mappers";
import type {
  TeamCreate,
  TeamUpdate,
  TeamResponse,
} from "@/lib/types/schemas/team";

// [>]: Get a team by ID with full stats.
// Uses stats repository for computed fields and player details.
export async function getTeam(teamId: number): Promise<TeamResponse> {
  const stats = await getTeamStats(teamId);
  return mapToTeamResponse(stats);
}

// [>]: Get all teams with stats for ranking display.
export async function getAllTeamsWithStats(options?: {
  skip?: number;
  limit?: number;
}): Promise<TeamResponse[]> {
  const { skip = 0, limit = 100 } = options ?? {};
  const teams = await getAllTeams(limit, skip);
  return teams.map(mapToTeamResponse);
}

// [>]: Get all teams containing a specific player.
export async function getTeamsByPlayer(
  playerId: number,
): Promise<TeamResponse[]> {
  // [>]: Get basic team data.
  const teams = await getTeamsByPlayerIdRepo(playerId);

  // [>]: Enrich each team with full stats.
  const enrichedTeams: TeamResponse[] = [];
  for (const team of teams) {
    try {
      const fullTeam = await getTeam(team.team_id);
      enrichedTeams.push(fullTeam);
    } catch {
      // [>]: If getTeam fails, skip this team (rare edge case).
      continue;
    }
  }

  return enrichedTeams;
}

// [>]: Create a new team.
// Validates both players exist.
export async function createNewTeam(data: TeamCreate): Promise<TeamResponse> {
  try {
    // [>]: Validate both players exist.
    const [player1, player2] = await Promise.all([
      getPlayerById(data.player1_id).catch(() => null),
      getPlayerById(data.player2_id).catch(() => null),
    ]);

    const missingPlayers: string[] = [];
    if (!player1) {
      missingPlayers.push(String(data.player1_id));
    }
    if (!player2) {
      missingPlayers.push(String(data.player2_id));
    }

    if (missingPlayers.length > 0) {
      throw new InvalidTeamDataError(
        `Players not found: ${missingPlayers.join(", ")}`,
      );
    }

    // [>]: Create the team (handles deduplication and ordering).
    const teamId = await createTeamByPlayerIds(
      data.player1_id,
      data.player2_id,
      data.global_elo,
    );

    // [>]: Return the created team with full details.
    return await getTeam(teamId);
  } catch (error) {
    if (
      error instanceof InvalidTeamDataError ||
      error instanceof PlayerNotFoundError
    ) {
      throw error;
    }
    throw new TeamOperationError(
      `Failed to create team: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

// [>]: Update an existing team.
export async function updateExistingTeam(
  teamId: number,
  data: TeamUpdate,
): Promise<TeamResponse> {
  // [>]: Verify team exists (throws TeamNotFoundError if not).
  await getTeam(teamId);

  // [>]: Update the team.
  await updateTeam(teamId, {
    global_elo: data.global_elo,
    last_match_at: data.last_match_at,
  });

  return await getTeam(teamId);
}

// [>]: Delete a team.
export async function deleteTeam(teamId: number): Promise<void> {
  // [>]: Verify team exists (throws TeamNotFoundError if not).
  await getTeam(teamId);

  // [>]: Delete the team.
  await deleteTeamById(teamId);
}

// [>]: Minimum matches required to appear in rankings.
const MIN_MATCHES_FOR_RANKING = 10;

// [>]: Get active teams for rankings display.
// Active = has more than MIN_MATCHES_FOR_RANKING matches AND last match within daysSinceLastMatch days.
// Filtering is now done in SQL for performance.
export async function getActiveTeamRankings(options?: {
  daysSinceLastMatch?: number;
}): Promise<TeamResponse[]> {
  const { daysSinceLastMatch = 180 } = options ?? {};

  // [>]: Fetch pre-filtered teams from optimized batch RPC.
  // Filtering by minMatches and daysSinceLastMatch is now done in SQL.
  const teams = await getActiveTeamsWithStats({
    daysSinceLastMatch,
    minMatches: MIN_MATCHES_FOR_RANKING,
  });

  return teams.map(mapToTeamResponse);
}
