// [>]: Player ELO history repository.
// Tracks ELO changes for each player after matches.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import { OperationError } from "@/lib/errors/api-errors";

// [>]: Database row type for ELO history records.
interface PlayerEloHistoryRow {
  history_id: number;
  player_id: number;
  match_id: number;
  old_elo: number;
  new_elo: number;
  difference: number;
  date: string;
}

// [>]: Input type for creating ELO history records.
interface PlayerEloHistoryInput {
  player_id: number;
  match_id: number;
  old_elo: number;
  new_elo: number;
  date: string;
}

// [>]: Query options for history filtering.
interface HistoryQueryOptions {
  limit?: number;
  offset?: number;
  startDate?: string;
  endDate?: string;
}

// [>]: Record a single player ELO update. Returns history ID.
async function recordPlayerEloUpdateImpl(
  data: PlayerEloHistoryInput,
): Promise<number> {
  const client = getSupabaseClient();

  const difference = data.new_elo - data.old_elo;

  const { data: result, error } = await client
    .from("players_elo_history")
    .insert({
      player_id: data.player_id,
      match_id: data.match_id,
      old_elo: data.old_elo,
      new_elo: data.new_elo,
      difference,
      date: data.date,
    })
    .select("history_id")
    .single();

  if (error) {
    throw new OperationError(
      `Failed to record player ELO history: ${error.message}`,
    );
  }

  if (!result?.history_id) {
    throw new OperationError(
      "Failed to record player ELO history: no ID returned",
    );
  }

  return result.history_id;
}

// [>]: Batch record player ELO updates (4 players per match).
// Returns array of history IDs.
async function batchRecordPlayerEloUpdatesImpl(
  updates: PlayerEloHistoryInput[],
): Promise<number[]> {
  if (updates.length === 0) {
    return [];
  }

  const client = getSupabaseClient();

  const records = updates.map((update) => ({
    player_id: update.player_id,
    match_id: update.match_id,
    old_elo: update.old_elo,
    new_elo: update.new_elo,
    difference: update.new_elo - update.old_elo,
    date: update.date,
  }));

  const { data, error } = await client
    .from("players_elo_history")
    .insert(records)
    .select("history_id");

  if (error) {
    throw new OperationError(
      `Failed to batch record player ELO history: ${error.message}`,
    );
  }

  return (data ?? []).map((row) => row.history_id);
}

// [>]: Get ELO history for a player with pagination and optional date filters.
async function getPlayerEloHistoryImpl(
  playerId: number,
  options: HistoryQueryOptions = {},
): Promise<PlayerEloHistoryRow[]> {
  const { limit = 100, offset = 0, startDate, endDate } = options;
  const client = getSupabaseClient();

  let query = client
    .from("players_elo_history")
    .select(
      "history_id, player_id, match_id, old_elo, new_elo, difference, date",
    )
    .eq("player_id", playerId)
    .order("date", { ascending: false })
    .limit(limit)
    .range(offset, offset + limit - 1);

  if (startDate) {
    query = query.gte("date", startDate);
  }

  if (endDate) {
    query = query.lte("date", endDate);
  }

  const { data, error } = await query;

  if (error) {
    throw new OperationError(
      `Failed to get player ELO history: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Get all player ELO records for a specific match.
async function getPlayersEloHistoryByMatchIdImpl(
  matchId: number,
): Promise<PlayerEloHistoryRow[]> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("players_elo_history")
    .select(
      "history_id, player_id, match_id, old_elo, new_elo, difference, date",
    )
    .eq("match_id", matchId)
    .order("date", { ascending: false });

  if (error) {
    throw new OperationError(
      `Failed to get player ELO history for match: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Export wrapped functions with retry logic.
export const recordPlayerEloUpdate = withRetry(recordPlayerEloUpdateImpl);
export const batchRecordPlayerEloUpdates = withRetry(
  batchRecordPlayerEloUpdatesImpl,
);
export const getPlayerEloHistory = withRetry(getPlayerEloHistoryImpl);
export const getPlayersEloHistoryByMatchId = withRetry(
  getPlayersEloHistoryByMatchIdImpl,
);

// [>]: Export types for use in services.
export type { PlayerEloHistoryRow, PlayerEloHistoryInput, HistoryQueryOptions };
