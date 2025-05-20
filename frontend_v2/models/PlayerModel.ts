export interface PlayerModel {
  name: String;
  player_id?: Number;
  global_elo?: Number;
  created_at?: String,
  matches_played?: Number;
  wins?: Number;
  losses?: Number; 
}