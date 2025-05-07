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
        # Use QueryBuilder for SELECT
        result = QueryBuilder("Players").where("player_id = ?", player_id).execute(fetch_all=False)
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
        rows = QueryBuilder("Players").order_by_clause("name").execute()
        return (
            [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in rows]
            if rows
            else []
        )
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
            result = db_manager.fetchone(
                "UPDATE Players SET name = ? WHERE player_id = ? RETURNING player_id",
                [name, player_id],
            )
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
            result = db_manager.fetchone(
                "DELETE FROM Players WHERE player_id = ? RETURNING player_id", [player_id]
            )
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
        rows = (
            QueryBuilder("Players")
            .where("name LIKE ?", f"%{name_pattern}%")
            .order_by_clause("name")
            .limit(limit)
            .execute()
        )
        return (
            [{"player_id": row[0], "name": row[1], "created_at": row[2]} for row in rows]
            if rows
            else []
        )
    except Exception as e:
        logger.error("Failed to search players with pattern '%s': %s", name_pattern, e)
        return []
