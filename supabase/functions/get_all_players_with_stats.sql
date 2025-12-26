-- Helper function to get comprehensive stats for a single player
CREATE OR REPLACE FUNCTION get_player_stats(p_player_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  total_matches INTEGER;
  win_count INTEGER;
  loss_count INTEGER;
  last_match_date TIMESTAMPTZ;
  player_win_rate NUMERIC;
BEGIN
  -- Calculate total matches played by the player
  SELECT COUNT(m.match_id)
  INTO total_matches
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  -- Calculate win count for the player
  SELECT COUNT(m.match_id)
  INTO win_count
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id);

  -- Calculate loss count for the player
  SELECT COUNT(m.match_id)
  INTO loss_count
  FROM matches m
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  -- Get the date of the last match played by the player
  SELECT m.played_at
  INTO last_match_date
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id)
  ORDER BY m.played_at DESC
  LIMIT 1;

  -- Calculate win rate as decimal (0.0 to 1.0)
  IF COALESCE(total_matches, 0) > 0 THEN
    player_win_rate := win_count::NUMERIC / total_matches::NUMERIC;
  ELSE
    player_win_rate := 0;
  END IF;

  RETURN jsonb_build_object(
    'matches_played', COALESCE(total_matches, 0),
    'wins', COALESCE(win_count, 0),
    'losses', COALESCE(loss_count, 0),
    'win_rate', ROUND(COALESCE(player_win_rate, 0), 4),
    'last_match_at', last_match_date
  );
END;
$$;

-- Main function to get all players with their comprehensive stats
CREATE OR REPLACE FUNCTION get_all_players_with_stats()
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    jsonb_build_object(
      'player_id', p.player_id,
      'name', p.name,
      'global_elo', p.global_elo,
      'created_at', p.created_at -- Assuming 'created_at' column exists in 'players' table
    ) || get_player_stats(p.player_id) -- Merge player info with stats
  FROM
    players p
  ORDER BY
    p.global_elo DESC; -- Order by ELO as in the reference Python function
END;
$$;
