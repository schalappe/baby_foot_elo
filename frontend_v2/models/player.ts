export interface PlayerModel {
  name: string;
  player_id?: number;
  global_elo?: number;
  created_at?: string,
  matches_played?: number;
  wins?: number;
  losses?: number; 
}