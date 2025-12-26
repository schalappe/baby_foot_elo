CREATE OR REPLACE FUNCTION get_player_matches_json(
    p_player_id BIGINT,
    p_start_date TIMESTAMP DEFAULT NULL,
    p_end_date TIMESTAMP DEFAULT NULL,
    p_is_fanny BOOLEAN DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
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
$$;
