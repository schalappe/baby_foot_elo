/**
 * team.types.ts
 *
 * TypeScript interfaces and types for team-related data structures.
 * Used throughout the app for type safety in API responses and UI.
 *
 * Exports:
 *   - Team, TeamMatchWithElo, TeamStatistics, etc.
 */
// frontend/types/team.types.ts
import { Player } from "@/types/player.types";
import { EntityStats } from "@/types/stats.types";
import { BackendMatchWithEloResponse } from "@/types/match.types";

/**
 * Represents a team with detailed player information, as returned by the backend TeamResponse.
 *
 * Includes team metadata, required player objects for both team members, and optional ranking.
 */
export interface Team {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  last_match_at?: string | null;
  player1: Player;
  player2: Player;
  rank?: number | null;
}

export type TeamMatchWithElo = BackendMatchWithEloResponse;

/**
 * TeamStatistics extends EntityStats for compatibility with generic stats cards.
 * Adds matches_played as an alias for total_matches.
 */
export interface TeamStatistics extends EntityStats {
  team_id: number;
  global_elo: number;
  total_matches: number;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
  elo_difference: number[];
  elo_values: number[];
  average_elo_change: number;
  highest_elo: number;
  lowest_elo: number;
  created_at: string;
  last_match_at: string | null;
  recent: {
    matches_played: number;
    wins: number;
    losses: number;
    win_rate: number;
    average_elo_change: number;
    elo_changes: number[];
  };
  player1_id: number;
  player2_id: number;
  player1: Player;
  player2: Player;
}
