"""
This module provides business logic and data transformation for player-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from typing import List

from loguru import logger

from app.db.repositories.players import (
    create_player,
    delete_player,
    get_all_players,
    get_player_by_name,
    update_player,
)
from app.db.repositories.stats import get_player_stats
from app.db.repositories.teams import create_team
from app.exceptions.players import (
    InvalidPlayerDataError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
    PlayerOperationError,
)
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate


def get_player_by_id(player_id: int) -> PlayerResponse:
    """
    Retrieve a player by their ID with associated statistics.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.

    Returns
    -------
    PlayerResponse
        The player's details with statistics.

    Raises
    ------
    PlayerNotFoundError
        If no player with the specified ID is found.
    PlayerOperationError
        If there's an error retrieving the player's data.
    """
    try:
        # ##: Get player statistics.
        stats = get_player_stats(player_id)
        if not stats:
            raise PlayerNotFoundError(f"No player found with ID {player_id}")

        return PlayerResponse(
            player_id=player_id,
            name=stats["name"],
            global_elo=stats["global_elo"],
            created_at=stats["created_at"],
            last_match_at=stats["last_match_at"],
            matches_played=stats.get("matches_played", 0),
            wins=stats.get("wins", 0),
            losses=stats.get("losses", 0),
            win_rate=stats.get("win_rate", 0.0),
        )
    except PlayerNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving player with ID {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to retrieve player with ID {player_id}") from exc


def create_new_player(player_data: PlayerCreate) -> PlayerResponse:
    """
    Create a new player with the provided data.

    Parameters
    ----------
    player_data : PlayerCreate
        The data for the new player.

    Returns
    -------
    PlayerResponse
        The created player's details with statistics.

    Raises
    ------
    InvalidPlayerDataError
        If the player data is invalid (e.g., empty name).
    PlayerAlreadyExistsError
        If a player with the same name already exists.
    PlayerOperationError
        If player creation fails.
    """
    # ##: Validate name.
    if not player_data.name or not player_data.name.strip():
        raise InvalidPlayerDataError("Player name cannot be empty or whitespace only")

    # ##: Check for existing player with same name.
    existing_player = get_player_by_name(player_data.name)
    if existing_player:
        raise PlayerAlreadyExistsError(player_data.name)

    try:
        # ##: Create the player.
        player_id = create_player(player_data.name, global_elo=player_data.global_elo)
        if not player_id:
            raise PlayerOperationError("Failed to create player in the database")

        # ##: Dynamically create teams with existing players.
        all_players = get_all_players()
        for existing_player in all_players:
            existing_player_id = existing_player.get("player_id")
            if existing_player_id is not None and existing_player_id != player_id:
                p1_id = min(player_id, existing_player_id)
                p2_id = max(player_id, existing_player_id)
                logger.info(f"Attempting to create team for players {p1_id} and {p2_id}.")
                created_team_id = create_team(player1_id=p1_id, player2_id=p2_id)
                if created_team_id:
                    logger.info(
                        f"Successfully created/ensured team for {p1_id} and {p2_id} with team ID: {created_team_id}"
                    )
                else:
                    logger.info(f"Team for {p1_id} and {p2_id} already exists or could not be created.")

        # ##: Return the complete player data.
        return get_player_by_id(player_id)
    except Exception as exc:
        logger.error(f"Error creating player '{player_data.name}': {exc}")
        raise PlayerOperationError(f"Failed to create player: {str(exc)}") from exc


def update_existing_player(player_id: int, player_update: PlayerUpdate) -> PlayerResponse:
    """
    Update an existing player's information.

    Parameters
    ----------
    player_id : int
        The ID of the player to update.
    player_update : PlayerUpdate
        The updated player data.

    Returns
    -------
    PlayerResponse
        The updated player's details.

    Raises
    ------
    PlayerNotFoundError
        If no player with the specified ID is found.
    PlayerAlreadyExistsError
        If another player with the new name already exists.
    PlayerOperationError
        If the update operation fails.
    """
    try:
        # ##: Check if player exists.
        existing_player = get_player_by_id(player_id)
        if not existing_player:
            raise PlayerNotFoundError(f"ID: {player_id}")

        # ##: If name is being updated, check for conflicts
        if player_update.name and player_update.name != existing_player.name:
            conflict_player = get_player_by_name(player_update.name)
            if conflict_player and conflict_player.player_id != player_id:
                raise PlayerAlreadyExistsError(player_update.name)

        # ##: Update the player.
        success = update_player(player_id=player_id, name=player_update.name)
        if not success:
            raise PlayerOperationError(f"Failed to update player with ID {player_id}")

        return get_player_by_id(player_id)
    except (PlayerNotFoundError, PlayerAlreadyExistsError):
        raise
    except Exception as exc:
        logger.error(f"Error updating player with ID {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to update player with ID {player_id}") from exc


# ##: TODO: Delete a player should also delete all teams and matches associated with it.
# and recalculate ELO ratings for all players.
def delete_player_by_id(player_id: int) -> bool:
    """
    Delete a player by their ID.

    Parameters
    ----------
    player_id : int
        The ID of the player to delete.

    Returns
    -------
    bool
        True if the player was deleted successfully, False otherwise.

    Raises
    ------
    PlayerOperationError
        If the deletion operation fails.
    """
    try:
        # ##: Check if player exists first
        existing_player = get_player_by_id(player_id)
        if not existing_player:
            raise PlayerNotFoundError(f"ID: {player_id}")

        success = delete_player(player_id)
        if not success:
            raise PlayerOperationError(f"Failed to delete player with ID {player_id}")
        return True
    except PlayerNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error deleting player with ID {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to delete player with ID {player_id}") from exc


def get_all_players_with_stats() -> List[PlayerResponse]:
    """
    Retrieve all players with their statistics.

    Returns
    -------
    List[PlayerResponse]
        A list of all players with their statistics.

    Raises
    ------
    PlayerOperationError
        If there's an error retrieving the players' data.
    """
    try:
        players = get_all_players()
        responses = []
        for player in players:
            player_id = player["player_id"]
            stats = get_player_stats(player_id)
            if not stats:
                logger.warning(f"No stats found for player ID {player_id}")
                stats = {
                    "matches_played": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0.0,
                    "last_match_at": None,
                }
            responses.append(
                PlayerResponse(
                    player_id=player_id,
                    name=player["name"],
                    global_elo=player["global_elo"],
                    created_at=player["created_at"],
                    last_match_at=stats["last_match_at"],
                    matches_played=stats.get("matches_played", 0),
                    wins=stats.get("wins", 0),
                    losses=stats.get("losses", 0),
                    win_rate=stats.get("win_rate", 0.0),
                )
            )
        return responses
    except Exception as exc:
        logger.error(f"Error retrieving all players with stats: {exc}")
        raise PlayerOperationError("Failed to retrieve all players with statistics") from exc
