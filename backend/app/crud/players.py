# -*- coding: utf-8 -*-
"""
CRUD operations for Players.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry

logger = getLogger(__name__)


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
