// frontend/types/player.types.ts

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

export interface PlayerStats {
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

export interface PlayerMatches {
  match_id: number;
  played_at: string;
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  notes: string;
}

export interface GetPlayersParams {
  limit?: number;
  skip?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}
