
DECLARE
  v_player_name TEXT;
  v_global_elo INT;
  v_created_at TIMESTAMPTZ;
  v_total_matches INTEGER;
  v_win_count INTEGER;
  v_loss_count INTEGER;
  v_last_match_date TIMESTAMPTZ;
  v_win_rate NUMERIC;
BEGIN
  -- Get player details
  SELECT name, global_elo, created_at
  INTO v_player_name, v_global_elo, v_created_at
  FROM players
  WHERE player_id = p_player_id;

  -- Calculate total matches
  SELECT COUNT(m.match_id)
  INTO v_total_matches
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  -- Calculate win count
  SELECT COUNT(m.match_id)
  INTO v_win_count
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  WHERE winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id;

  -- Calculate loss count
  SELECT COUNT(m.match_id)
  INTO v_loss_count
  FROM matches m
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id;

  -- Get last match date
  SELECT m.played_at
  INTO v_last_match_date
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE winner_team.player1_id = p_player_id
    OR winner_team.player2_id = p_player_id
    OR loser_team.player1_id = p_player_id
    OR loser_team.player2_id = p_player_id
  ORDER BY m.played_at DESC
  LIMIT 1;

  -- Calculate win rate
  IF v_total_matches > 0 THEN
    v_win_rate := (v_win_count::NUMERIC / v_total_matches::NUMERIC) * 100;
  ELSE
    v_win_rate := 0;
  END IF;

  RETURN jsonb_build_object(
    'player_id', p_player_id,
    'name', v_player_name,
    'global_elo', v_global_elo,
    'created_at', v_created_at,
    'matches_played', COALESCE(v_total_matches, 0),
    'wins', COALESCE(v_win_count, 0),
    'losses', COALESCE(v_loss_count, 0),
    'last_match_at', v_last_match_date,
    'win_rate', v_win_rate
  ) || get_player_comprehensive_stats(p_player_id);
END;
