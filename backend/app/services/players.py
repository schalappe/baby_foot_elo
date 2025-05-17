"""
This module provides business logic and data transformation for player-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from typing import Dict, List, Optional

from loguru import logger

from app.db.repositories.elo_history import get_player_elo_history
from app.db.repositories.matches import get_matches_by_player
from app.db.repositories.players import (
    create_player,
    delete_player,
    get_all_players,
    get_player,
    get_player_by_name,
    update_player,
    get_player_stats,
)
from app.models.elo_history import EloHistoryResponse
from app.models.match import MatchWithEloResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate


def get_player_by_id(player_id: int) -> Optional[PlayerResponse]:
    """
    Retrieve a player by their ID with associated statistics.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.


    Returns
    -------
    Optional[PlayerResponse]
        The player's details with statistics if found, None otherwise.
    """
    try:
        # ##: Get basic player data.
        player = get_player(player_id)
        if not player:
            return None

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
            matches_played=stats.get("matches_played", 0),
            wins=stats.get("wins", 0),
            losses=stats.get("losses", 0),
        )
    except Exception as e:
        logger.error(f"Error retrieving player with ID {player_id}: {e}")
        return None


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
    ValueError
        If player creation fails or if a player with the same name exists.
    """
    # ##: Validate name.
    if not player_data.name.strip():
        raise ValueError("Player name cannot be empty or whitespace only")

    # ##: Check for existing player with same name.
    existing_player = get_player_by_name(player_data.name)
    if existing_player:
        raise ValueError(f"A player with the name '{player_data.name}' already exists")

    # ##: Create the player.
    player_id = create_player(player_data.name, global_elo=player_data.global_elo)
    if not player_id:
        raise ValueError("Failed to create player")

    # ##: Return the complete player data.
    return get_player_by_id(player_id)


def update_existing_player(player_id: int, player_update: PlayerUpdate) -> Optional[PlayerResponse]:
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
    Optional[PlayerResponse]
        The updated player's details if successful, None otherwise.
    """
    # ##: Check if player exists.
    existing_player = get_player(player_id)
    if not existing_player:
        return None

    # ##: Check for name conflict if name is being updated.
    if player_update.name and player_update.name != existing_player["name"]:
        conflict_player = get_player_by_name(player_update.name)
        if conflict_player and conflict_player["player_id"] != player_id:
            raise ValueError(f"Another player with the name '{player_update.name}' already exists")

    # ##: Update the player.
    success = update_player(player_id=player_id, name=player_update.name)

    if not success:
        return None

    return get_player_by_id(player_id)


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
    """
    return delete_player(player_id)


def get_all_players_with_stats() -> List[PlayerResponse]:
    """
    Retrieve all players with their statistics.

    Returns
    -------
    List[PlayerResponse]
        A list of all players with their statistics.
    """
    players = []
    for player in get_all_players():
        player_id = player["player_id"]
        try:
            player_response = get_player_by_id(player_id)
            if player_response:
                players.append(player_response)
        except Exception as e:
            logger.error(f"Error processing player {player_id}: {e}")
    return players

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
                player1=get_player(winner_team["player1_id"]),
                player2=get_player(winner_team["player2_id"]),
            )
            match_response.loser_team = TeamResponse(
                **loser_team,
                player1=get_player(loser_team["player1_id"]),
                player2=get_player(loser_team["player2_id"]),
            )
            response.append(match_response)

        return response
    except Exception as e:
        logger.error(f"Error retrieving matches for player {player_id}: {e}")
        return []

def get_player_elo_history(player_id: int, limit: int = 20, offset: int = 0, **filters) -> List[EloHistoryResponse]:
    """
    Retrieve ELO history for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    limit : int, optional
        Maximum number of history records to return (default: 20).
    offset : int, optional
        Number of records to skip for pagination (default: 0).
    **filters
        Additional filters for the history (e.g., start_date, end_date, elo_type).

    Returns
    -------
    List[EloHistoryResponse]
        A list of ELO history records for the player.
    """
    try:
        history = get_player_elo_history(player_id, limit, offset, **filters)
        return [EloHistoryResponse(**record) for record in history] if history else []
    except Exception as e:
        logger.error(f"Error retrieving ELO history for player {player_id}: {e}")
        return []

def get_player_statistics(player_id: int) -> Dict[str, Any]:
    """
    Retrieve statistics for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.


    Returns
    -------
    Dict[str, Any]
        A dictionary containing the player's statistics.
    """
    try:
        stats = get_player_stats(player_id)
        if not stats:
            return {
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "current_streak": 0,
                "best_streak": 0,
                "worst_streak": 0,
                "average_elo_change": 0,
                "highest_elo": 0,
                "lowest_elo": 0,
            }
        return stats
    except Exception as e:
        logger.error(f"Error retrieving statistics for player {player_id}: {e}")
        raise