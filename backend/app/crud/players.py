# -*- coding: utf-8 -*-
"""
Operations related to the Players table.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry

logger = getLogger(__name__)

from .elo_history import get_current_elo


@with_retry()
def create_player(name: str) -> Optional[int]:
    """
    Create a new player in the database.

    Parameters
    ----------
    name : str
        Name of the player

    Returns
    -------
    Optional[int]
        ID of the newly created player, or None on failure
    """
    with transaction() as db:
        cursor = db.execute("INSERT INTO Players (name) VALUES (?)", [name])
        if cursor.lastrowid:
            return cursor.lastrowid

        result = db.fetchone("SELECT last_insert_rowid()")
        return result[0] if result else None


@with_retry()
def get_player(player_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a player by ID.

    Parameters
    ----------
    player_id : int
        ID of the player to retrieve

    Returns
    -------
    Optional[Dict[str, Any]]
        Player data as a dictionary, or None if not found
    """
    db = DatabaseManager()
    result = db.fetchone("SELECT player_id, name, created_at FROM Players WHERE player_id = ?", [player_id])
    if result:
        return {"player_id": result[0], "name": result[1], "created_at": result[2]}
    return None


@with_retry()
def get_all_players() -> List[Dict[str, Any]]:
    """
    Get all players from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of player dictionaries
    """
    db = DatabaseManager()
    results = db.fetchall("SELECT player_id, name, created_at FROM Players ORDER BY name")
    return [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in results] if results else []


@with_retry()
def update_player(player_id: int, name: str) -> bool:
    """
    Update a player's information.

    Parameters
    ----------
    player_id : int
        ID of the player to update
    name : str
        New name for the player

    Returns
    -------
    bool
        True if update affected at least one row, False otherwise
    """
    with transaction() as db:
        cursor = db.execute("UPDATE Players SET name = ? WHERE player_id = ?", [name, player_id])
        return cursor.rowcount > 0


@with_retry()
def delete_player(player_id: int) -> bool:
    """
    Delete a player from the database.

    Parameters
    ----------
    player_id : int
        ID of the player to delete

    Returns
    -------
    bool
        True if deletion affected at least one row, False otherwise
    """
    with transaction() as db:
        cursor = db.execute("DELETE FROM Players WHERE player_id = ?", [player_id])
        return cursor.rowcount > 0


@with_retry()
def batch_insert_players(players: List[Dict[str, str]]) -> List[Optional[int]]:
    """
    Insert multiple players in a single transaction.

    Parameters
    ----------
    players : List[Dict[str, str]]
        List of player dictionaries, each with a 'name' key

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created players, or None for failures
    """
    player_ids = []
    with transaction() as db:
        for player in players:
            db.execute("INSERT INTO Players (name) VALUES (?)", [player["name"]])
            result = db.fetchone("SELECT last_insert_rowid()")
            player_ids.append(result[0] if result else None)

    return player_ids


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

    # ##: Get player details.
    player = get_player(player_id)
    if not player:
        return None

    # ##: Get current ELO.
    current_elo = get_current_elo(player_id)

    # ##: Get match count.
    match_count_query = """
    SELECT COUNT(DISTINCT m.match_id) FROM Matches m
    JOIN Teams t1 ON m.team1_id = t1.team_id
    JOIN Teams t2 ON m.team2_id = t2.team_id
    WHERE t1.player1_id = ? OR t1.player2_id = ? OR t2.player1_id = ? OR t2.player2_id = ?
    """
    match_count_result = db.fetchone(match_count_query, [player_id, player_id, player_id, player_id])
    match_count = match_count_result[0] if match_count_result else 0

    # ##: Get win count.
    win_count_query = """
    SELECT COUNT(*) FROM Matches m
    JOIN Teams t ON m.winner_team_id = t.team_id
    WHERE t.player1_id = ? OR t.player2_id = ?
    """
    win_count_result = db.fetchone(win_count_query, [player_id, player_id])
    win_count = win_count_result[0] if win_count_result else 0

    # ##: Calculate win rate.
    win_rate = (win_count / match_count * 100) if match_count > 0 else 0

    return {
        **player,
        "current_elo": current_elo if current_elo is not None else 1000.0,
        "matches_played": match_count,
        "wins": win_count,
        "win_rate": win_rate,
    }


@with_retry()
def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the current leaderboard based on ELO scores.
    Assumes a default ELO of 1000 for players without history.

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
    query = """
    SELECT
        p.player_id,
        p.name,
        COALESCE(h.elo_score, 1000.0) as elo_score
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

    # ##: Now, for each player in the top list, fetch their stats.
    for player_data in leaderboard_players:
        player_id_from_lb = player_data[0]
        stats = get_player_stats(player_id_from_lb)
        if stats:
            results.append(stats)

    # ##: Re-sort based on the potentially updated ELO from stats (though it should match).
    results.sort(key=lambda x: x.get("current_elo", 1000.0), reverse=True)

    return results
