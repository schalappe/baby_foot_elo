-- ============================================================================
-- get_all_matches_with_details (OPTIMIZED)
-- ============================================================================
-- Returns paginated matches with full team and player details.
-- Uses CTEs to pre-compute all stats in a single pass instead of calling
-- get_team_full_stats_optimized() per row (which caused N+1 queries).
--
-- Performance: O(1) query instead of O(2*N) function calls for N matches.
-- ============================================================================

CREATE OR REPLACE FUNCTION get_all_matches_with_details(
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS SETOF jsonb
LANGUAGE sql
STABLE
AS $$
WITH
-- Step 1: Get paginated matches first (limits scope of all subsequent CTEs).
target_matches AS (
  SELECT match_id, is_fanny, played_at, notes, winner_team_id, loser_team_id
  FROM matches
  ORDER BY played_at DESC
  LIMIT p_limit
  OFFSET p_offset
),

-- Step 2: Collect unique team IDs from target matches.
involved_team_ids AS (
  SELECT DISTINCT team_id FROM (
    SELECT winner_team_id AS team_id FROM target_matches
    UNION
    SELECT loser_team_id AS team_id FROM target_matches
  ) t
),

-- Step 3: Pre-compute team stats for ALL involved teams in one scan.
team_stats AS (
  SELECT
    team_id,
    COUNT(*) AS matches_played,
    COUNT(*) FILTER (WHERE is_winner) AS wins,
    COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
    MAX(played_at) AS last_match_at
  FROM (
    SELECT winner_team_id AS team_id, played_at, true AS is_winner
    FROM matches
    WHERE winner_team_id IN (SELECT team_id FROM involved_team_ids)
    UNION ALL
    SELECT loser_team_id AS team_id, played_at, false AS is_winner
    FROM matches
    WHERE loser_team_id IN (SELECT team_id FROM involved_team_ids)
  ) all_team_matches
  GROUP BY team_id
),

-- Step 4: Collect unique player IDs from involved teams.
involved_player_ids AS (
  SELECT DISTINCT player_id FROM (
    SELECT player1_id AS player_id FROM teams WHERE team_id IN (SELECT team_id FROM involved_team_ids)
    UNION
    SELECT player2_id AS player_id FROM teams WHERE team_id IN (SELECT team_id FROM involved_team_ids)
  ) p
),

-- Step 5: Pre-compute player stats for ALL involved players in one scan.
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
    WHERE t.player1_id IN (SELECT player_id FROM involved_player_ids)
       OR t.player2_id IN (SELECT player_id FROM involved_player_ids)
    UNION ALL
    SELECT
      UNNEST(ARRAY[t.player1_id, t.player2_id]) AS player_id,
      m.played_at,
      false AS is_winner
    FROM matches m
    JOIN teams t ON t.team_id = m.loser_team_id
    WHERE t.player1_id IN (SELECT player_id FROM involved_player_ids)
       OR t.player2_id IN (SELECT player_id FROM involved_player_ids)
  ) player_matches
  GROUP BY player_id
)

-- Step 6: Build final JSONB result by joining all pre-computed data.
SELECT jsonb_build_object(
  'match_id', m.match_id,
  'is_fanny', m.is_fanny,
  'played_at', m.played_at,
  'notes', m.notes,
  'winner_team_id', m.winner_team_id,
  'loser_team_id', m.loser_team_id,
  'winner_team', jsonb_build_object(
    'team_id', wt.team_id,
    'player1_id', wt.player1_id,
    'player2_id', wt.player2_id,
    'global_elo', wt.global_elo,
    'created_at', wt.created_at,
    'matches_played', COALESCE(wts.matches_played, 0),
    'wins', COALESCE(wts.wins, 0),
    'losses', COALESCE(wts.losses, 0),
    'win_rate', CASE WHEN COALESCE(wts.matches_played, 0) > 0
                     THEN ROUND(wts.wins::NUMERIC / wts.matches_played::NUMERIC, 4)
                     ELSE 0 END,
    'last_match_at', wts.last_match_at,
    'player1', jsonb_build_object(
      'player_id', wp1.player_id,
      'name', wp1.name,
      'global_elo', wp1.global_elo,
      'created_at', wp1.created_at,
      'matches_played', COALESCE(wps1.matches_played, 0),
      'wins', COALESCE(wps1.wins, 0),
      'losses', COALESCE(wps1.losses, 0),
      'win_rate', CASE WHEN COALESCE(wps1.matches_played, 0) > 0
                       THEN ROUND(wps1.wins::NUMERIC / wps1.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', wps1.last_match_at
    ),
    'player2', jsonb_build_object(
      'player_id', wp2.player_id,
      'name', wp2.name,
      'global_elo', wp2.global_elo,
      'created_at', wp2.created_at,
      'matches_played', COALESCE(wps2.matches_played, 0),
      'wins', COALESCE(wps2.wins, 0),
      'losses', COALESCE(wps2.losses, 0),
      'win_rate', CASE WHEN COALESCE(wps2.matches_played, 0) > 0
                       THEN ROUND(wps2.wins::NUMERIC / wps2.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', wps2.last_match_at
    )
  ),
  'loser_team', jsonb_build_object(
    'team_id', lt.team_id,
    'player1_id', lt.player1_id,
    'player2_id', lt.player2_id,
    'global_elo', lt.global_elo,
    'created_at', lt.created_at,
    'matches_played', COALESCE(lts.matches_played, 0),
    'wins', COALESCE(lts.wins, 0),
    'losses', COALESCE(lts.losses, 0),
    'win_rate', CASE WHEN COALESCE(lts.matches_played, 0) > 0
                     THEN ROUND(lts.wins::NUMERIC / lts.matches_played::NUMERIC, 4)
                     ELSE 0 END,
    'last_match_at', lts.last_match_at,
    'player1', jsonb_build_object(
      'player_id', lp1.player_id,
      'name', lp1.name,
      'global_elo', lp1.global_elo,
      'created_at', lp1.created_at,
      'matches_played', COALESCE(lps1.matches_played, 0),
      'wins', COALESCE(lps1.wins, 0),
      'losses', COALESCE(lps1.losses, 0),
      'win_rate', CASE WHEN COALESCE(lps1.matches_played, 0) > 0
                       THEN ROUND(lps1.wins::NUMERIC / lps1.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', lps1.last_match_at
    ),
    'player2', jsonb_build_object(
      'player_id', lp2.player_id,
      'name', lp2.name,
      'global_elo', lp2.global_elo,
      'created_at', lp2.created_at,
      'matches_played', COALESCE(lps2.matches_played, 0),
      'wins', COALESCE(lps2.wins, 0),
      'losses', COALESCE(lps2.losses, 0),
      'win_rate', CASE WHEN COALESCE(lps2.matches_played, 0) > 0
                       THEN ROUND(lps2.wins::NUMERIC / lps2.matches_played::NUMERIC, 4)
                       ELSE 0 END,
      'last_match_at', lps2.last_match_at
    )
  )
)
FROM target_matches m
-- Winner team joins.
JOIN teams wt ON wt.team_id = m.winner_team_id
LEFT JOIN team_stats wts ON wts.team_id = wt.team_id
JOIN players wp1 ON wp1.player_id = wt.player1_id
JOIN players wp2 ON wp2.player_id = wt.player2_id
LEFT JOIN player_stats wps1 ON wps1.player_id = wt.player1_id
LEFT JOIN player_stats wps2 ON wps2.player_id = wt.player2_id
-- Loser team joins.
JOIN teams lt ON lt.team_id = m.loser_team_id
LEFT JOIN team_stats lts ON lts.team_id = lt.team_id
JOIN players lp1 ON lp1.player_id = lt.player1_id
JOIN players lp2 ON lp2.player_id = lt.player2_id
LEFT JOIN player_stats lps1 ON lps1.player_id = lt.player1_id
LEFT JOIN player_stats lps2 ON lps2.player_id = lt.player2_id
ORDER BY m.played_at DESC;
$$;
