// [>]: Match service - orchestrates match creation with ELO updates.
// This is the most complex service, coordinating multiple repositories and the ELO service.

import {
  createMatchByTeamIds,
  getMatchById,
  getAllMatches as getAllMatchesRepo,
  getMatchesByTeamId as getMatchesByTeamIdRepo,
  getMatchesByPlayerId as getMatchesByPlayerIdRepo,
  deleteMatchById,
} from "@/lib/db/repositories/matches";
import { batchUpdatePlayersElo } from "@/lib/db/repositories/players";
import { batchUpdateTeamsElo } from "@/lib/db/repositories/teams";
import {
  batchRecordPlayerEloUpdates,
  getPlayersEloHistoryByMatchId,
  deletePlayerEloHistoryByMatchId,
} from "@/lib/db/repositories/player-elo-history";
import {
  batchRecordTeamEloUpdates,
  getTeamsEloHistoryByMatchId,
  deleteTeamEloHistoryByMatchId,
} from "@/lib/db/repositories/team-elo-history";
import { getTeam } from "@/lib/services/teams";
import { processMatchResult, type TeamWithPlayers } from "@/lib/services/elo";
import {
  InvalidMatchTeamsError,
  MatchCreationError,
} from "@/lib/errors/api-errors";
import { mapToMatchResponse } from "@/lib/mappers/entity-mappers";
import type {
  MatchCreate,
  MatchResponse,
  MatchWithEloResponse,
} from "@/lib/types/schemas/match";

// [>]: Query options for match filtering.
interface MatchQueryOptions {
  skip?: number;
  limit?: number;
  teamId?: number;
  startDate?: string;
  endDate?: string;
  isFanny?: boolean;
}

// [>]: Get a match by ID with team details.
export async function getMatch(matchId: number): Promise<MatchResponse> {
  const matchData = await getMatchById(matchId);

  // [>]: Fetch team details.
  const [winnerTeam, loserTeam] = await Promise.all([
    getTeam(matchData.winner_team_id),
    getTeam(matchData.loser_team_id),
  ]);

  return {
    match_id: matchData.match_id,
    winner_team_id: matchData.winner_team_id,
    loser_team_id: matchData.loser_team_id,
    is_fanny: matchData.is_fanny,
    played_at: matchData.played_at,
    notes: matchData.notes ?? null,
    winner_team: winnerTeam,
    loser_team: loserTeam,
  };
}

// [>]: Get matches with optional filtering.
export async function getMatches(
  options: MatchQueryOptions = {},
): Promise<MatchResponse[]> {
  const {
    skip = 0,
    limit = 100,
    teamId,
    startDate,
    endDate,
    isFanny,
  } = options;

  let matchesData;
  if (teamId) {
    matchesData = await getMatchesByTeamIdRepo(teamId, {
      limit,
      offset: skip,
      startDate,
      endDate,
      isFanny,
    });
  } else {
    matchesData = await getAllMatchesRepo(limit, skip);
  }

  // [>]: Map to response format (RPC already includes team data).
  return matchesData.map(mapToMatchResponse);
}

// [>]: Get matches for a specific player.
export async function getMatchesByPlayer(
  playerId: number,
  options: Omit<MatchQueryOptions, "teamId"> = {},
): Promise<MatchResponse[]> {
  const { skip = 0, limit = 100, startDate, endDate, isFanny } = options;

  const matchesData = await getMatchesByPlayerIdRepo(playerId, {
    limit,
    offset: skip,
    startDate,
    endDate,
    isFanny,
  });

  return matchesData.map(mapToMatchResponse);
}

// [>]: Create a new match with full ELO processing.
// Orchestration steps:
// 1. Validate winner !== loser
// 2. Fetch both teams with players
// 3. Create match record
// 4. Calculate ELO changes (uses elo.ts)
// 5. Batch update player ELOs
// 6. Batch update team ELOs
// 7. Record player ELO history
// 8. Record team ELO history
// 9. Return match with ELO changes
export async function createNewMatch(
  data: MatchCreate,
): Promise<MatchWithEloResponse> {
  // [>]: Step 1: Validate teams are different.
  if (data.winner_team_id === data.loser_team_id) {
    throw new InvalidMatchTeamsError(
      "Winner and loser teams cannot be the same",
    );
  }

  try {
    // [>]: Step 2: Get team details with players.
    const [winnerTeamData, loserTeamData] = await Promise.all([
      getTeam(data.winner_team_id),
      getTeam(data.loser_team_id),
    ]);

    // [>]: Prepare teams for ELO calculation (requires player data).
    if (!winnerTeamData.player1 || !winnerTeamData.player2) {
      throw new MatchCreationError("Winner team players not found");
    }
    if (!loserTeamData.player1 || !loserTeamData.player2) {
      throw new MatchCreationError("Loser team players not found");
    }

    const winningTeam: TeamWithPlayers = {
      team_id: winnerTeamData.team_id,
      global_elo: winnerTeamData.global_elo,
      player1: {
        player_id: winnerTeamData.player1.player_id,
        global_elo: winnerTeamData.player1.global_elo,
      },
      player2: {
        player_id: winnerTeamData.player2.player_id,
        global_elo: winnerTeamData.player2.global_elo,
      },
    };

    const losingTeam: TeamWithPlayers = {
      team_id: loserTeamData.team_id,
      global_elo: loserTeamData.global_elo,
      player1: {
        player_id: loserTeamData.player1.player_id,
        global_elo: loserTeamData.player1.global_elo,
      },
      player2: {
        player_id: loserTeamData.player2.player_id,
        global_elo: loserTeamData.player2.global_elo,
      },
    };

    // [>]: Step 3: Create match record.
    const matchId = await createMatchByTeamIds(
      data.winner_team_id,
      data.loser_team_id,
      data.played_at,
      data.is_fanny,
      data.notes ?? undefined,
    );

    // [>]: Step 4: Calculate ELO changes.
    const [playersChange, teamsChange] = processMatchResult(
      winningTeam,
      losingTeam,
    );

    // [>]: Step 5: Batch update player ELOs.
    const playerUpdates = Object.entries(playersChange).map(
      ([playerIdStr, change]) => ({
        player_id: Number(playerIdStr),
        global_elo: change.new_elo,
      }),
    );
    await batchUpdatePlayersElo(playerUpdates);

    // [>]: Step 6: Record player ELO history.
    const playerHistoryUpdates = Object.entries(playersChange).map(
      ([playerIdStr, change]) => ({
        player_id: Number(playerIdStr),
        match_id: matchId,
        old_elo: change.old_elo,
        new_elo: change.new_elo,
        date: data.played_at,
      }),
    );
    await batchRecordPlayerEloUpdates(playerHistoryUpdates);

    // [>]: Step 7: Batch update team ELOs.
    const teamUpdates = Object.entries(teamsChange).map(
      ([teamIdStr, change]) => ({
        team_id: Number(teamIdStr),
        global_elo: change.new_elo,
        last_match_at: data.played_at,
      }),
    );
    await batchUpdateTeamsElo(teamUpdates);

    // [>]: Step 8: Record team ELO history.
    const teamHistoryUpdates = Object.entries(teamsChange).map(
      ([teamIdStr, change]) => ({
        team_id: Number(teamIdStr),
        match_id: matchId,
        old_elo: change.old_elo,
        new_elo: change.new_elo,
        date: data.played_at,
      }),
    );
    await batchRecordTeamEloUpdates(teamHistoryUpdates);

    // [>]: Step 9: Prepare and return response.
    // Convert playersChange to Record<string, EloChange> for response.
    const eloChanges: Record<
      string,
      { old_elo: number; new_elo: number; difference: number }
    > = {};
    for (const [playerIdStr, change] of Object.entries(playersChange)) {
      eloChanges[playerIdStr] = {
        old_elo: change.old_elo,
        new_elo: change.new_elo,
        difference: change.difference,
      };
    }

    return {
      match_id: matchId,
      winner_team_id: data.winner_team_id,
      loser_team_id: data.loser_team_id,
      is_fanny: data.is_fanny,
      played_at: data.played_at,
      notes: data.notes ?? null,
      winner_team: winnerTeamData,
      loser_team: loserTeamData,
      elo_changes: eloChanges,
    };
  } catch (error) {
    if (
      error instanceof InvalidMatchTeamsError ||
      error instanceof MatchCreationError
    ) {
      throw error;
    }
    throw new MatchCreationError(
      `Failed to create match: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

// [>]: Get match with player ELO changes.
export async function getMatchWithPlayerElo(
  matchId: number,
): Promise<MatchWithEloResponse> {
  const matchData = await getMatchById(matchId);

  // [>]: Get ELO history for this match.
  const eloHistory = await getPlayersEloHistoryByMatchId(matchId);

  // [>]: Fetch team details.
  const [winnerTeam, loserTeam] = await Promise.all([
    getTeam(matchData.winner_team_id),
    getTeam(matchData.loser_team_id),
  ]);

  // [>]: Build elo_changes map.
  const eloChanges: Record<
    string,
    { old_elo: number; new_elo: number; difference: number }
  > = {};
  for (const eh of eloHistory) {
    eloChanges[String(eh.player_id)] = {
      old_elo: eh.old_elo,
      new_elo: eh.new_elo,
      difference: eh.difference,
    };
  }

  return {
    match_id: matchData.match_id,
    winner_team_id: matchData.winner_team_id,
    loser_team_id: matchData.loser_team_id,
    is_fanny: matchData.is_fanny,
    played_at: matchData.played_at,
    notes: matchData.notes ?? null,
    winner_team: winnerTeam,
    loser_team: loserTeam,
    elo_changes: eloChanges,
  };
}

// [>]: Get match with team ELO changes.
export async function getMatchWithTeamElo(
  matchId: number,
): Promise<MatchWithEloResponse> {
  const matchData = await getMatchById(matchId);

  // [>]: Get team ELO history for this match.
  const eloHistory = await getTeamsEloHistoryByMatchId(matchId);

  // [>]: Fetch team details.
  const [winnerTeam, loserTeam] = await Promise.all([
    getTeam(matchData.winner_team_id),
    getTeam(matchData.loser_team_id),
  ]);

  // [>]: Build elo_changes map.
  const eloChanges: Record<
    string,
    { old_elo: number; new_elo: number; difference: number }
  > = {};
  for (const eh of eloHistory) {
    eloChanges[String(eh.team_id)] = {
      old_elo: eh.old_elo,
      new_elo: eh.new_elo,
      difference: eh.difference,
    };
  }

  return {
    match_id: matchData.match_id,
    winner_team_id: matchData.winner_team_id,
    loser_team_id: matchData.loser_team_id,
    is_fanny: matchData.is_fanny,
    played_at: matchData.played_at,
    notes: matchData.notes ?? null,
    winner_team: winnerTeam,
    loser_team: loserTeam,
    elo_changes: eloChanges,
  };
}

// [>]: Delete a match.
// [!]: Does not reverse ELO changes (matches Python behavior).
export async function deleteMatch(matchId: number): Promise<void> {
  // [>]: Verify match exists (throws MatchNotFoundError if not).
  await getMatchById(matchId);

  // [>]: Delete ELO history records first to avoid FK constraint violations.
  await Promise.all([
    deletePlayerEloHistoryByMatchId(matchId),
    deleteTeamEloHistoryByMatchId(matchId),
  ]);

  // [>]: Delete the match.
  await deleteMatchById(matchId);
}
