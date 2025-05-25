# -*- coding: utf-8 -*-
"""
Operations related to the Players table.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from app.db.builders import (
    DeleteQueryBuilder,
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)
from app.db.session.retry import with_retry
from app.db.session.transaction import transaction


@with_retry(max_retries=3, retry_delay=0.5)
def create_player_by_name(name: str, global_elo: int = 1000) -> Optional[int]:
    """
    Create a new player in the database.

    Parameters
    ----------
    name : str
        Name of the player.
    global_elo : int, optional
        Initial global ELO rating (default 1000).

    Returns
    -------
    Optional[int]
        ID of the newly created player, or None on failure.
    """
    try:
        result = InsertQueryBuilder("Players").set(name=name, global_elo=global_elo).build()

        query, params = result
        new_player_id: Optional[int] = None
        with transaction() as db_manager:
            res = db_manager.fetchone(f"{query} RETURNING player_id", params)
            if res and res[0]:
                new_player_id = res[0]

        if new_player_id is not None:
            logger.info(f"Player '{name}' created with ID: {new_player_id}.")
            return new_player_id

        logger.error(f"Failed to create player '{name}'.")
        return None

    except Exception as exc:
        logger.error(f"Failed to create player '{name}': {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_players_by_name(players: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Insert multiple players in a single transaction.

    Parameters
    ----------
    players : List[Dict[str, Any]]
        List of player dictionaries, each with at least a 'name' key. Optional: 'global_elo'.

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
                query, params = InsertQueryBuilder("Players").set(name=name, global_elo=global_elo).build()
                result = db_manager.fetchone(f"{query} RETURNING player_id", params)
                player_ids.append(result[0] if result else None)
        return player_ids
    except Exception as exc:
        logger.error(f"Failed during batch insert: {exc}")
        return player_ids


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_players() -> List[Dict[str, Any]]:
    """
    Get all players from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of player dictionaries, each including 'player_id', 'name', 'global_elo', 'created_at'.
    """
    try:
        rows = (
            SelectQueryBuilder("Players")
            .select("player_id", "name", "global_elo", "created_at")
            .order_by_clause("global_elo DESC")
            .execute()
        )
        return (
            [
                {
                    "player_id": row[0],
                    "name": row[1],
                    "global_elo": row[2],
                    "created_at": row[3],
                    "rank": idx + 1,
                }
                for idx, row in enumerate(rows)
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get all players: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_by_id_or_name(player_id: Optional[int] = None, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a player by ID or name.

    Parameters
    ----------
    player_id : Optional[int]
        ID of the player to retrieve.
    name : Optional[str]
        Name of the player to find.

    Returns
    -------
    Optional[Dict[str, Any]]
        Player data as a dictionary, or None if not found.

    Raises
    ------
    ValueError
        If neither player_id nor name is provided.
        If both player_id and name are provided.
    """
    if player_id is None and name is None:
        raise ValueError("Either player_id or name must be provided.")
    if player_id is not None and name is not None:
        raise ValueError("Cannot provide both player_id and name.")

    try:
        query_builder = SelectQueryBuilder("Players").select("player_id", "name", "global_elo", "created_at")
        if player_id is not None:
            query_builder.where("player_id = ?", player_id)
        if name is not None:
            query_builder.where("name = ?", name)

        result = query_builder.execute(fetch_all=False)
        if result:
            return {
                "player_id": result[0],
                "name": result[1],
                "global_elo": result[2],
                "created_at": result[3],
            }
        return None
    except Exception as exc:
        logger.error(f"Failed to get player by ID {player_id} or name {name}: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def update_player_name_or_elo(
    player_id: int,
    name: Optional[str] = None,
    global_elo: Optional[int] = None,
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
    update_fields = {}
    if name is not None:
        update_fields["name"] = name
    if global_elo is not None:
        update_fields["global_elo"] = global_elo

    if not update_fields:
        logger.warning(f"No fields to update for player ID {player_id}.")
        return False

    try:
        query, params = UpdateQueryBuilder("Players").set(**update_fields).where("player_id = ?", player_id).build()
        with transaction() as db_manager:
            db_manager.execute(query, params)
        logger.info(f"Player ID {player_id} updated successfully.")
        return True
    except Exception as exc:
        logger.error(f"Failed to update player ID {player_id}: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def batch_update_players_elo(players: List[Dict[str, Any]]) -> bool:
    """
    Batch update player information.

    Parameters
    ----------
    players : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary contains 'player_id' and
        the fields to update (e.g., 'global_elo', 'name').

    Returns
    -------
    bool
        True if the batch update was successful, False otherwise.
    """
    try:
        with transaction() as db_manager:
            for player_data in players:
                player_id = player_data.get("player_id")
                if player_id is None:
                    logger.warning("Skipping player update due to missing player_id.")
                    continue

                update_fields = {key: value for key, value in player_data.items() if key != "player_id"}
                if not update_fields:
                    logger.warning(f"No fields to update for player ID {player_id}.")
                    continue

                query, params = (
                    UpdateQueryBuilder("Players").set(**update_fields).where("player_id = ?", player_id).build()
                )
                db_manager.execute(query, params)
        logger.info("Batch update of players completed successfully.")
        return True
    except Exception as exc:
        logger.error(f"Failed during batch update of players: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def delete_player_by_id(player_id: int) -> bool:
    """
    Delete a player by ID.

    Parameters
    ----------
    player_id : int
        ID of the player to delete.

    Returns
    -------
    bool
        True if the player was deleted successfully, False otherwise.
    """
    try:
        query, params = DeleteQueryBuilder("Players").where("player_id = ?", player_id).build()
        with transaction() as db_manager:
            result = db_manager.fetchone(query, params)
            return bool(result[0])
    except Exception as exc:
        logger.error(f"Failed to delete player ID {player_id}: {exc}")
        return False
