-- ============================================================================
-- get_player_full_stats_optimized
-- ============================================================================
-- Returns a single player's comprehensive stats using a CTE.
-- Reduces 4 separate queries to 1 aggregated query.
-- ============================================================================

CREATE OR REPLACE FUNCTION get_player_full_stats_optimized(p_player_id INTEGER)
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
  WITH player_stats AS (
    SELECT
      COUNT(*) AS matches_played,
      COUNT(*) FILTER (WHERE is_winner) AS wins,
      COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
      MAX(played_at) AS last_match_at
    FROM (
      SELECT m.played_at, true AS is_winner
      FROM matches m
      JOIN teams t ON t.team_id = m.winner_team_id
      WHERE t.player1_id = p_player_id OR t.player2_id = p_player_id
      UNION ALL
      SELECT m.played_at, false AS is_winner
      FROM matches m
      JOIN teams t ON t.team_id = m.loser_team_id
      WHERE t.player1_id = p_player_id OR t.player2_id = p_player_id
    ) player_matches
  )
  SELECT jsonb_build_object(
    'player_id', p.player_id,
    'name', p.name,
    'global_elo', p.global_elo,
    'created_at', p.created_at,
    'matches_played', COALESCE(ps.matches_played, 0),
    'wins', COALESCE(ps.wins, 0),
    'losses', COALESCE(ps.losses, 0),
    'win_rate', CASE WHEN COALESCE(ps.matches_played, 0) > 0
                     THEN ROUND(ps.wins::NUMERIC / ps.matches_played::NUMERIC, 4)
                     ELSE 0 END,
    'last_match_at', ps.last_match_at
  )
  FROM players p
  CROSS JOIN player_stats ps
  WHERE p.player_id = p_player_id;
$$;
