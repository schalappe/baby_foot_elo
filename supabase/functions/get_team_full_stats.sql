-- ============================================================================
-- get_team_full_stats_optimized
-- ============================================================================
-- Returns a single team's comprehensive stats with nested player data using CTEs.
-- Reduces multiple separate queries to a single aggregated query.
-- ============================================================================

CREATE OR REPLACE FUNCTION get_team_full_stats_optimized(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
  WITH
  team_stats AS (
    SELECT
      COUNT(*) AS matches_played,
      COUNT(*) FILTER (WHERE is_winner) AS wins,
      COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
      MAX(played_at) AS last_match_at
    FROM (
      SELECT played_at, true AS is_winner
      FROM matches WHERE winner_team_id = p_team_id
      UNION ALL
      SELECT played_at, false AS is_winner
      FROM matches WHERE loser_team_id = p_team_id
    ) team_matches
  ),

  player_stats AS (
    SELECT
      player_id,
      COUNT(*) AS matches_played,
      COUNT(*) FILTER (WHERE is_winner) AS wins,
      COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
      MAX(played_at) AS last_match_at
    FROM (
      SELECT
        UNNEST(ARRAY[t.player1_id, t.player2_id]) AS player_id,
        m.played_at,
        true AS is_winner
      FROM matches m
      JOIN teams t ON t.team_id = m.winner_team_id
      UNION ALL
      SELECT
        UNNEST(ARRAY[t.player1_id, t.player2_id]) AS player_id,
        m.played_at,
        false AS is_winner
      FROM matches m
      JOIN teams t ON t.team_id = m.loser_team_id
    ) player_matches
    GROUP BY player_id
  )

  SELECT jsonb_build_object(
    'team_id', t.team_id,
    'player1_id', t.player1_id,
    'player2_id', t.player2_id,
    'global_elo', t.global_elo,
    'created_at', t.created_at,
    'matches_played', COALESCE(ts.matches_played, 0),
    'wins', COALESCE(ts.wins, 0),
    'losses', COALESCE(ts.losses, 0),
    'win_rate', CASE WHEN COALESCE(ts.matches_played, 0) > 0
                     THEN ROUND(ts.wins::NUMERIC / ts.matches_played::NUMERIC, 4)
                     ELSE 0 END,
    'last_match_at', ts.last_match_at,
    'player1', jsonb_build_object(
      'player_id', p1.player_id,
      'name', p1.name,
      'global_elo', p1.global_elo,
      'created_at', p1.created_at,
      'matches_played', COALESCE(ps1.matches_played, 0),
      'wins', COALESCE(ps1.wins, 0),
      'losses', COALESCE(ps1.losses, 0),
      'win_rate', CASE WHEN COALESCE(ps1.matches_played, 0) > 0
                       THEN ROUND(ps1.wins::NUMERIC / ps1.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', ps1.last_match_at
    ),
    'player2', jsonb_build_object(
      'player_id', p2.player_id,
      'name', p2.name,
      'global_elo', p2.global_elo,
      'created_at', p2.created_at,
      'matches_played', COALESCE(ps2.matches_played, 0),
      'wins', COALESCE(ps2.wins, 0),
      'losses', COALESCE(ps2.losses, 0),
      'win_rate', CASE WHEN COALESCE(ps2.matches_played, 0) > 0
                       THEN ROUND(ps2.wins::NUMERIC / ps2.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', ps2.last_match_at
    )
  )
  FROM teams t
  CROSS JOIN team_stats ts
  JOIN players p1 ON p1.player_id = t.player1_id
  JOIN players p2 ON p2.player_id = t.player2_id
  LEFT JOIN player_stats ps1 ON ps1.player_id = t.player1_id
  LEFT JOIN player_stats ps2 ON ps2.player_id = t.player2_id
  WHERE t.team_id = p_team_id;
$$;
