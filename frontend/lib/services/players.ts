// [>]: Player service - business logic layer for player operations.
// Orchestrates repositories and applies validation rules.

import {
  createPlayerByName,
  getAllPlayers,
  getPlayerByName,
  updatePlayer,
  deletePlayerById,
} from "@/lib/db/repositories/players";
import { getPlayerStats } from "@/lib/db/repositories/stats";
import { createTeamByPlayerIds } from "@/lib/db/repositories/teams";
import { getPlayerEloHistory as getPlayerEloHistoryRepo } from "@/lib/db/repositories/player-elo-history";
import {
  PlayerAlreadyExistsError,
  InvalidPlayerDataError,
  PlayerOperationError,
} from "@/lib/errors/api-errors";
import { mapToPlayerResponse } from "@/lib/mappers/entity-mappers";
import type {
  PlayerCreate,
  PlayerUpdate,
  PlayerResponse,
} from "@/lib/types/schemas/player";
import type { EloHistoryResponse } from "@/lib/types/schemas/elo-history";

// [>]: Get a player by ID with full stats.
// Uses stats repository for computed fields (matches_played, wins, losses, win_rate).
export async function getPlayer(playerId: number): Promise<PlayerResponse> {
  const stats = await getPlayerStats(playerId);
  return mapToPlayerResponse(stats);
}

// [>]: Get all players with stats for ranking display.
export async function getAllPlayersWithStats(): Promise<PlayerResponse[]> {
  const players = await getAllPlayers();
  return players.map(mapToPlayerResponse);
}

// [>]: Create a new player.
// Validates name not empty, checks for duplicates, creates teams with existing players.
export async function createNewPlayer(
  data: PlayerCreate,
): Promise<PlayerResponse> {
  // [>]: Validate name is not empty.
  if (!data.name || !data.name.trim()) {
    throw new InvalidPlayerDataError(
      "Player name cannot be empty or whitespace only",
    );
  }

  // [>]: Check for existing player with same name.
  const existingPlayer = await getPlayerByName(data.name);
  if (existingPlayer) {
    throw new PlayerAlreadyExistsError(data.name);
  }

  try {
    // [>]: Create the player.
    const playerId = await createPlayerByName(data.name, data.global_elo);

    // [>]: Dynamically create teams with all existing players.
    const allPlayers = await getAllPlayers();
    for (const existingPlayer of allPlayers) {
      const existingPlayerId = existingPlayer.player_id;
      if (existingPlayerId !== playerId) {
        // [>]: createTeamByPlayerIds handles deduplication and ordering.
        await createTeamByPlayerIds(playerId, existingPlayerId);
      }
    }

    // [>]: Return the complete player data.
    return await getPlayer(playerId);
  } catch (error) {
    if (
      error instanceof InvalidPlayerDataError ||
      error instanceof PlayerAlreadyExistsError
    ) {
      throw error;
    }
    throw new PlayerOperationError(
      `Failed to create player: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

// [>]: Update an existing player.
// Validates name uniqueness if changed.
export async function updateExistingPlayer(
  playerId: number,
  data: PlayerUpdate,
): Promise<PlayerResponse> {
  // [>]: Verify player exists first (throws PlayerNotFoundError if not).
  const existingPlayer = await getPlayer(playerId);

  // [>]: If name is being updated, check for conflicts.
  if (data.name && data.name !== existingPlayer.name) {
    const conflictPlayer = await getPlayerByName(data.name);
    if (conflictPlayer && conflictPlayer.player_id !== playerId) {
      throw new PlayerAlreadyExistsError(data.name);
    }
  }

  // [>]: Update the player.
  await updatePlayer(playerId, {
    name: data.name,
    global_elo: data.global_elo,
  });

  return await getPlayer(playerId);
}

// [>]: Delete a player.
// Verifies existence before deletion.
export async function deletePlayer(playerId: number): Promise<void> {
  // [>]: Verify player exists (throws PlayerNotFoundError if not).
  await getPlayer(playerId);

  // [>]: Delete the player.
  await deletePlayerById(playerId);
}

// [>]: Get player's ELO history with pagination.
export async function getPlayerEloHistory(
  playerId: number,
  options?: { limit?: number; offset?: number },
): Promise<EloHistoryResponse[]> {
  // [>]: Verify player exists first.
  await getPlayer(playerId);

  const history = await getPlayerEloHistoryRepo(playerId, options);
  return history.map((h) => ({
    history_id: h.history_id,
    player_id: h.player_id,
    match_id: h.match_id,
    old_elo: h.old_elo,
    new_elo: h.new_elo,
    difference: h.difference,
    date: h.date,
  }));
}
