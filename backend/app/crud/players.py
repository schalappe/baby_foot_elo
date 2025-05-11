# -*- coding: utf-8 -*-
"""
Operations related to the Players table.
"""

import logging
from typing import Any, Dict, List, Optional

from app.db.retry import with_retry
from app.db.transaction import transaction

from .builders import QueryBuilder

logger = logging.getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def create_player(name: str, global_elo: int = 1000, current_month_elo: int = 1000) -> Optional[int]:
    """
    Create a new player in the database.

    Parameters
    ----------
    name : str
        Name of the player.
    global_elo : int, optional
        Initial global ELO rating (default 1000).
    current_month_elo : int, optional
        Initial current month ELO rating (default 1000).

    Returns
    -------
    Optional[int]
        ID of the newly created player, or None on failure.
    """
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone(
                "INSERT INTO Players (name, global_elo, current_month_elo) VALUES (?, ?, ?) RETURNING player_id",
                [name, global_elo, current_month_elo],
            )
        return result[0] if result else None
    except Exception as exc:
        logger.error("Failed to create player '%s': %s", name, exc)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_player(player_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a player by ID.

    Parameters
    ----------
    player_id : int
        ID of the player to retrieve.

    Returns
    -------
    Optional[Dict[str, Any]]
        Player data as a dictionary, or None if not found.
    """
    try:
        result = (
            QueryBuilder("Players")
            .select(
                "player_id",
                "name",
                "global_elo",
                "current_month_elo",
                "created_at",
            )
            .where("player_id = ?", player_id)
            .execute(fetch_all=False)
        )
        if result:
            return {
                "player_id": result[0],
                "name": result[1],
                "global_elo": result[2],
                "current_month_elo": result[3],
                "created_at": result[4],
            }
        return None
    except Exception as exc:
        logger.error("Failed to get player by ID %d: %s", player_id, exc)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def update_player(
    player_id: int,
    name: Optional[str] = None,
    global_elo: Optional[int] = None,
    current_month_elo: Optional[int] = None,
) -> bool:
    """
    Update an existing player's attributes.

    Parameters
    ----------
    player_id : int
        ID of the player to update.
    name : Optional[str], optional
        New name for the player.
    global_elo : Optional[int], optional
        New global ELO rating.
    current_month_elo : Optional[int], optional
        New current month ELO rating.

    Returns
    -------
    bool
        True if the player was updated successfully, False otherwise.
    """
    try:
        fields = []
        params = []
        if name is not None:
            fields.append("name = ?")
            params.append(name)
        if global_elo is not None:
            fields.append("global_elo = ?")
            params.append(global_elo)
        if current_month_elo is not None:
            fields.append("current_month_elo = ?")
            params.append(current_month_elo)
        if not fields:
            return False
        params.append(player_id)
        query = f"UPDATE Players SET {', '.join(fields)} WHERE player_id = ? RETURNING player_id"
        with transaction() as db_manager:
            result = db_manager.fetchone(query, params)
            return result is not None
    except Exception as exc:
        logger.error("Failed to update player ID %d: %s", player_id, exc)
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
            result = db_manager.fetchone("DELETE FROM Players WHERE player_id = ? RETURNING player_id", [player_id])
            return result is not None
    except Exception as exc:
        logger.error("Failed to delete player ID %d: %s", player_id, exc)
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_players(players: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Insert multiple players in a single transaction.

    Parameters
    ----------
    players : List[Dict[str, Any]]
        List of player dictionaries, each with at least a 'name' key. Optional: 'global_elo', 'current_month_elo'.

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created players, or None for failures.
    """
    player_ids = []
    try:
        with transaction() as db_manager:
            for player in players:
                name = player["name"]
                global_elo = player.get("global_elo", 1000)
                current_month_elo = player.get("current_month_elo", 1000)
                result = db_manager.fetchone(
                    "INSERT INTO Players (name, global_elo, current_month_elo) VALUES (?, ?, ?) RETURNING player_id",
                    [name, global_elo, current_month_elo],
                )
                player_ids.append(result[0] if result else None)
        return player_ids
    except Exception as exc:
        logger.error("Failed during batch insert: %s", exc)
        return player_ids


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_players() -> List[Dict[str, Any]]:
    """
    Get all players from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of player dictionaries, each including 'player_id', 'name', 'global_elo', 'current_month_elo', 'created_at'.
    """
    try:
        rows = (
            QueryBuilder("Players")
            .select("player_id", "name", "global_elo", "current_month_elo", "created_at")
            .order_by_clause("name")
            .execute()
        )
        return (
            [
                {
                    "player_id": row[0],
                    "name": row[1],
                    "global_elo": row[2],
                    "current_month_elo": row[3],
                    "created_at": row[4],
                }
                for row in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error("Failed to get all players: %s", exc)
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def search_players(name_pattern: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for players by name pattern.

    Parameters
    ----------
    name_pattern : str
        Name pattern to search for.
    limit : int, optional
        Maximum number of results to return (default 10).

    Returns
    -------
    List[Dict[str, Any]]
        List of matching player dictionaries.
    """
    try:
        rows = (
            QueryBuilder("Players")
            .select("player_id", "name", "global_elo", "current_month_elo", "created_at")
            .where("name LIKE ?", f"%{name_pattern}%")
            .order_by_clause("name")
            .limit(limit)
            .execute()
        )
        return (
            [
                {
                    "player_id": row[0],
                    "name": row[1],
                    "global_elo": row[2],
                    "current_month_elo": row[3],
                    "created_at": row[4],
                }
                for row in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error("Failed to search players with pattern '%s': %s", name_pattern, exc)
        return []
