// [>]: Entity mappers for converting repository data to response types.
// Centralizes mapping logic to avoid duplication across services.
// Note: RPC functions return partial nested objects (e.g., player data in teams).
// We use type assertions to handle the mismatch between RPC data and schema types.

import type { PlayerWithStatsRow } from "@/lib/db/repositories/players";
import type { TeamWithStatsRow } from "@/lib/db/repositories/teams";
import type { MatchWithTeamsRow } from "@/lib/db/repositories/matches";
import type { PlayerResponse } from "@/lib/types/schemas/player";
import type { TeamResponse } from "@/lib/types/schemas/team";
import type { MatchResponse } from "@/lib/types/schemas/match";

// [>]: Map raw player data to PlayerResponse.
export function mapToPlayerResponse(data: PlayerWithStatsRow): PlayerResponse {
  return {
    player_id: data.player_id,
    name: data.name,
    global_elo: data.global_elo,
    created_at: data.created_at,
    last_match_at: data.last_match_at ?? null,
    matches_played: data.matches_played,
    wins: data.wins,
    losses: data.losses,
    win_rate: data.win_rate,
  };
}

// [>]: Map raw team data to TeamResponse.
// Note: player1/player2 from stats RPC are partial (no computed stats).
export function mapToTeamResponse(data: TeamWithStatsRow): TeamResponse {
  return {
    team_id: data.team_id,
    player1_id: data.player1_id,
    player2_id: data.player2_id,
    global_elo: data.global_elo,
    created_at: data.created_at,
    last_match_at: data.last_match_at ?? null,
    matches_played: data.matches_played,
    wins: data.wins,
    losses: data.losses,
    win_rate: data.win_rate,
    // [>]: Cast partial player data - RPC returns subset of PlayerResponse fields.
    player1: data.player1 as unknown as PlayerResponse | null,
    player2: data.player2 as unknown as PlayerResponse | null,
    rank: data.rank ?? null,
  };
}

// [>]: Map raw match data to MatchResponse.
// Note: winner_team/loser_team from RPC are partial (basic team info only).
export function mapToMatchResponse(data: MatchWithTeamsRow): MatchResponse {
  return {
    match_id: data.match_id,
    winner_team_id: data.winner_team_id,
    loser_team_id: data.loser_team_id,
    is_fanny: data.is_fanny,
    played_at: data.played_at,
    notes: data.notes ?? null,
    // [>]: Cast partial team data - RPC returns subset of TeamResponse fields.
    winner_team: data.winner_team as unknown as TeamResponse | null,
    loser_team: data.loser_team as unknown as TeamResponse | null,
  };
}
