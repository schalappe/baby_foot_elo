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

-- Teams ELO history indexes
CREATE INDEX idx_teams_elohist_team_id ON public.teams_elo_history USING btree (team_id);
CREATE INDEX idx_teams_elohist_match_id ON public.teams_elo_history USING btree (match_id);
CREATE INDEX idx_teams_elohist_date ON public.teams_elo_history USING btree (date);

-- ============================================
-- 4. CREATE FUNCTIONS
-- ============================================

-- Helper function to get stats for a single player
CREATE OR REPLACE FUNCTION public.get_player_stats(p_player_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
DECLARE
  total_matches INTEGER;
  win_count INTEGER;
  loss_count INTEGER;
  win_rate NUMERIC;
  last_match_date TIMESTAMPTZ;
BEGIN
  SELECT COUNT(m.match_id)
  INTO total_matches
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  SELECT COUNT(m.match_id)
  INTO win_count
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id);

  SELECT COUNT(m.match_id)
  INTO loss_count
  FROM matches m
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  SELECT m.played_at
  INTO last_match_date
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id)
  ORDER BY m.played_at DESC
  LIMIT 1;

  IF COALESCE(total_matches, 0) > 0 THEN
    win_rate := win_count::NUMERIC / total_matches::NUMERIC;
  ELSE
    win_rate := 0;
  END IF;

  RETURN jsonb_build_object(
    'matches_played', COALESCE(total_matches, 0),
    'wins', COALESCE(win_count, 0),
    'losses', COALESCE(loss_count, 0),
    'win_rate', ROUND(COALESCE(win_rate, 0), 4),
    'last_match_at', last_match_date
  );
END;
$function$;

-- Get full stats for a single player
CREATE OR REPLACE FUNCTION public.get_player_full_stats(p_player_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
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
  SELECT name, global_elo, created_at
  INTO v_player_name, v_global_elo, v_created_at
  FROM players
  WHERE player_id = p_player_id;

  SELECT COUNT(m.match_id)
  INTO v_total_matches
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE (winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id)
     OR (loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id);

  SELECT COUNT(m.match_id)
  INTO v_win_count
  FROM matches m
  INNER JOIN teams winner_team ON m.winner_team_id = winner_team.team_id
  WHERE winner_team.player1_id = p_player_id OR winner_team.player2_id = p_player_id;

  SELECT COUNT(m.match_id)
  INTO v_loss_count
  FROM matches m
  INNER JOIN teams loser_team ON m.loser_team_id = loser_team.team_id
  WHERE loser_team.player1_id = p_player_id OR loser_team.player2_id = p_player_id;

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
  );
END;
$function$;

-- Get all players with stats
CREATE OR REPLACE FUNCTION public.get_all_players_with_stats()
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $function$
BEGIN
  RETURN QUERY
  SELECT
    jsonb_build_object(
      'player_id', p.player_id,
      'name', p.name,
      'global_elo', p.global_elo,
      'created_at', p.created_at
    ) || get_player_stats(p.player_id)
  FROM
    players p
  ORDER BY
    p.global_elo DESC;
END;
$function$;

-- Helper function to get calculated stats for a team
CREATE OR REPLACE FUNCTION public.get_team_calculated_stats(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
DECLARE
  team_matches_played INTEGER;
  team_wins INTEGER;
  team_losses INTEGER;
  team_win_rate NUMERIC;
  team_last_match_at TIMESTAMPTZ;
BEGIN
  SELECT COUNT(match_id)
  INTO team_matches_played
  FROM matches
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  SELECT COUNT(match_id)
  INTO team_wins
  FROM matches
  WHERE winner_team_id = p_team_id;

  SELECT COUNT(match_id)
  INTO team_losses
  FROM matches
  WHERE loser_team_id = p_team_id;

  IF COALESCE(team_matches_played, 0) > 0 THEN
    team_win_rate := team_wins::NUMERIC / team_matches_played::NUMERIC;
  ELSE
    team_win_rate := 0;
  END IF;

  SELECT MAX(played_at)
  INTO team_last_match_at
  FROM matches
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  RETURN jsonb_build_object(
    'matches_played', COALESCE(team_matches_played, 0),
    'wins', COALESCE(team_wins, 0),
    'losses', COALESCE(team_losses, 0),
    'win_rate', ROUND(COALESCE(team_win_rate, 0), 4),
    'last_match_at', team_last_match_at
  );
END;
$function$;

-- Get full stats for a team
CREATE OR REPLACE FUNCTION public.get_team_full_stats(p_team_id INTEGER)
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
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
  SELECT team_id, player1_id, player2_id, global_elo, created_at
  INTO v_team_id, v_player1_id, v_player2_id, v_global_elo, v_created_at
  FROM teams
  WHERE team_id = p_team_id;

  SELECT COUNT(m.match_id)
  INTO v_total_matches
  FROM matches m
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id;

  SELECT COUNT(m.match_id)
  INTO v_win_count
  FROM matches m
  WHERE winner_team_id = p_team_id;

  SELECT COUNT(m.match_id)
  INTO v_loss_count
  FROM matches m
  WHERE loser_team_id = p_team_id;

  SELECT m.played_at
  INTO v_last_match_date
  FROM matches m
  WHERE winner_team_id = p_team_id OR loser_team_id = p_team_id
  ORDER BY m.played_at DESC
  LIMIT 1;

  IF v_total_matches > 0 THEN
    v_win_rate := (v_win_count::NUMERIC / v_total_matches::NUMERIC) * 100;
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
    'win_rate', v_win_rate
  );
END;
$function$;

-- Get all teams with stats
CREATE OR REPLACE FUNCTION public.get_all_teams_with_stats(p_skip INTEGER DEFAULT 0, p_limit INTEGER DEFAULT 100)
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $function$
BEGIN
  RETURN QUERY
  WITH ranked_teams AS (
    SELECT
      t.team_id,
      t.player1_id,
      t.player2_id,
      t.global_elo AS team_global_elo,
      t.created_at AS team_created_at,
      RANK() OVER (ORDER BY t.global_elo DESC, t.created_at ASC) AS team_rank
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
    ) || get_team_calculated_stats(rt.team_id)
      || jsonb_build_object(
        'player1', COALESCE(
            (SELECT jsonb_build_object(
                        'player_id', p1.player_id,
                        'name', p1.name,
                        'global_elo', p1.global_elo,
                        'created_at', p1.created_at
                     ) || get_player_stats(p1.player_id)
             FROM players p1 WHERE p1.player_id = rt.player1_id),
            'null'::jsonb
        ),
        'player2', COALESCE(
            (SELECT jsonb_build_object(
                        'player_id', p2.player_id,
                        'name', p2.name,
                        'global_elo', p2.global_elo,
                        'created_at', p2.created_at
                     ) || get_player_stats(p2.player_id)
             FROM players p2 WHERE p2.player_id = rt.player2_id),
            'null'::jsonb
        )
      )
  FROM
    ranked_teams rt
  ORDER BY
    rt.team_rank ASC, rt.team_id ASC
  OFFSET p_skip
  LIMIT p_limit;
END;
$function$;

-- Get all matches with details
CREATE OR REPLACE FUNCTION public.get_all_matches_with_details(p_limit INTEGER DEFAULT 100, p_offset INTEGER DEFAULT 0)
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $function$
BEGIN
  RETURN QUERY
  SELECT
    jsonb_build_object(
      'match_id', m.match_id,
      'is_fanny', m.is_fanny,
      'played_at', m.played_at,
      'notes', m.notes,
      'winner_team_id', m.winner_team_id,
      'loser_team_id', m.loser_team_id,
      'winner_team', get_team_full_stats(m.winner_team_id),
      'loser_team', get_team_full_stats(m.loser_team_id)
    )
  FROM
    matches m
  ORDER BY
    m.played_at DESC
  LIMIT
    p_limit
  OFFSET
    p_offset;
END;
$function$;

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
            'winner_team', get_team_full_stats(m.winner_team_id),
            'loser_team', get_team_full_stats(m.loser_team_id)
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
