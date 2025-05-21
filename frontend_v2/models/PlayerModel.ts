export interface PlayerModel {
  player_id: number;
  name: string;
  global_elo: number;
  created_at?: string,
  matches_played?: number;
  wins?: number;
  losses?: number; 
}