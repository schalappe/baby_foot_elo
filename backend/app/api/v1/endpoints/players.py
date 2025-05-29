"""
This module defines FastAPI endpoints for managing players in the Baby Foot Elo system.
It supports creating, listing, retrieving, updating, and deleting player records, as well as fetching player statistics.

Endpoints:
    - POST /players/: Create a new player
    - GET /players/: List all players
    - GET /players/{player_id}: Retrieve a player's details
    - PUT /players/{player_id}: Update a player's information
    - DELETE /players/{player_id}: Delete a player
    - GET /players/{player_id}/matches: Get player's match history
    - GET /players/{player_id}/elo-history: Get player's ELO history
    - GET /players/{player_id}/statistics: Get player's statistics

Notes
-----
- All endpoints return or accept Pydantic models for request and response bodies.
- ELO updates are not supported via the update endpoint.
- All endpoints include proper validation and error handling.
- Rate limiting is applied to prevent abuse.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from loguru import logger

from app.exceptions.players import (
    InvalidPlayerDataError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
    PlayerOperationError,
)
from app.models.elo_history import EloHistoryResponse
from app.models.match import MatchWithEloResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.services import players as player_service
from app.services import stats as stats_service
from app.utils.error_handlers import ErrorResponse

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad request",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Resource not found",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ErrorResponse,
            "description": "Rate limit exceeded",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal server error",
        },
    },
)


@router.post(
    "/",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new player",
    description="Creates a new player in the system with the provided name and optional initial ELO ratings.",
)
async def create_player_endpoint(player: PlayerCreate):
    """
    Create a new player and return the player's details.

    Parameters
    ----------
    player : PlayerCreate
        The player creation data (name required).

    Returns
    -------
    PlayerResponse
        The created player's details, including ELO and statistics.

    Raises
    ------
    HTTPException
        If player creation or fetching stats fails.
    """
    try:
        created_player = player_service.create_new_player(player_data=player)
        return created_player
    except InvalidPlayerDataError as exc:
        logger.warning(f"Invalid player data for creation: {exc.detail}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail)
    except PlayerAlreadyExistsError as exc:
        logger.info(f"Attempt to create player that already exists: {exc.detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.detail)
    except PlayerOperationError as exc:
        logger.error(f"Player operation error during creation: {exc.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error creating player: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the player",
        )


@router.get(
    "/",
    response_model=List[PlayerResponse],
    summary="List all players",
    description="Retrieves a list of all players with their details and statistics.",
)
async def list_players_endpoint(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of players to return"),
    offset: int = Query(0, ge=0, description="Number of players to skip"),
):
    """
    List all players with their details and statistics.

    Parameters
    ----------
    limit : int, optional
        Maximum number of players to return (default: 50, max: 100).
    offset : int, optional
        Number of players to skip for pagination (default: 0).

    Returns
    -------
    List[PlayerResponse]
        List of all players with their ELO and statistics.

    Raises
    ------
    HTTPException
        If an error occurs while retrieving players.
    """
    try:
        players_list = player_service.get_all_players_with_stats()
        return players_list[offset : offset + limit]
    except PlayerOperationError as exc:
        logger.error(f"Player operation error while listing players: {exc.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error listing players: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing players",
        )


@router.get(
    "/rankings",
    response_model=List[PlayerResponse],
    summary="Get player rankings",
    description="Retrieves a list of players sorted by global ELO rating.",
)
async def get_player_rankings_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of players to return"),
    days_since_last_match: Optional[int] = Query(
        180, ge=1, description="Only include players whose last match was at least this many days ago"
    ),
):
    """
    Get players sorted by ELO rating for rankings display.

    Parameters
    ----------
    limit : int, optional
        Maximum number of players to return (default: 100, max: 1000).
    days_since_last_match : Optional[int], optional
        Only include players whose last match was at least this many days ago, by default 180.

    Returns
    -------
    List[PlayerResponse]
        List of players sorted by ELO in descending order.
        Each player includes complete details and ELO ratings.

    Notes
    -----
    - Players are sorted in descending order by global ELO.
    - Only includes players who have played at least one match.
    - Only includes players whose last match was within the last `days_since_last_match` days.
    - This is useful for leaderboard displays and ranking tables.
    """
    try:
        return stats_service.get_active_players_rankings(limit=limit, days_since_last_match=days_since_last_match)
    except PlayerOperationError as exc:
        logger.error(f"Player operation error while getting player rankings: {exc.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error getting player rankings: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve player rankings"
        )


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Get player details",
    description="Retrieves a player's details and statistics by player ID.",
)
async def get_player_endpoint(player_id: int = Path(..., gt=0, description="The unique identifier of the player")):
    """
    Retrieve a player's details and statistics by player ID.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.

    Returns
    -------
    PlayerResponse
        The player's details, including ELO and statistics.

    Raises
    ------
    HTTPException
        If the player is not found.
    """
    try:
        player_response = player_service.get_player(player_id=player_id)
        return player_response
    except PlayerNotFoundError as e:
        logger.info(f"Player not found for ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error retrieving player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving player with ID {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the player",
        )


@router.put(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Update player information",
    description="Updates a player's name by player ID. ELO updates are not supported via this endpoint.",
)
async def update_player_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player to update"),
    player: PlayerUpdate = None,
):
    """
    Update a player's name by player ID.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player to update.
    player : PlayerUpdate
        The updated player data (name).

    Returns
    -------
    PlayerResponse
        The updated player's details, including ELO and statistics.

    Raises
    ------
    HTTPException
        If no update fields are provided, update fails, or player is not found.

    Notes
    -----
    ELO updates are not supported via this endpoint.
    """
    if not player or player.name is None:
        try:
            current_player = player_service.get_player(player_id=player_id)
            return current_player
        except PlayerNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
        except PlayerOperationError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)

    if not player.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Player name cannot be empty or whitespace only for update"
        )

    try:
        updated_player_response = player_service.update_existing_player(player_id=player_id, player_update=player)
        return updated_player_response
    except PlayerNotFoundError as e:
        logger.info(f"Player not found for update, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerAlreadyExistsError as e:
        logger.info(f"Attempt to update player to a name that already exists: {e.detail}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
    except InvalidPlayerDataError as e:
        logger.warning(f"Invalid player data for update, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error updating player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error updating player with ID {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the player",
        )


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete player",
    description="Deletes a player by player ID. This operation cannot be undone.",
)
async def delete_player_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player to delete")
):
    """
    Delete a player by player ID.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player to delete.

    Returns
    -------
    None
        No content is returned on successful deletion.

    Raises
    ------
    HTTPException
        If the player is not found.
    """
    try:
        player_service.delete_player(player_id=player_id)
        return None
    except PlayerNotFoundError as e:
        logger.info(f"Player not found for deletion, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error deleting player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error deleting player with ID {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the player",
        )


@router.get(
    "/{player_id}/matches",
    response_model=List[MatchWithEloResponse],
    summary="Get player match history",
    description="Retrieves a player's match history with pagination and date filtering options.",
)
async def get_player_matches_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of matches to return"),
    offset: int = Query(0, ge=0, description="Number of matches to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter matches after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter matches before this date"),
) -> List[MatchWithEloResponse]:
    """
    Get match history for a player.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.
    limit : int, optional
        Maximum number of matches to return (default: 10, max: 100).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).
    start_date : Optional[datetime], optional
        Filter matches after this date (default: None).
    end_date : Optional[datetime], optional
        Filter matches before this date (default: None).

    Returns
    -------
    List[MatchResponse]
        List of matches the player participated in.

    Raises
    ------
    HTTPException
        If the player is not found or an error occurs.
    """
    try:
        filters = {}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date

        matches_response = stats_service.get_player_matches(player_id=player_id, limit=limit, offset=offset, **filters)
        return matches_response
    except PlayerNotFoundError as e:
        logger.info(f"Player not found when fetching matches, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error fetching matches for player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error getting matches for player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving player matches",
        )


@router.get(
    "/{player_id}/elo-history",
    response_model=List[EloHistoryResponse],
    summary="Get player ELO history",
    description="Retrieves a player's ELO rating history with pagination, date filtering, and ELO type filtering options.",
)
async def get_player_elo_history_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of history records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter records after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter records before this date"),
    elo_type: Optional[str] = Query(None, description="Filter by ELO type ('global' or 'monthly')"),
) -> List[EloHistoryResponse]:
    """
    Get ELO history for a player.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.
    limit : int, optional
        Maximum number of history records to return (default: 20, max: 100).
    offset : int, optional
        Number of records to skip for pagination (default: 0).
    start_date : Optional[datetime], optional
        Filter history records after this date (default: None).
    end_date : Optional[datetime], optional
        Filter history records before this date (default: None).
    elo_type : Optional[str], optional
        Filter by ELO type ('global' or 'monthly') (default: None).

    Returns
    -------
    List[EloHistoryResponse]
        List of ELO history records for the player.

    Raises
    ------
    HTTPException
        If the player is not found or an error occurs.
    """
    try:
        filters = {}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if elo_type:
            filters["elo_type"] = elo_type

        elo_history_response = player_service.get_player_elo_history(
            player_id=player_id, limit=limit, offset=offset, **filters
        )
        return elo_history_response
    except PlayerNotFoundError as e:
        logger.info(f"Player not found when fetching ELO history, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error fetching ELO history for player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error getting ELO history for player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving player ELO history",
        )


@router.get(
    "/{player_id}/statistics",
    response_model=Dict[str, Any],
    summary="Get player statistics",
    description="Retrieves detailed statistics for a player, including match results, streaks, and ELO rating information.",
)
async def get_player_statistics_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player")
) -> Dict[str, Any]:
    """
    Get detailed statistics for a player.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing player statistics including:
        - matches_played: Total number of matches played
        - wins: Number of matches won
        - losses: Number of matches lost
        - win_rate: Percentage of matches won
        - average_elo_change: Average ELO change per match
        - highest_elo: Highest ELO achieved
        - lowest_elo: Lowest ELO after initial matches

    Raises
    ------
    HTTPException
        If the player is not found or an error occurs.
    """
    try:
        statistics = stats_service.get_player_statistics(player_id=player_id)
        return statistics
    except PlayerNotFoundError as e:
        logger.info(f"Player not found when fetching statistics, ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except PlayerOperationError as e:
        logger.error(f"Player operation error fetching statistics for player ID {player_id}: {e.detail}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving statistics for player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving player statistics",
        )
