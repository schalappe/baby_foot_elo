// frontend/types/team.types.ts
import { Player } from './player.types';

/**
 * Represents a team with detailed player information, as returned by the backend TeamResponse.
 *
 * Includes team metadata, required player objects for both team members, and optional ranking.
 */
export interface Team {
  team_id: number;              // Unique team identifier
  player1_id: number;           // ID of first player
  player2_id: number;           // ID of second player
  global_elo: number;           // Team's global ELO rating
  created_at: string;           // Team creation date (ISO string)
  last_match_at?: string | null;// Date of last match (nullable)
  player1: Player;              // Full details for player 1
  player2: Player;              // Full details for player 2
  rank?: number | null;         // Optional team rank
}


// Represents a match with ELO change info for a team, as returned by /teams/{team_id}/matches
import type { BackendMatchWithEloResponse } from './match.types';

export type TeamMatchWithElo = BackendMatchWithEloResponse;

/**
 * Team statistics structure returned from the backend statistics endpoint.
 *
 * Corresponds to the output of get_team_statistics (backend).
 */
export interface TeamStatistics {
  team_id: number;
  global_elo: number;
  total_matches: number;
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
