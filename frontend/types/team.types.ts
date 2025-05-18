// frontend/types/team.types.ts
import { Player } from './player.types';

export interface Team {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
  player1?: Player | null;
  player2?: Player | null;
  rank?: number | null;
}

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
}
