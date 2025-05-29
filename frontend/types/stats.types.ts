export interface EntityStats {
  global_elo: number;
  elo_values: number[];
  wins: number;
  losses: number;
  win_rate: number;
  matches_played?: number;
  recent: {
    elo_changes: number[];
    win_rate: number;
    wins: number;
    losses: number;
    matches_played?: number;
  };
  [key: string]: unknown;
}
