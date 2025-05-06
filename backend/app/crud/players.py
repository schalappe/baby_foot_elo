# -*- coding: utf-8 -*-
"""
Operations related to the Players table.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.db.database import DatabaseManager
from app.db.retry import with_retry
from app.db.transaction import transaction

logger = logging.getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone(
                "INSERT INTO Players (name) VALUES (?) RETURNING player_id", [name]
            )
        return result[0] if result else None
    except Exception as e:
        logger.error("Failed to create player '%s': %s", name, e)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone("SELECT * FROM Players WHERE player_id = ?", [player_id])
            if result:
                return {"player_id": result[0], "name": result[1], "created_at": result[2]}
            return None
    except Exception as e:
        logger.error("Failed to get player by ID %d: %s", player_id, e)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_players() -> List[Dict[str, Any]]:
    """
    Get all players from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of player dictionaries
    """
    try:
        with transaction() as db_manager:
            results = db_manager.fetchall("SELECT * FROM Players ORDER BY name")
            return [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in results] if results else []
    except Exception as e:
        logger.error("Failed to get all players: %s", e)
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def update_player(player_id: int, name: str) -> bool:
    """
    Update an existing player's name.

    Parameters
    ----------
    player_id : int
        ID of the player to update.
    name : str
        New name for the player.

    Returns
    -------
    bool
        True if the player was updated successfully, False otherwise
    """
    try:
        with transaction() as db_manager:
            # Use RETURNING to check if a row was actually updated
            result = db_manager.fetchone(
                "UPDATE Players SET name = ? WHERE player_id = ? RETURNING player_id",
                [name, player_id]
            )
            # Return True if fetchone returned a result (a row was updated)
            return result is not None
    except Exception as e:
        logger.error("Failed to update player ID %d: %s", player_id, e)
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def delete_player(player_id: int) -> bool:
    """
    Delete a player from the database.

    Parameters
    ----------
    player_id : int
        ID of the player to delete.

    Returns
    -------
    bool
        True if the player was deleted successfully, False otherwise
    """
    try:
        with transaction() as db_manager:
            # Use RETURNING to check if a row was actually deleted
            result = db_manager.fetchone(
                "DELETE FROM Players WHERE player_id = ? RETURNING player_id",
                [player_id]
            )
            # Return True if fetchone returned a result (a row was deleted)
            return result is not None
    except Exception as e:
        logger.error("Failed to delete player ID %d: %s", player_id, e)
        return False


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
            for player in players:
                result = db_manager.fetchone(
                    "INSERT INTO Players (name) VALUES (?) RETURNING player_id",
                    [player["name"]],
                )
                player_ids.append(result[0] if result else None)
        return player_ids
    except Exception as e:
        logger.error("Failed during batch insert: %s", e)
        return player_ids


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
            query = """
            SELECT *
            FROM Players
            WHERE name LIKE ?
            ORDER BY name
            LIMIT ?
            """
            results = db_manager.fetchall(query, [f"%{name_pattern}%", limit])
            return [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in results] if results else []
    except Exception as e:
        logger.error("Failed to search players with pattern '%s': %s", name_pattern, e)
        return []


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
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
            match_count_result = db_manager.fetchone(match_count_query, [player_id, player_id, player_id, player_id])
            match_count = match_count_result[0] if match_count_result else 0

            # ##: Get win count.
            win_count_query = """
            SELECT COUNT(*) FROM Matches m
            JOIN Teams t ON m.winner_team_id = t.team_id
            WHERE t.player1_id = ? OR t.player2_id = ?
            """
            win_count_result = db_manager.fetchone(win_count_query, [player_id, player_id])
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
    except Exception as e:
        logger.error("Failed to get player stats for ID %d: %s", player_id, e)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
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

            leaderboard_players = db_manager.fetchall(query, [limit])
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
    except Exception as e:
        logger.error("Failed to get leaderboard: %s", e)
        return []
