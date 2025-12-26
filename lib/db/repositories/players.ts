// [>]: Player repository - all database operations for players table.
// Throws domain errors on failure; never returns null for ID lookups.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import {
  PlayerNotFoundError,
  PlayerOperationError,
} from "@/lib/errors/api-errors";

// [>]: Database row type for raw Supabase responses.
interface PlayerDbRow {
  player_id: number;
  name: string;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
}

// [>]: Extended row type with computed stats from RPC.
interface PlayerWithStatsRow extends PlayerDbRow {
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  rank?: number;
}

// [>]: Create a new player. Returns full player row.
async function createPlayerImpl(
  name: string,
  globalElo: number = 1000,
): Promise<PlayerDbRow> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("players")
    .insert({ name, global_elo: globalElo })
    .select("player_id, name, global_elo, created_at")
    .single();

  if (error) {
    throw new PlayerOperationError(`Failed to create player: ${error.message}`);
  }

  if (!data?.player_id) {
    throw new PlayerOperationError("Failed to create player: no ID returned");
  }

  return data;
}

// [>]: Lookup player by ID. Throws PlayerNotFoundError if not found.
async function getPlayerByIdImpl(playerId: number): Promise<PlayerDbRow> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("players")
    .select("player_id, name, global_elo, created_at")
    .eq("player_id", playerId)
    .maybeSingle();

  if (error) {
    throw new PlayerOperationError(`Database error: ${error.message}`);
  }

  if (!data) {
    throw new PlayerNotFoundError(playerId);
  }

  return data;
}

// [>]: Lookup player by name. Returns null if not found (for existence checks).
async function getPlayerByNameImpl(name: string): Promise<PlayerDbRow | null> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("players")
    .select("player_id, name, global_elo, created_at")
    .eq("name", name)
    .maybeSingle();

  if (error) {
    throw new PlayerOperationError(`Database error: ${error.message}`);
  }

  return data;
}

// [>]: Get all players with computed stats (uses RPC).
async function getAllPlayersImpl(): Promise<PlayerWithStatsRow[]> {
  const client = getSupabaseClient();

  const { data, error } = await client.rpc("get_all_players_with_stats");

  if (error) {
    throw new PlayerOperationError(
      `Failed to get all players: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Update player fields. Throws PlayerNotFoundError if player does not exist.
async function updatePlayerImpl(
  playerId: number,
  updates: { name?: string; global_elo?: number },
): Promise<void> {
  if (!updates.name && updates.global_elo === undefined) {
    return;
  }

  const client = getSupabaseClient();

  const updateFields: Record<string, unknown> = {};
  if (updates.name !== undefined) {
    updateFields.name = updates.name;
  }
  if (updates.global_elo !== undefined) {
    updateFields.global_elo = updates.global_elo;
  }

  const { data, error } = await client
    .from("players")
    .update(updateFields)
    .eq("player_id", playerId)
    .select("player_id");

  if (error) {
    throw new PlayerOperationError(`Failed to update player: ${error.message}`);
  }

  if (!data || data.length === 0) {
    throw new PlayerNotFoundError(playerId);
  }
}

// [>]: Batch update player ELOs. Used after match processing.
async function batchUpdatePlayersEloImpl(
  updates: Array<{ player_id: number; global_elo: number }>,
): Promise<void> {
  if (updates.length === 0) {
    return;
  }

  const client = getSupabaseClient();

  // [>]: Supabase does not support true batch updates with different values.
  // Execute updates sequentially within the same function call.
  for (const { player_id, global_elo } of updates) {
    const { error } = await client
      .from("players")
      .update({ global_elo })
      .eq("player_id", player_id);

    if (error) {
      throw new PlayerOperationError(
        `Failed to update player ${player_id} ELO: ${error.message}`,
      );
    }
  }
}

// [>]: Delete player by ID. Throws PlayerNotFoundError if not found.
async function deletePlayerByIdImpl(playerId: number): Promise<void> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("players")
    .delete()
    .eq("player_id", playerId)
    .select("player_id");

  if (error) {
    throw new PlayerOperationError(`Failed to delete player: ${error.message}`);
  }

  if (!data || data.length === 0) {
    throw new PlayerNotFoundError(playerId);
  }
}

// [>]: Export wrapped functions with retry logic.
export const createPlayer = withRetry(createPlayerImpl);
export const getPlayerById = withRetry(getPlayerByIdImpl);
export const getPlayerByName = withRetry(getPlayerByNameImpl);
export const getAllPlayers = withRetry(getAllPlayersImpl);
export const updatePlayer = withRetry(updatePlayerImpl);
export const batchUpdatePlayersElo = withRetry(batchUpdatePlayersEloImpl);
export const deletePlayerById = withRetry(deletePlayerByIdImpl);

// [>]: Legacy export for backward compatibility with tests.
// Returns only the player_id for tests that expect the old signature.
export async function createPlayerByName(
  name: string,
  globalElo: number = 1000,
): Promise<number> {
  const player = await createPlayer(name, globalElo);
  return player.player_id;
}

// [>]: Export types for use in services.
export type { PlayerDbRow, PlayerWithStatsRow };
