// [>]: Team repository - all database operations for teams table.
// Normalizes player order (player1_id < player2_id) for uniqueness.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import { TeamNotFoundError, TeamOperationError } from "@/lib/errors/api-errors";

// [>]: Database row type for raw Supabase responses.
interface TeamDbRow {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
}

// [>]: Extended row type with computed stats from RPC.
interface TeamWithStatsRow extends TeamDbRow {
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  rank?: number;
  player1?: {
    player_id: number;
    name: string;
    global_elo: number;
  } | null;
  player2?: {
    player_id: number;
    name: string;
    global_elo: number;
  } | null;
}

// [>]: Normalize player IDs to canonical order (player1_id < player2_id).
function normalizePlayerIds(
  player1Id: number,
  player2Id: number,
): [number, number] {
  return player1Id < player2Id
    ? [player1Id, player2Id]
    : [player2Id, player1Id];
}

// [>]: Create a new team. Normalizes player order.
// Returns existing team_id if duplicate found.
async function createTeamByPlayerIdsImpl(
  player1Id: number,
  player2Id: number,
  globalElo: number = 1000,
): Promise<number> {
  const [p1, p2] = normalizePlayerIds(player1Id, player2Id);
  const client = getSupabaseClient();

  // [>]: Check for existing team first.
  const { data: existing } = await client
    .from("teams")
    .select("team_id")
    .eq("player1_id", p1)
    .eq("player2_id", p2)
    .maybeSingle();

  if (existing?.team_id) {
    return existing.team_id;
  }

  // [>]: Create new team.
  const { data, error } = await client
    .from("teams")
    .insert({ player1_id: p1, player2_id: p2, global_elo: globalElo })
    .select("team_id")
    .single();

  if (error) {
    throw new TeamOperationError(`Failed to create team: ${error.message}`);
  }

  if (!data?.team_id) {
    throw new TeamOperationError("Failed to create team: no ID returned");
  }

  return data.team_id;
}

// [>]: Lookup team by ID. Throws TeamNotFoundError if not found.
async function getTeamByIdImpl(teamId: number): Promise<TeamDbRow> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("teams")
    .select(
      "team_id, player1_id, player2_id, global_elo, created_at, last_match_at",
    )
    .eq("team_id", teamId)
    .maybeSingle();

  if (error) {
    throw new TeamOperationError(`Database error: ${error.message}`);
  }

  if (!data) {
    throw new TeamNotFoundError(teamId);
  }

  return data;
}

// [>]: Lookup team by player pair. Normalizes order internally.
async function getTeamByPlayerIdsImpl(
  player1Id: number,
  player2Id: number,
): Promise<TeamDbRow | null> {
  const [p1, p2] = normalizePlayerIds(player1Id, player2Id);
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("teams")
    .select(
      "team_id, player1_id, player2_id, global_elo, created_at, last_match_at",
    )
    .eq("player1_id", p1)
    .eq("player2_id", p2)
    .maybeSingle();

  if (error) {
    throw new TeamOperationError(`Database error: ${error.message}`);
  }

  return data;
}

// [>]: Get all teams with computed stats (uses RPC).
async function getAllTeamsImpl(
  limit: number = 100,
  offset: number = 0,
): Promise<TeamWithStatsRow[]> {
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_all_teams_with_stats", {
    p_skip: offset,
    p_limit: limit,
  });

  if (error) {
    throw new TeamOperationError(`Failed to get all teams: ${error.message}`);
  }

  return data ?? [];
}

// [>]: Get all teams containing a specific player.
async function getTeamsByPlayerIdImpl(playerId: number): Promise<TeamDbRow[]> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("teams")
    .select(
      "team_id, player1_id, player2_id, global_elo, created_at, last_match_at",
    )
    .or(`player1_id.eq.${playerId},player2_id.eq.${playerId}`)
    .order("last_match_at", { ascending: false, nullsFirst: false });

  if (error) {
    throw new TeamOperationError(
      `Failed to get teams for player: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Update team fields. Throws TeamNotFoundError if team does not exist.
async function updateTeamImpl(
  teamId: number,
  updates: { global_elo?: number; last_match_at?: string },
): Promise<void> {
  if (updates.global_elo === undefined && updates.last_match_at === undefined) {
    return;
  }

  const client = getSupabaseClient();

  const updateFields: Record<string, unknown> = {};
  if (updates.global_elo !== undefined) {
    updateFields.global_elo = updates.global_elo;
  }
  if (updates.last_match_at !== undefined) {
    updateFields.last_match_at = updates.last_match_at;
  }

  const { data, error } = await client
    .from("teams")
    .update(updateFields)
    .eq("team_id", teamId)
    .select("team_id");

  if (error) {
    throw new TeamOperationError(`Failed to update team: ${error.message}`);
  }

  if (!data || data.length === 0) {
    throw new TeamNotFoundError(teamId);
  }
}

// [>]: Batch update team ELOs and last_match_at. Used after match processing.
async function batchUpdateTeamsEloImpl(
  updates: Array<{
    team_id: number;
    global_elo: number;
    last_match_at?: string;
  }>,
): Promise<void> {
  if (updates.length === 0) {
    return;
  }

  const client = getSupabaseClient();

  for (const { team_id, global_elo, last_match_at } of updates) {
    const updateFields: Record<string, unknown> = { global_elo };
    if (last_match_at) {
      updateFields.last_match_at = last_match_at;
    }

    const { error } = await client
      .from("teams")
      .update(updateFields)
      .eq("team_id", team_id);

    if (error) {
      throw new TeamOperationError(
        `Failed to update team ${team_id} ELO: ${error.message}`,
      );
    }
  }
}

// [>]: Delete team by ID. Throws TeamNotFoundError if not found.
async function deleteTeamByIdImpl(teamId: number): Promise<void> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("teams")
    .delete()
    .eq("team_id", teamId)
    .select("team_id");

  if (error) {
    throw new TeamOperationError(`Failed to delete team: ${error.message}`);
  }

  if (!data || data.length === 0) {
    throw new TeamNotFoundError(teamId);
  }
}

// [>]: Get all teams that have played at least one match.
// Uses optimized batch RPC that pre-aggregates stats in SQL.
async function getActiveTeamsWithStatsImpl(options?: {
  daysSinceLastMatch?: number;
  minMatches?: number;
}): Promise<TeamWithStatsRow[]> {
  const { daysSinceLastMatch = 180, minMatches = 10 } = options ?? {};
  const client = getSupabaseClient();

  // [>]: Single RPC call replaces N+1 loop - 1000x faster.
  const { data, error } = await client.rpc(
    "get_active_teams_with_stats_batch",
    {
      p_days_since_last_match: daysSinceLastMatch,
      p_min_matches: minMatches,
    },
  );

  if (error) {
    throw new TeamOperationError(
      `Failed to get active teams: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Export wrapped functions with retry logic.
export const createTeamByPlayerIds = withRetry(createTeamByPlayerIdsImpl);
export const getTeamById = withRetry(getTeamByIdImpl);
export const getTeamByPlayerIds = withRetry(getTeamByPlayerIdsImpl);
export const getAllTeams = withRetry(getAllTeamsImpl);
export const getTeamsByPlayerId = withRetry(getTeamsByPlayerIdImpl);
export const updateTeam = withRetry(updateTeamImpl);
export const batchUpdateTeamsElo = withRetry(batchUpdateTeamsEloImpl);
export const deleteTeamById = withRetry(deleteTeamByIdImpl);
export const getActiveTeamsWithStats = withRetry(getActiveTeamsWithStatsImpl);

// [>]: Export types for use in services.
export type { TeamDbRow, TeamWithStatsRow };
