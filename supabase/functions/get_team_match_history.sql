CREATE OR REPLACE FUNCTION get_team_match_history(
    p_team_id INTEGER,
    p_start_date TIMESTAMPTZ DEFAULT NULL,
    p_end_date TIMESTAMPTZ DEFAULT NULL,
    p_is_fanny BOOLEAN DEFAULT NULL,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS SETOF jsonb
LANGUAGE plpgsql
AS $$
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
        AND (p_is_fanny IS NULL OR m.is_fanny = p_is_fanny)
    ORDER BY
        m.played_at DESC
    LIMIT
        p_limit
    OFFSET
        p_offset;
END;
$$;
