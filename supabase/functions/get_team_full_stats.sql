CREATE OR REPLACE FUNCTION get_team_full_stats(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  v_team_id INT;
  v_player1_id INT;
  v_player2_id INT;
  v_global_elo INT;
  v_created_at TIMESTAMPTZ;
  v_total_matches INTEGER;
  v_win_count INTEGER;
  v_loss_count INTEGER;
  v_last_match_date TIMESTAMPTZ;
  v_win_rate NUMERIC;
BEGIN
  -- Get team details
  SELECT team_id, player1_id, player2_id, global_elo, created_at
  INTO v_team_id, v_player1_id, v_player2_id, v_global_elo, v_created_at
  FROM teams
  WHERE team_id = p_team_id;

  -- Calculate total matches
  SELECT COUNT(m.match_id)
  INTO v_total_matches
  FROM matches m
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  -- Calculate win count
  SELECT COUNT(m.match_id)
  INTO v_win_count
  FROM matches m
  WHERE winner_team_id = p_team_id;

  -- Calculate loss count
  SELECT COUNT(m.match_id)
  INTO v_loss_count
  FROM matches m
  WHERE loser_team_id = p_team_id;

  -- Get last match date
  SELECT m.played_at
  INTO v_last_match_date
  FROM matches m
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id
  ORDER BY m.played_at DESC
  LIMIT 1;

  -- Calculate win rate as decimal (0.0 to 1.0)
  IF v_total_matches > 0 THEN
    v_win_rate := v_win_count::NUMERIC / v_total_matches::NUMERIC;
  ELSE
    v_win_rate := 0;
  END IF;

  RETURN jsonb_build_object(
    'team_id', v_team_id,
    'player1_id', v_player1_id,
    'player2_id', v_player2_id,
    'player1', COALESCE(get_player_full_stats(v_player1_id), '{}'::jsonb),
    'player2', COALESCE(get_player_full_stats(v_player2_id), '{}'::jsonb),
    'global_elo', v_global_elo,
    'created_at', v_created_at,
    'matches_played', COALESCE(v_total_matches, 0),
    'wins', COALESCE(v_win_count, 0),
    'losses', COALESCE(v_loss_count, 0),
    'last_match_at', v_last_match_date,
    'win_rate', ROUND(COALESCE(v_win_rate, 0), 4)
  );
END;
$$;
