"""
This module provides business logic and data transformation for player-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from typing import List

from loguru import logger

from app.db.repositories.players import (
    create_player_by_name,
    delete_player_by_id,
    get_all_players,
    get_player_by_id_or_name,
    update_player_name_or_elo,
)
from app.db.repositories.players_elo_history import get_player_elo_history_by_id
from app.db.repositories.stats import get_player_stats
from app.db.repositories.teams import create_team_by_player_ids
from app.exceptions.players import (
    InvalidPlayerDataError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
    PlayerOperationError,
)
from app.models.elo_history import EloHistoryResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate


def get_player(player_id: int) -> PlayerResponse:
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


# ##: TODO: Delete a player should also delete all teams and matches associated with it.
# and recalculate ELO ratings for all players.
def delete_player(player_id: int) -> bool:
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

        success = delete_player_by_id(player_id)
        if not success:
            raise PlayerOperationError(f"Failed to delete player with ID {player_id}")
        return True
    except PlayerNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error deleting player with ID {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to delete player with ID {player_id}") from exc


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
    existing_player = get_player_by_id_or_name(name=player_data.name)
    if existing_player:
        raise PlayerAlreadyExistsError(player_data.name)

    try:
        # ##: Create the player.
        player_id = create_player_by_name(player_data.name, global_elo=player_data.global_elo)
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
                created_team_id = create_team_by_player_ids(player1_id=p1_id, player2_id=p2_id)
                if created_team_id:
                    logger.info(
                        f"Successfully created/ensured team for {p1_id} and {p2_id} with team ID: {created_team_id}"
                    )
                else:
                    logger.info(f"Team for {p1_id} and {p2_id} already exists or could not be created.")

        # ##: Return the complete player data.
        return get_player(player_id)
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
        existing_player = get_player(player_id)
        if not existing_player:
            raise PlayerNotFoundError(f"ID: {player_id}")

        # ##: If name is being updated, check for conflicts
        if player_update.name and player_update.name != existing_player.name:
            conflict_player = get_player_by_id_or_name(name=player_update.name)
            if conflict_player and conflict_player.player_id != player_id:
                raise PlayerAlreadyExistsError(player_update.name)

        # ##: Update the player.
        success = update_player_name_or_elo(
            player_id=player_id, name=player_update.name, global_elo=player_update.global_elo
        )
        if not success:
            raise PlayerOperationError(f"Failed to update player with ID {player_id}")

        return get_player(player_id)
    except (PlayerNotFoundError, PlayerAlreadyExistsError):
        raise
    except Exception as exc:
        logger.error(f"Error updating player with ID {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to update player with ID {player_id}") from exc


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
        responses = [PlayerResponse(**player) for player in players]
        return responses
    except Exception as exc:
        logger.error(f"Error retrieving all players with stats: {exc}")
        raise PlayerOperationError("Failed to retrieve all players with statistics") from exc


def get_player_elo_history(player_id: int, limit: int = 100, offset: int = 0, **filters) -> List[EloHistoryResponse]:
    """
    Retrieve a paginated list of ELO history records for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    limit : int, optional
        Maximum number of records to return (default: 100).
    offset : int, optional
        Number of records to skip for pagination (default: 0).
    **filters
        Additional filters for the ELO history (e.g., start_date, end_date).

    Returns
    -------
    List[EloHistoryResponse]
        A list of ELO history records for the player.
    """
    try:
        elo_history = get_player_elo_history_by_id(player_id, limit, offset, **filters)
        return [EloHistoryResponse(**history) for history in elo_history]
    except Exception as exc:
        logger.error(f"Error retrieving ELO history for player {player_id}: {exc}")
        raise PlayerOperationError(f"Failed to retrieve ELO history for player {player_id}") from exc
