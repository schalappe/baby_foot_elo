-- ============================================
-- Baby Foot ELO - Complete Schema Migration
-- Run this in the SQL Editor of your new Supabase project
-- ============================================

-- ============================================
-- 1. CREATE TABLES
-- ============================================

-- Players table
CREATE TABLE IF NOT EXISTS public.players (
    player_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR NOT NULL,
    global_elo INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE IF NOT EXISTS public.teams (
    team_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    global_elo INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_match_at TIMESTAMPTZ
);

-- Matches table
CREATE TABLE IF NOT EXISTS public.matches (
    match_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    winner_team_id INTEGER NOT NULL,
    loser_team_id INTEGER NOT NULL,
    is_fanny BOOLEAN NOT NULL DEFAULT FALSE,
    played_at TIMESTAMPTZ NOT NULL,
    notes TEXT
);

-- Players ELO history table
CREATE TABLE IF NOT EXISTS public.players_elo_history (
    history_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    difference INTEGER NOT NULL,
    date TIMESTAMPTZ NOT NULL
);

-- Teams ELO history table
CREATE TABLE IF NOT EXISTS public.teams_elo_history (
    history_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    team_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    difference INTEGER NOT NULL,
    date TIMESTAMPTZ NOT NULL
);

-- ============================================
-- 2. ADD FOREIGN KEYS
-- ============================================

ALTER TABLE public.teams
    ADD CONSTRAINT teams_player1_id_fkey FOREIGN KEY (player1_id) REFERENCES public.players(player_id),
    ADD CONSTRAINT teams_player2_id_fkey FOREIGN KEY (player2_id) REFERENCES public.players(player_id);

ALTER TABLE public.matches
    ADD CONSTRAINT matches_winner_team_id_fkey FOREIGN KEY (winner_team_id) REFERENCES public.teams(team_id),
    ADD CONSTRAINT matches_loser_team_id_fkey FOREIGN KEY (loser_team_id) REFERENCES public.teams(team_id);

ALTER TABLE public.players_elo_history
    ADD CONSTRAINT players_elo_history_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(player_id),
    ADD CONSTRAINT players_elo_history_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id);

ALTER TABLE public.teams_elo_history
    ADD CONSTRAINT teams_elo_history_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id),
    ADD CONSTRAINT teams_elo_history_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(match_id);

-- ============================================
-- 3. CREATE INDEXES
-- ============================================

-- Matches indexes
CREATE INDEX idx_matches_winner_team_id ON public.matches USING btree (winner_team_id);
CREATE INDEX idx_matches_loser_team_id ON public.matches USING btree (loser_team_id);
CREATE INDEX idx_matches_played_at ON public.matches USING btree (played_at);
-- [>]: Composite index for OR queries on winner/loser team lookups.
CREATE INDEX idx_matches_winner_loser_played ON public.matches USING btree (winner_team_id, loser_team_id, played_at DESC);

-- Players indexes
CREATE INDEX idx_players_name ON public.players USING btree (name);

-- Players ELO history indexes
CREATE INDEX idx_players_elohist_player_id ON public.players_elo_history USING btree (player_id);
CREATE INDEX idx_players_elohist_match_id ON public.players_elo_history USING btree (match_id);
CREATE INDEX idx_players_elohist_date ON public.players_elo_history USING btree (date);

-- Teams indexes
CREATE INDEX idx_teams_player1_id ON public.teams USING btree (player1_id);
CREATE INDEX idx_teams_player2_id ON public.teams USING btree (player2_id);
CREATE UNIQUE INDEX idx_teams_player_pair_order_insensitive ON public.teams USING btree (LEAST(player1_id, player2_id), GREATEST(player1_id, player2_id));
-- [>]: Composite index for player pair lookups.
CREATE INDEX idx_teams_players ON public.teams USING btree (player1_id, player2_id);

-- Teams ELO history indexes
CREATE INDEX idx_teams_elohist_team_id ON public.teams_elo_history USING btree (team_id);
CREATE INDEX idx_teams_elohist_match_id ON public.teams_elo_history USING btree (match_id);
CREATE INDEX idx_teams_elohist_date ON public.teams_elo_history USING btree (date);

-- ============================================
-- 4. CREATE FUNCTIONS (Optimized with CTEs)
-- ============================================

-- Get full stats for a single player (optimized)
CREATE OR REPLACE FUNCTION public.get_player_full_stats_optimized(p_player_id INTEGER)
RETURNS jsonb
LANGUAGE sql
STABLE
AS $function$
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
$function$;

-- Get all players with stats (optimized)
CREATE OR REPLACE FUNCTION public.get_all_players_with_stats_optimized()
RETURNS SETOF jsonb
LANGUAGE sql
STABLE
AS $function$
  WITH player_stats AS (
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
    'last_match_at', ps.last_match_at,
    'rank', RANK() OVER (ORDER BY p.global_elo DESC, p.created_at ASC)
  )
  FROM players p
  LEFT JOIN player_stats ps ON ps.player_id = p.player_id
  ORDER BY p.global_elo DESC;
$function$;

-- Get full stats for a team (optimized)
CREATE OR REPLACE FUNCTION public.get_team_full_stats_optimized(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE sql
STABLE
AS $function$
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
$function$;

-- Get all teams with stats (optimized)
CREATE OR REPLACE FUNCTION public.get_all_teams_with_stats_optimized(p_skip INTEGER DEFAULT 0, p_limit INTEGER DEFAULT 100)
RETURNS SETOF jsonb
LANGUAGE sql
STABLE
AS $function$
  WITH
  team_stats AS (
    SELECT
      team_id,
      COUNT(*) AS matches_played,
      COUNT(*) FILTER (WHERE is_winner) AS wins,
      COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
      MAX(played_at) AS last_match_at
    FROM (
      SELECT winner_team_id AS team_id, played_at, true AS is_winner FROM matches
      UNION ALL
      SELECT loser_team_id AS team_id, played_at, false AS is_winner FROM matches
    ) team_matches
    GROUP BY team_id
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
  ),
  ranked_teams AS (
    SELECT
      t.team_id,
      t.player1_id,
      t.player2_id,
      t.global_elo,
      t.created_at,
      COALESCE(ts.matches_played, 0) AS matches_played,
      COALESCE(ts.wins, 0) AS wins,
      COALESCE(ts.losses, 0) AS losses,
      ts.last_match_at,
      CASE WHEN COALESCE(ts.matches_played, 0) > 0
           THEN ROUND(ts.wins::NUMERIC / ts.matches_played::NUMERIC, 4)
           ELSE 0 END AS win_rate,
      RANK() OVER (ORDER BY t.global_elo DESC, t.created_at ASC) AS rank
    FROM teams t
    LEFT JOIN team_stats ts ON ts.team_id = t.team_id
  )
  SELECT jsonb_build_object(
    'team_id', rt.team_id,
    'player1_id', rt.player1_id,
    'player2_id', rt.player2_id,
    'global_elo', rt.global_elo,
    'created_at', rt.created_at,
    'matches_played', rt.matches_played,
    'wins', rt.wins,
    'losses', rt.losses,
    'win_rate', rt.win_rate,
    'last_match_at', rt.last_match_at,
    'rank', rt.rank,
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
  FROM ranked_teams rt
  JOIN players p1 ON p1.player_id = rt.player1_id
  JOIN players p2 ON p2.player_id = rt.player2_id
  LEFT JOIN player_stats ps1 ON ps1.player_id = rt.player1_id
  LEFT JOIN player_stats ps2 ON ps2.player_id = rt.player2_id
  ORDER BY rt.rank ASC, rt.team_id ASC
  OFFSET p_skip
  LIMIT p_limit;
$function$;

-- Get active teams with stats (batch - replaces N+1 pattern)
CREATE OR REPLACE FUNCTION public.get_active_teams_with_stats_batch(
  p_days_since_last_match INTEGER DEFAULT 180,
  p_min_matches INTEGER DEFAULT 10
)
RETURNS SETOF jsonb
LANGUAGE sql
STABLE
AS $function$
  WITH
  team_stats AS (
    SELECT
      team_id,
      COUNT(*) AS matches_played,
      COUNT(*) FILTER (WHERE is_winner) AS wins,
      COUNT(*) FILTER (WHERE NOT is_winner) AS losses,
      MAX(played_at) AS last_match_at
    FROM (
      SELECT winner_team_id AS team_id, played_at, true AS is_winner FROM matches
      UNION ALL
      SELECT loser_team_id AS team_id, played_at, false AS is_winner FROM matches
    ) team_matches
    GROUP BY team_id
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
  ),
  active_teams AS (
    SELECT
      t.team_id,
      t.player1_id,
      t.player2_id,
      t.global_elo,
      t.created_at,
      ts.matches_played,
      ts.wins,
      ts.losses,
      ts.last_match_at,
      CASE WHEN ts.matches_played > 0
           THEN ROUND(ts.wins::NUMERIC / ts.matches_played::NUMERIC, 4)
           ELSE 0 END AS win_rate,
      RANK() OVER (ORDER BY t.global_elo DESC, t.created_at ASC) AS rank
    FROM teams t
    JOIN team_stats ts ON ts.team_id = t.team_id
    WHERE ts.matches_played >= p_min_matches
      AND ts.last_match_at >= NOW() - (p_days_since_last_match || ' days')::INTERVAL
  )
  SELECT jsonb_build_object(
    'team_id', at.team_id,
    'player1_id', at.player1_id,
    'player2_id', at.player2_id,
    'global_elo', at.global_elo,
    'created_at', at.created_at,
    'matches_played', at.matches_played,
    'wins', at.wins,
    'losses', at.losses,
    'win_rate', at.win_rate,
    'last_match_at', at.last_match_at,
    'rank', at.rank,
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
  FROM active_teams at
  JOIN players p1 ON p1.player_id = at.player1_id
  JOIN players p2 ON p2.player_id = at.player2_id
  LEFT JOIN player_stats ps1 ON ps1.player_id = at.player1_id
  LEFT JOIN player_stats ps2 ON ps2.player_id = at.player2_id
  ORDER BY at.global_elo DESC, at.rank ASC;
$function$;

-- Get all matches with details (OPTIMIZED)
-- Returns paginated matches with full team and player details.
-- Uses CTEs to pre-compute all stats in a single pass instead of calling
-- get_team_full_stats_optimized() per row (which caused N+1 queries).
CREATE OR REPLACE FUNCTION public.get_all_matches_with_details(
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0,
    p_start_date TIMESTAMPTZ DEFAULT NULL,
    p_end_date TIMESTAMPTZ DEFAULT NULL,
    p_is_fanny BOOLEAN DEFAULT NULL
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
  WHERE (p_start_date IS NULL OR played_at >= p_start_date)
    AND (p_end_date IS NULL OR played_at <= p_end_date)
    AND (p_is_fanny IS NULL OR is_fanny = p_is_fanny)
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

-- Get team match history
CREATE OR REPLACE FUNCTION public.get_team_match_history(
    p_team_id INTEGER,
    p_start_date TIMESTAMPTZ DEFAULT NULL,
    p_end_date TIMESTAMPTZ DEFAULT NULL,
    p_is_fanny BOOLEAN DEFAULT FALSE,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        jsonb_build_object(
            'match_id', m.match_id,
            'winner_team_id', m.winner_team_id,
            'loser_team_id', m.loser_team_id,
            'is_fanny', m.is_fanny,
            'played_at', m.played_at,
            'notes', m.notes,
            'won', (m.winner_team_id = p_team_id),
            'elo_changes', jsonb_build_object(
                p_team_id::TEXT, jsonb_build_object(
                    'old_elo', teh.old_elo,
                    'new_elo', teh.new_elo,
                    'difference', teh.difference
                )
            ),
            'winner_team', get_team_full_stats_optimized(m.winner_team_id),
            'loser_team', get_team_full_stats_optimized(m.loser_team_id)
        )
    FROM
        teams_elo_history teh
    INNER JOIN
        matches m ON teh.match_id = m.match_id
    WHERE
        teh.team_id = p_team_id
        AND (p_start_date IS NULL OR m.played_at >= p_start_date)
        AND (p_end_date IS NULL OR m.played_at <= p_end_date)
        AND (p_is_fanny = FALSE OR m.is_fanny = TRUE)
    ORDER BY
        m.played_at DESC
    LIMIT
        p_limit
    OFFSET
        p_offset;
END;
$function$;

-- Get player matches (JSON format)
CREATE OR REPLACE FUNCTION public.get_player_matches_json(
    p_player_id BIGINT,
    p_start_date TIMESTAMP DEFAULT NULL,
    p_end_date TIMESTAMP DEFAULT NULL,
    p_is_fanny BOOLEAN DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
AS $function$
DECLARE
    result JSON;
BEGIN
    SELECT
        COALESCE(json_agg(t), '[]'::json)
    INTO result
    FROM (
        SELECT
            m.match_id,
            m.played_at,
            m.is_fanny,
            m.notes,
            m.winner_team_id,
            m.loser_team_id,
            json_build_object(
                p_player_id::TEXT, json_build_object(
                    'old_elo', peh.old_elo,
                    'new_elo', peh.new_elo,
                    'difference', peh.difference
                )
            ) AS elo_changes,
            CASE WHEN wt.team_id IS NOT NULL THEN json_build_object(
                'team_id', wt.team_id,
                'global_elo', wt.global_elo,
                'created_at', wt.created_at,
                'last_match_at', wt.last_match_at,
                'matches_played', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = wt.team_id OR m_stat.loser_team_id = wt.team_id),
                'wins', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = wt.team_id),
                'losses', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.loser_team_id = wt.team_id),
                'win_rate', CASE WHEN (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = wt.team_id OR m_stat.loser_team_id = wt.team_id) > 0
                                THEN ((SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = wt.team_id)::NUMERIC / (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = wt.team_id OR m_stat.loser_team_id = wt.team_id)::NUMERIC) * 100
                                ELSE 0
                           END,
                'player1_id', wt.player1_id,
                'player2_id', wt.player2_id,
                'player1', CASE WHEN wtp1.player_id IS NOT NULL THEN json_build_object(
                    'player_id', wtp1.player_id,
                    'name', wtp1.name,
                    'global_elo', wtp1.global_elo,
                    'created_at', wtp1.created_at
                ) ELSE NULL END,
                'player2', CASE WHEN wtp2.player_id IS NOT NULL THEN json_build_object(
                    'player_id', wtp2.player_id,
                    'name', wtp2.name,
                    'global_elo', wtp2.global_elo,
                    'created_at', wtp2.created_at
                ) ELSE NULL END
            ) ELSE NULL END AS winner_team,
            CASE WHEN lt.team_id IS NOT NULL THEN json_build_object(
                'team_id', lt.team_id,
                'global_elo', lt.global_elo,
                'created_at', lt.created_at,
                'last_match_at', lt.last_match_at,
                'matches_played', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = lt.team_id OR m_stat.loser_team_id = lt.team_id),
                'wins', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = lt.team_id),
                'losses', (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.loser_team_id = lt.team_id),
                'win_rate', CASE WHEN (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = lt.team_id OR m_stat.loser_team_id = lt.team_id) > 0
                                THEN ((SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = lt.team_id)::NUMERIC / (SELECT COUNT(*) FROM matches m_stat WHERE m_stat.winner_team_id = lt.team_id OR m_stat.loser_team_id = lt.team_id)::NUMERIC) * 100
                                ELSE 0
                           END,
                'player1_id', lt.player1_id,
                'player2_id', lt.player2_id,
                'player1', CASE WHEN ltp1.player_id IS NOT NULL THEN json_build_object(
                    'player_id', ltp1.player_id,
                    'name', ltp1.name,
                    'global_elo', ltp1.global_elo,
                    'created_at', ltp1.created_at
                ) ELSE NULL END,
                'player2', CASE WHEN ltp2.player_id IS NOT NULL THEN json_build_object(
                    'player_id', ltp2.player_id,
                    'name', ltp2.name,
                    'global_elo', ltp2.global_elo,
                    'created_at', ltp2.created_at
                ) ELSE NULL END
            ) ELSE NULL END AS loser_team
        FROM
            players_elo_history peh
        JOIN
            matches m ON peh.match_id = m.match_id
        LEFT JOIN
            Teams wt ON m.winner_team_id = wt.team_id
        LEFT JOIN
            Players wtp1 ON wt.player1_id = wtp1.player_id
        LEFT JOIN
            Players wtp2 ON wt.player2_id = wtp2.player_id
        LEFT JOIN
            Teams lt ON m.loser_team_id = lt.team_id
        LEFT JOIN
            Players ltp1 ON lt.player1_id = ltp1.player_id
        LEFT JOIN
            Players ltp2 ON lt.player2_id = ltp2.player_id
        WHERE
            peh.player_id = p_player_id
            AND (p_start_date IS NULL OR m.played_at >= p_start_date)
            AND (p_end_date IS NULL OR m.played_at <= p_end_date)
            AND (p_is_fanny IS NULL OR m.is_fanny = p_is_fanny)
        ORDER BY
            m.played_at DESC
        LIMIT
            p_limit
        OFFSET
            p_offset
    ) t;

    RETURN result;
END;
$function$;

-- ============================================
-- 5. GRANT PERMISSIONS (for Supabase API access)
-- ============================================

GRANT ALL ON TABLE public.players TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.teams TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.matches TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.players_elo_history TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.teams_elo_history TO anon, authenticated, service_role;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- ============================================
-- Migration complete!
-- ============================================
