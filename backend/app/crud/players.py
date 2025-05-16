# -*- coding: utf-8 -*-
"""
Operations related to the Players table.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from app.crud.builders import (
    DeleteQueryBuilder,
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)
from app.crud.teams import create_team
from app.db.retry import with_retry
from app.db.transaction import transaction


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a player by name.

    Parameters
    ----------
    name : str
        Name of the player to find.

    Returns
    -------
    Optional[Dict[str, Any]]
        Player data if found, None otherwise.
    """
    try:
        query, params = SelectQueryBuilder("Players").where("name = ?", name).build()
        with transaction() as db_manager:
            player = db_manager.fetchone(query, params)

        if player:
            return dict(zip(["player_id", "name", "global_elo", "created_at"], player))
        return None
    except Exception as e:
        logger.error(f"Error getting player by name '{name}': {e}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def create_player(name: str, global_elo: int = 1000) -> Optional[int]:
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
            # ##: Dynamically create teams with existing players.
            all_players = get_all_players()
            for existing_player in all_players:
                existing_player_id = existing_player.get("player_id")
                if existing_player_id is not None and existing_player_id != new_player_id:
                    p1_id = min(new_player_id, existing_player_id)
                    p2_id = max(new_player_id, existing_player_id)
                    logger.info(f"Attempting to create team for players {p1_id} and {p2_id}.")
                    created_team_id = create_team(player1_id=p1_id, player2_id=p2_id)
                    if created_team_id:
                        logger.info(
                            f"Successfully created/ensured team for {p1_id} and {p2_id} with team ID: {created_team_id}"
                        )
                    else:
                        logger.info(f"Team for {p1_id} and {p2_id} already exists or could not be created.")
            return new_player_id
        else:
            logger.error(f"Failed to retrieve ID for new player '{name}'.")
            return None

    except Exception as exc:
        logger.error(f"Failed to create player '{name}': {exc}")
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
            SelectQueryBuilder("Players")
            .select(
                "player_id",
                "name",
                "global_elo",
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
                "created_at": result[3],
            }
        return None
    except Exception as exc:
        logger.error(f"Failed to get player by ID {player_id}: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def update_player(
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
    try:
        update_builder = UpdateQueryBuilder("Players")
        if name is not None:
            update_builder.set(name=name)
        if global_elo is not None:
            update_builder.set(global_elo=global_elo)
        if not update_builder.set_clauses:
            return False

        update_builder.where("player_id = ?", player_id)
        query, params = update_builder.build()

        with transaction() as db_manager:
            result = db_manager.fetchone(query, params)
            return bool(result[0])
    except Exception as exc:
        logger.error(f"Failed to update player ID {player_id}: {exc}")
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
        delete_builder = DeleteQueryBuilder("Players").where("player_id = ?", player_id)
        query, params = delete_builder.build()

        with transaction() as db_manager:
            result = db_manager.fetchone(query, params)
            return bool(result[0])
    except Exception as exc:
        logger.error(f"Failed to delete player ID {player_id}: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_players(players: List[Dict[str, Any]]) -> List[Optional[int]]:
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
            .order_by_clause("name")
            .execute()
        )
        return (
            [
                {
                    "player_id": row[0],
                    "name": row[1],
                    "global_elo": row[2],
                    "created_at": row[3],
                }
                for row in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get all players: {exc}")
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
            SelectQueryBuilder("Players")
            .select("player_id", "name", "global_elo", "created_at")
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
                    "created_at": row[3],
                }
                for row in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to search players with pattern '{name_pattern}': {exc}")
        return []
