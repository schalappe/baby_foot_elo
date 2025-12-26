// [>]: Match repository - all database operations for matches table.
// Uses RPC functions for complex queries with team/player data.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import {
  MatchNotFoundError,
  MatchCreationError,
  MatchOperationError,
  MatchDeletionError,
} from "@/lib/errors/api-errors";

// [>]: Database row type for raw Supabase responses.
interface MatchDbRow {
  match_id: number;
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  notes?: string | null;
}

// [>]: Extended row type with team details from RPC.
interface MatchWithTeamsRow extends MatchDbRow {
  winner_team?: {
    team_id: number;
    player1_id: number;
    player2_id: number;
    global_elo: number;
  } | null;
  loser_team?: {
    team_id: number;
    player1_id: number;
    player2_id: number;
    global_elo: number;
  } | null;
  // [>]: ELO changes keyed by player ID (from get_player_matches_json RPC).
  elo_changes?: Record<
    string,
    { old_elo: number; new_elo: number; difference: number }
  > | null;
}

// [>]: Query options for match filtering.
interface MatchQueryOptions {
  limit?: number;
  offset?: number;
  isFanny?: boolean;
  startDate?: string;
  endDate?: string;
}

// [>]: Create a new match record. Returns the match_id.
// Does NOT update ELOs - that is the service layer's responsibility.
async function createMatchByTeamIdsImpl(
  winnerTeamId: number,
  loserTeamId: number,
  playedAt: string,
  isFanny: boolean = false,
  notes?: string,
): Promise<number> {
  const client = getSupabaseClient();

  const matchData: Record<string, unknown> = {
    winner_team_id: winnerTeamId,
    loser_team_id: loserTeamId,
    played_at: playedAt,
    is_fanny: isFanny,
  };

  if (notes) {
    matchData.notes = notes;
  }

  const { data, error } = await client
    .from("matches")
    .insert(matchData)
    .select("match_id")
    .single();

  if (error) {
    throw new MatchCreationError(`Failed to create match: ${error.message}`);
  }

  if (!data?.match_id) {
    throw new MatchCreationError("Failed to create match: no ID returned");
  }

  return data.match_id;
}

// [>]: Lookup match by ID. Throws MatchNotFoundError if not found.
async function getMatchByIdImpl(matchId: number): Promise<MatchDbRow> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("matches")
    .select(
      "match_id, winner_team_id, loser_team_id, is_fanny, played_at, notes",
    )
    .eq("match_id", matchId)
    .maybeSingle();

  if (error) {
    throw new MatchOperationError(`Database error: ${error.message}`);
  }

  if (!data) {
    throw new MatchNotFoundError(matchId);
  }

  return data;
}

// [>]: Get all matches with pagination and optional filters (uses RPC for joined data).
async function getAllMatchesImpl(
  options: MatchQueryOptions = {},
): Promise<MatchWithTeamsRow[]> {
  const { limit = 100, offset = 0, startDate, endDate, isFanny } = options;
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_all_matches_with_details", {
    p_limit: limit,
    p_offset: offset,
    p_start_date: startDate ?? null,
    p_end_date: endDate ?? null,
    p_is_fanny: isFanny ?? null,
  });

  if (error) {
    throw new MatchOperationError(
      `Failed to get all matches: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Get matches filtered by team ID (uses RPC).
async function getMatchesByTeamIdImpl(
  teamId: number,
  options: MatchQueryOptions = {},
): Promise<MatchWithTeamsRow[]> {
  const { limit = 100, offset = 0, isFanny, startDate, endDate } = options;
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_team_match_history", {
    p_team_id: teamId,
    p_limit: limit,
    p_offset: offset,
    p_is_fanny: isFanny ?? null,
    p_start_date: startDate ?? null,
    p_end_date: endDate ?? null,
  });

  if (error) {
    throw new MatchOperationError(
      `Failed to get matches for team: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Get matches filtered by player ID (uses RPC).
async function getMatchesByPlayerIdImpl(
  playerId: number,
  options: MatchQueryOptions = {},
): Promise<MatchWithTeamsRow[]> {
  const { limit = 100, offset = 0, isFanny, startDate, endDate } = options;
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_player_matches_json", {
    p_player_id: playerId,
    p_limit: limit,
    p_offset: offset,
    p_is_fanny: isFanny ?? null,
    p_start_date: startDate ?? null,
    p_end_date: endDate ?? null,
  });

  if (error) {
    throw new MatchOperationError(
      `Failed to get matches for player: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Delete match by ID. Throws MatchNotFoundError if not found.
async function deleteMatchByIdImpl(matchId: number): Promise<void> {
  const client = getSupabaseClient();

  const { count, error } = await client
    .from("matches")
    .delete({ count: "exact" })
    .eq("match_id", matchId);

  if (error) {
    throw new MatchDeletionError(`Failed to delete match: ${error.message}`);
  }

  if (count === 0) {
    throw new MatchNotFoundError(matchId);
  }
}

// [>]: Export wrapped functions with retry logic.
export const createMatchByTeamIds = withRetry(createMatchByTeamIdsImpl);
export const getMatchById = withRetry(getMatchByIdImpl);
export const getAllMatches = withRetry(getAllMatchesImpl);
export const getMatchesByTeamId = withRetry(getMatchesByTeamIdImpl);
export const getMatchesByPlayerId = withRetry(getMatchesByPlayerIdImpl);
export const deleteMatchById = withRetry(deleteMatchByIdImpl);

// [>]: Export types for use in services.
export type { MatchDbRow, MatchWithTeamsRow, MatchQueryOptions };
