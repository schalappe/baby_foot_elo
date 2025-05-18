"""
This module provides business logic and data transformation for player-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from typing import List

from loguru import logger

from app.db.repositories.matches import get_matches_by_player
from app.db.repositories.players import (
    create_player,
    delete_player,
    get_all_players,
    get_player,
    get_player_by_name,
    update_player,
)
from app.db.repositories.stats import get_player_stats
from app.db.repositories.teams import get_team
from app.exceptions.players import (
    InvalidPlayerDataError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
    PlayerOperationError,
)
from app.models.elo_history import EloHistoryResponse
from app.models.match import MatchWithEloResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.models.team import TeamResponse


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
        # ##: Get basic player data.
        player = get_player(player_id)
        if not player:
            raise PlayerNotFoundError(f"ID: {player_id}")

        # ##: Get player statistics.
        stats = get_player_stats(player_id)
        if not stats:
            logger.warning(f"No stats found for player ID {player_id}")
            stats = {
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
            }
        return PlayerResponse(
            player_id=player_id,
            name=player["name"],
            global_elo=player["global_elo"],
            created_at=player["created_at"],
            last_match_at=stats["last_match_at"],
            matches_played=stats.get("matches_played", 0),
            wins=stats.get("wins", 0),
            losses=stats.get("losses", 0),
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

        # ##: Return the complete player data.
        return get_player_by_id(player_id)
    except Exception as e:
        logger.error(f"Error creating player '{player_data.name}': {e}")
        raise PlayerOperationError(f"Failed to create player: {str(e)}") from e


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
        if player_update.name and player_update.name != existing_player["name"]:
            conflict_player = get_player_by_name(player_update.name)
            if conflict_player and conflict_player["player_id"] != player_id:
                raise PlayerAlreadyExistsError(player_update.name)

        # ##: Update the player.
        success = update_player(player_id=player_id, name=player_update.name)
        if not success:
            raise PlayerOperationError(f"Failed to update player with ID {player_id}")

        return get_player_by_id(player_id)
    except (PlayerNotFoundError, PlayerAlreadyExistsError):
        raise
    except Exception as e:
        logger.error(f"Error updating player with ID {player_id}: {e}")
        raise PlayerOperationError(f"Failed to update player with ID {player_id}") from e


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
        existing_player = get_player(player_id)
        if not existing_player:
            raise PlayerNotFoundError(f"ID: {player_id}")

        success = delete_player(player_id)
        if not success:
            raise PlayerOperationError(f"Failed to delete player with ID {player_id}")
        return True
    except PlayerNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting player with ID {player_id}: {e}")
        raise PlayerOperationError(f"Failed to delete player with ID {player_id}") from e


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
        players = []
        for player in get_all_players():
            player_id = player["player_id"]
            try:
                player_response = get_player_by_id(player_id)
                if player_response:
                    players.append(player_response)
            except PlayerNotFoundError:
                logger.warning(f"Player with ID {player_id} not found but listed in players")
                continue
            except Exception as e:
                logger.error(f"Error processing player {player_id}: {e}")
                continue
        return players
    except Exception as e:
        logger.error(f"Error retrieving all players: {e}")
        raise PlayerOperationError("Failed to retrieve players") from e


def get_player_matches(player_id: int, limit: int = 10, offset: int = 0, **filters) -> List[MatchWithEloResponse]:
    """
    Retrieve a paginated list of matches for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    limit : int, optional
        Maximum number of matches to return (default: 10).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).
    **filters
        Additional filters for the matches (e.g., start_date, end_date).

    Returns
    -------
    List[MatchWithEloResponse]
        A list of matches the player participated in.
    """
    try:
        matches = get_matches_by_player(player_id, limit, offset, **filters)

        # ##: Convert to response model.
        # ##: TODO: Optimize this by using a single query to get all teams and players.
        response = []
        for match in matches:
            winner_team = get_team(match["winner_team_id"])
            loser_team = get_team(match["loser_team_id"])
            match_response = MatchWithEloResponse(**match)
            match_response.winner_team = TeamResponse(
                **winner_team,
                player1=get_player_by_id(winner_team["player1_id"]),
                player2=get_player_by_id(winner_team["player2_id"]),
            )
            match_response.loser_team = TeamResponse(
                **loser_team,
                player1=get_player_by_id(loser_team["player1_id"]),
                player2=get_player_by_id(loser_team["player2_id"]),
            )
            response.append(match_response)

        return response
    except Exception as e:
        logger.error(f"Error retrieving matches for player {player_id}: {e}")
        return []
