# -*- coding: utf-8 -*-
"""
Operations related to the Players table using Supabase client.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

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
        with transaction() as db_client:
            response = (
                db_client.table("Players")
                .insert({"name": name, "global_elo": global_elo}, returning="representation")
                .execute()
            )

        if response.data and len(response.data) > 0:
            new_player_id = response.data[0].get("player_id")
            if new_player_id is not None:
                logger.info(f"Player '{name}' created with ID: {new_player_id}.")
                return new_player_id

        logger.error(f"Failed to create player '{name}'. Response: {response}")
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
    player_ids: List[Optional[int]] = []
    try:
        players_to_insert = [
            {"name": player["name"], "global_elo": player.get("global_elo", 1000)} for player in players
        ]

        if not players_to_insert:
            return []

        with transaction() as db_client:
            response = db_client.table("Players").insert(players_to_insert, returning="representation").execute()

        if response.data:
            for record in response.data:
                player_ids.append(record.get("player_id"))

            while len(player_ids) < len(players):
                player_ids.append(None)
        else:
            player_ids = [None] * len(players)
            logger.error(f"Batch insert failed or returned no data. Response: {response}")

        return player_ids
    except Exception as exc:
        logger.error(f"Failed during batch insert: {exc}")
        return [None] * len(players)


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_players() -> List[Dict[str, Any]]:
    """
    Get all players from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of player dictionaries, each including 'player_id', 'name', 'global_elo', 'created_at', 'rank'.
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("Players")
                .select("player_id, name, global_elo, created_at")
                .order("global_elo", desc=True)
                .execute()
            )

        if response.data:
            return [{**row, "rank": idx + 1} for idx, row in enumerate(response.data)]
        return []
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
    """
    if player_id is None and name is None:
        raise ValueError("Either player_id or name must be provided.")
    if player_id is not None and name is not None:
        raise ValueError("Cannot provide both player_id and name. Choose one.")

    try:
        with transaction() as db_client:
            query = db_client.table("Players").select("player_id, name, global_elo, created_at")
            if player_id is not None:
                query = query.eq("player_id", player_id)
            if name is not None:
                query = query.eq("name", name)

            response = query.maybe_single().execute()

        if response.data:
            return response.data
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

    Returns
    -------
    bool
        True if the player was updated successfully, False otherwise.
    """
    update_fields: Dict[str, Any] = {}
    if name is not None:
        update_fields["name"] = name
    if global_elo is not None:
        update_fields["global_elo"] = global_elo

    if not update_fields:
        logger.warning(f"No fields to update for player ID {player_id}.")
        return False

    try:
        with transaction() as db_client:
            response = db_client.table("Players").update(update_fields).eq("player_id", player_id).execute()

        updated_successfully = False
        if response.data and len(response.data) > 0:
            updated_successfully = True
        elif getattr(response, "count", 0) > 0:
            updated_successfully = True

        if updated_successfully:
            logger.info(f"Player ID {player_id} updated successfully.")
            return True

        logger.warning(f"Player ID {player_id} not found or no changes made during update. Response: {response}")
        return False

    except Exception as exc:
        logger.error(f"Failed to update player ID {player_id}: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def batch_update_players_elo(players: List[Dict[str, Any]]) -> bool:
    """
    Batch update player information (name or ELO).

    Parameters
    ----------
    players : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary must contain 'player_id' and
        optionally 'name' and/or 'global_elo' to update.

    Returns
    -------
    bool
        True if all updates in the batch were successful, False otherwise.
    """
    if not players:
        return True

    all_successful = True
    try:
        with transaction() as db_client:
            for player_data in players:
                player_id = player_data.get("player_id")
                if player_id is None:
                    logger.error(f"Missing player_id in batch update data: {player_data}")
                    all_successful = False
                    continue

                update_fields: Dict[str, Any] = {}
                if "name" in player_data:
                    update_fields["name"] = player_data["name"]
                if "global_elo" in player_data:
                    update_fields["global_elo"] = player_data["global_elo"]

                if not update_fields:
                    logger.warning(f"No fields to update for player_id {player_id} in batch.")
                    continue

                response = db_client.table("Players").update(update_fields).eq("player_id", player_id).execute()

                updated_this_player = False
                if response.data and len(response.data) > 0:
                    updated_this_player = True
                elif getattr(response, "count", 0) > 0:
                    updated_this_player = True

                if not updated_this_player:
                    all_successful = False
                    logger.warning(
                        f"Failed to update player_id {player_id} in batch or player not found/no change. Response: {response}"
                    )

        if all_successful:
            logger.info("Batch update of players completed successfully.")
        else:
            logger.warning("Batch update of players completed with one or more failures.")
        return all_successful

    except Exception as exc:
        logger.error(f"Error during batch update of players: {exc}")
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
        with transaction() as db_client:
            response = db_client.table("Players").delete().eq("player_id", player_id).execute()

        deleted_successfully = False
        if response.data and len(response.data) > 0:
            deleted_successfully = True
        elif getattr(response, "count", 0) > 0:
            deleted_successfully = True

        if deleted_successfully:
            logger.info(f"Player ID {player_id} deleted successfully.")
            return True

        logger.warning(f"Player ID {player_id} not found for deletion. Response: {response}")
        return False

    except Exception as exc:
        logger.error(f"Failed to delete player ID {player_id}: {exc}")
        return False
