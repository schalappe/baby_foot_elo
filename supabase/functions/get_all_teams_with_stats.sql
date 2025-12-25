-- Helper function to get calculated stats for a single team
-- This function calculates match statistics for a given team_id.
CREATE OR REPLACE FUNCTION get_team_calculated_stats(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  team_matches_played INTEGER;
  team_wins INTEGER;
  team_losses INTEGER;
  team_win_rate NUMERIC;
  team_last_match_at TIMESTAMPTZ;
BEGIN
  -- Calculate total matches played by the team
  SELECT COUNT(match_id)
  INTO team_matches_played
  FROM matches
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  -- Calculate win count for the team
  SELECT COUNT(match_id)
  INTO team_wins
  FROM matches
  WHERE winner_team_id = p_team_id;

  -- Calculate loss count for the team
  -- This can also be derived if total_matches and wins are accurate
  SELECT COUNT(match_id)
  INTO team_losses
  FROM matches
  WHERE loser_team_id = p_team_id;
  -- Alternatively: team_losses := team_matches_played - team_wins;

  -- Calculate win rate
  IF COALESCE(team_matches_played, 0) > 0 THEN
    team_win_rate := team_wins::NUMERIC / team_matches_played::NUMERIC;
  ELSE
    team_win_rate := 0;
  END IF;

  -- Get the date of the last match played by the team
  SELECT MAX(played_at)
  INTO team_last_match_at
  FROM matches
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  RETURN jsonb_build_object(
    'matches_played', COALESCE(team_matches_played, 0),
    'wins', COALESCE(team_wins, 0),
    'losses', COALESCE(team_losses, 0),
    'win_rate', ROUND(COALESCE(team_win_rate, 0), 4), -- Round win_rate for cleaner output
    'last_match_at', team_last_match_at
  );
END;
$$;

-- Main function to get all teams with their comprehensive stats
-- This function retrieves teams with their stats, rank, and player details.
-- It depends on:
--   - get_team_calculated_stats(INTEGER) defined above.
--   - get_player_stats(INTEGER) (assumed to be pre-existing, provides player-specific stats).
CREATE OR REPLACE FUNCTION get_all_teams_with_stats(p_skip INTEGER DEFAULT 0, p_limit INTEGER DEFAULT 100)
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH ranked_teams AS (
    SELECT
      t.team_id,
      t.player1_id,
      t.player2_id,
      t.global_elo AS team_global_elo,
      t.created_at AS team_created_at,
      RANK() OVER (ORDER BY t.global_elo DESC, t.created_at ASC) AS team_rank -- Added created_at for tie-breaking in rank
    FROM teams t
  )
  SELECT
    jsonb_build_object(
      'team_id', rt.team_id,
      'global_elo', rt.team_global_elo,
      'created_at', rt.team_created_at,
      'player1_id', rt.player1_id,
      'player2_id', rt.player2_id,
      'rank', rt.team_rank
    ) || get_team_calculated_stats(rt.team_id) -- Merges: matches_played, wins, losses, win_rate, last_match_at
      || jsonb_build_object(
        'player1', COALESCE(
            (SELECT jsonb_build_object(
                        'player_id', p1.player_id,
                        'name', p1.name,
                        'global_elo', p1.global_elo,
                        'created_at', p1.created_at -- Corresponds to Player frontend interface 'creation_date'
                     ) || get_player_stats(p1.player_id) -- Merges player's: matches_played, wins, losses, last_match_at
             FROM players p1 WHERE p1.player_id = rt.player1_id),
            'null'::jsonb
        ),
        'player2', COALESCE(
            (SELECT jsonb_build_object(
                        'player_id', p2.player_id,
                        'name', p2.name,
                        'global_elo', p2.global_elo,
                        'created_at', p2.created_at -- Corresponds to Player frontend interface 'creation_date'
                     ) || get_player_stats(p2.player_id) -- Merges player's: matches_played, wins, losses, last_match_at
             FROM players p2 WHERE p2.player_id = rt.player2_id),
            'null'::jsonb
        )
      )
  FROM
    ranked_teams rt
  ORDER BY
    rt.team_rank ASC, rt.team_id ASC -- Ensure stable sort for pagination
  OFFSET p_skip
  LIMIT p_limit;
END;
$$;
