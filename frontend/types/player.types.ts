/**
 * player.types.ts
 *
 * TypeScript interfaces and types for player-related data structures.
 * Used throughout the app for type safety in API responses and UI.
 *
 * Exports:
 *   - Player, PlayerStats, PlayerMatches, GetPlayersParams, etc.
 */
// frontend/types/player.types.ts
import { EntityStats } from "@/types/stats.types";

/**
 * Represents a player in the system with their basic information and ELO.
 */
export interface Player {
  player_id: number;
  name: string;
  global_elo: number;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  creation_date: string;
}

/**
 * PlayerStats extends EntityStats for compatibility with generic stats cards.
 */
export interface PlayerStats extends EntityStats {
  player_id: number;
  name: string;
  global_elo: number;
  matches_played: number;
  wins: number;
  losses: number;
  creation_date: string;
  win_rate: number;
  elo_difference: number[];
  elo_values: number[];
  average_elo_change: number;
  highest_elo: number;
  lowest_elo: number;
  recent: {
    matches_played: number;
    wins: number;
    losses: number;
    win_rate: number;
    average_elo_change: number;
    elo_changes: number[];
  };
}

/**
 * Represents a summary of a match a player participated in.
 */
export interface PlayerMatches {
  match_id: number;
  played_at: string;
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  notes: string;
}

/**
 * Parameters for fetching a list of players, allowing for pagination and sorting.
 */
export interface GetPlayersParams {
  limit?: number;
  skip?: number;
  sort_by?: string;
  order?: "asc" | "desc";
}
