// [>]: Stats repository - RPC calls for aggregated statistics.
// Uses Supabase SQL functions for computed player and team stats.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import {
  PlayerNotFoundError,
  TeamNotFoundError,
  OperationError,
} from "@/lib/errors/api-errors";

// [>]: Full stats row type for player RPC response.
interface PlayerStatsRow {
  player_id: number;
  name: string;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  rank?: number;
}

// [>]: Full stats row type for team RPC response.
interface TeamStatsRow {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
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

// [>]: Get full stats for a single player (RPC: get_player_full_stats).
// Throws PlayerNotFoundError if player does not exist.
async function getPlayerStatsImpl(playerId: number): Promise<PlayerStatsRow> {
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_player_full_stats", {
    p_player_id: playerId,
  });

  if (error) {
    throw new OperationError(`Failed to get player stats: ${error.message}`);
  }

  if (!data) {
    throw new PlayerNotFoundError(playerId);
  }

  return data;
}

// [>]: Get full stats for a single team (RPC: get_team_full_stats).
// Throws TeamNotFoundError if team does not exist.
async function getTeamStatsImpl(teamId: number): Promise<TeamStatsRow> {
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_team_full_stats", {
    p_team_id: teamId,
  });

  if (error) {
    throw new OperationError(`Failed to get team stats: ${error.message}`);
  }

  if (!data) {
    throw new TeamNotFoundError(teamId);
  }

  return data;
}

// [>]: Export wrapped functions with retry logic.
export const getPlayerStats = withRetry(getPlayerStatsImpl);
export const getTeamStats = withRetry(getTeamStatsImpl);

// [>]: Export types for use in services.
export type { PlayerStatsRow, TeamStatsRow };
