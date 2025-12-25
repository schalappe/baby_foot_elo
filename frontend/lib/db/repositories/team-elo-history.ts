// [>]: Team ELO history repository.
// Tracks ELO changes for each team after matches.

import { getSupabaseClient } from "@/lib/db/client";
import { withRetry } from "@/lib/db/retry";
import { OperationError } from "@/lib/errors/api-errors";

// [>]: Database row type for team ELO history records.
interface TeamEloHistoryRow {
  history_id: number;
  team_id: number;
  match_id: number;
  old_elo: number;
  new_elo: number;
  difference: number;
  date: string;
}

// [>]: Input type for creating team ELO history records.
interface TeamEloHistoryInput {
  team_id: number;
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

// [>]: Record a single team ELO update. Returns history ID.
async function recordTeamEloUpdateImpl(
  data: TeamEloHistoryInput,
): Promise<number> {
  const client = getSupabaseClient();

  const difference = data.new_elo - data.old_elo;

  const { data: result, error } = await client
    .from("teams_elo_history")
    .insert({
      team_id: data.team_id,
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
      `Failed to record team ELO history: ${error.message}`,
    );
  }

  if (!result?.history_id) {
    throw new OperationError(
      "Failed to record team ELO history: no ID returned",
    );
  }

  return result.history_id;
}

// [>]: Batch record team ELO updates (2 teams per match).
// Returns array of history IDs.
async function batchRecordTeamEloUpdatesImpl(
  updates: TeamEloHistoryInput[],
): Promise<number[]> {
  if (updates.length === 0) {
    return [];
  }

  const client = getSupabaseClient();

  const records = updates.map((update) => ({
    team_id: update.team_id,
    match_id: update.match_id,
    old_elo: update.old_elo,
    new_elo: update.new_elo,
    difference: update.new_elo - update.old_elo,
    date: update.date,
  }));

  const { data, error } = await client
    .from("teams_elo_history")
    .insert(records)
    .select("history_id");

  if (error) {
    throw new OperationError(
      `Failed to batch record team ELO history: ${error.message}`,
    );
  }

  return (data ?? []).map((row) => row.history_id);
}

// [>]: Get ELO history for a team with pagination and optional date filters.
async function getTeamEloHistoryImpl(
  teamId: number,
  options: HistoryQueryOptions = {},
): Promise<TeamEloHistoryRow[]> {
  const { limit = 100, offset = 0, startDate, endDate } = options;
  const client = getSupabaseClient();

  let query = client
    .from("teams_elo_history")
    .select("history_id, team_id, match_id, old_elo, new_elo, difference, date")
    .eq("team_id", teamId)
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
      `Failed to get team ELO history: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Get all team ELO records for a specific match.
async function getTeamsEloHistoryByMatchIdImpl(
  matchId: number,
): Promise<TeamEloHistoryRow[]> {
  const client = getSupabaseClient();

  const { data, error } = await client
    .from("teams_elo_history")
    .select("history_id, team_id, match_id, old_elo, new_elo, difference, date")
    .eq("match_id", matchId)
    .order("date", { ascending: false });

  if (error) {
    throw new OperationError(
      `Failed to get team ELO history for match: ${error.message}`,
    );
  }

  return data ?? [];
}

// [>]: Export wrapped functions with retry logic.
export const recordTeamEloUpdate = withRetry(recordTeamEloUpdateImpl);
export const batchRecordTeamEloUpdates = withRetry(
  batchRecordTeamEloUpdatesImpl,
);
export const getTeamEloHistory = withRetry(getTeamEloHistoryImpl);
export const getTeamsEloHistoryByMatchId = withRetry(
  getTeamsEloHistoryByMatchIdImpl,
);

// [>]: Export types for use in services.
export type { TeamEloHistoryRow, TeamEloHistoryInput, HistoryQueryOptions };
