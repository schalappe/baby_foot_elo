# -*- coding: utf-8 -*-
"""
Query builder and common query functions.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from app.db import transaction, with_retry

from .elo_history import get_current_elo
from .players import get_player

# ===== Common Query Functions =====


@with_retry()
def search_players(name_pattern: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for players by name pattern.

    Parameters
    ----------
    name_pattern : str
        Name pattern to search for
    limit : int
        Maximum number of results to return

    Returns
    -------
    List[Dict[str, Any]]
        List of matching player dictionaries
    """
    db = transaction()
    query = """
    SELECT player_id, name, created_at
    FROM Players
    WHERE name LIKE ?
    ORDER BY name
    LIMIT ?
    """
    results = db.fetchall(query, [f"%{name_pattern}%", limit])
    return [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in results] if results else []


@with_retry()
def get_player_stats(player_id: int) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive stats for a player.

    Parameters
    ----------
    player_id : int
        ID of the player

    Returns
    -------
    Optional[Dict[str, Any]]
        Player statistics, or None if player not found
    """
    db = transaction()

    # Get player details
    player = get_player(player_id)
    if not player:
        return None

    # Get current ELO
    current_elo = get_current_elo(player_id)

    # Get match count (Assuming player name is unique and can be used to identify their teams)
    # Note: This logic might need refinement if players can be on multiple teams or team names don't directly correlate
    match_count_query = """
    SELECT COUNT(DISTINCT m.match_id) FROM Matches m
    JOIN Teams t1 ON m.team1_id = t1.team_id
    JOIN Teams t2 ON m.team2_id = t2.team_id
    WHERE t1.name LIKE ? OR t2.name LIKE ? 
    """
    # Use player name to approximate team involvement. This might be inaccurate.
    # A better approach would involve a PlayerTeams mapping table.
    player_name_pattern = f"%{player['name']}%"
    match_count_result = db.fetchone(match_count_query, [player_name_pattern, player_name_pattern])
    match_count = match_count_result[0] if match_count_result else 0

    # Get win count (Similar assumption about team names)
    win_count_query = """
    SELECT COUNT(*) FROM Matches m
    JOIN Teams t ON m.winner_team_id = t.team_id
    WHERE t.name LIKE ?
    """
    win_count_result = db.fetchone(win_count_query, [player_name_pattern])
    win_count = win_count_result[0] if win_count_result else 0

    # Calculate win rate
    win_rate = (win_count / match_count * 100) if match_count > 0 else 0

    return {
        **player,
        "current_elo": current_elo if current_elo is not None else 1500.0,  # Default ELO if none exists
        "matches_played": match_count,
        "wins": win_count,
        "win_rate": win_rate,
    }


@with_retry()
def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the current leaderboard based on ELO scores.
    Assumes a default ELO of 1500 for players without history.

    Parameters
    ----------
    limit : int
        Maximum number of players to include

    Returns
    -------
    List[Dict[str, Any]]
        Leaderboard entries
    """
    db = transaction()
    # This query fetches players and their latest ELO, ordering by ELO.
    # It uses a LEFT JOIN to include players even if they have no ELO history yet.
    # COALESCE is used to provide a default ELO of 1500.
    query = """
    SELECT 
        p.player_id, 
        p.name, 
        COALESCE(h.elo_score, 1500.0) as elo_score
    FROM Players p
    LEFT JOIN (
        SELECT player_id, MAX(updated_at) as latest_update
        FROM ELO_History
        GROUP BY player_id
    ) latest ON p.player_id = latest.player_id
    LEFT JOIN ELO_History h ON latest.player_id = h.player_id AND latest.latest_update = h.updated_at
    ORDER BY elo_score DESC
    LIMIT ?
    """

    leaderboard_players = db.fetchall(query, [limit])
    results = []

    # Now, for each player in the top list, fetch their stats
    for player_data in leaderboard_players:
        player_id = player_data[0]
        stats = get_player_stats(player_id)  # Re-use the stats function
        if stats:
            results.append(stats)

    # Re-sort based on the potentially updated ELO from stats (though it should match)
    results.sort(key=lambda x: x.get("current_elo", 1500.0), reverse=True)

    return results
