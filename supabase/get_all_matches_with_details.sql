CREATE OR REPLACE FUNCTION get_all_matches_with_details(
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
$$;
