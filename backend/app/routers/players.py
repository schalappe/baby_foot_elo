"""
This module defines FastAPI endpoints for managing players in the Baby Foot Elo system.
It supports creating, listing, retrieving, updating, and deleting player records, as well as fetching player statistics.

Endpoints:
    - POST /api/v1/players/: Create a new player
    - GET /api/v1/players/: List all players
    - GET /api/v1/players/{player_id}: Retrieve a player's details
    - PUT /api/v1/players/{player_id}: Update a player's information
    - DELETE /api/v1/players/{player_id}: Delete a player
    - GET /api/v1/players/{player_id}/matches: Get player's match history
    - GET /api/v1/players/{player_id}/elo-history: Get player's ELO history
    - GET /api/v1/players/{player_id}/statistics: Get player's statistics

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

from app.crud.elo_history import get_player_elo_history as get_elo_history
from app.crud.matches import get_matches_by_team
from app.crud.players import (
    create_player,
    delete_player,
    get_all_players,
    get_player,
    update_player,
)
from app.crud.stats import get_player_elo_history, get_player_stats
from app.crud.teams import get_teams_by_player
from app.models.elo_history import EloHistoryResponse
from app.models.match import MatchResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.utils.error_handlers import ErrorResponse

router = APIRouter(
    prefix="/api/v1/players",
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
        # ##: Check if name contains only valid characters.
        if not player.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Player name cannot be empty or whitespace only"
            )

        # ##: Create the player.
        player_id = create_player(
            player.name, global_elo=player.global_elo, current_month_elo=player.current_month_elo
        )

        if not player_id:
            logger.error(f"Failed to create player with name: {player.name}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create player")

        # ##: Get player stats.
        stats = get_player_stats(player_id)
        if not stats:
            logger.error(f"Failed to fetch stats for newly created player ID: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch player after creation"
            )

        # ##: Calculate losses.
        losses = stats["matches_played"] - stats["wins"]

        # ##: Return player response.
        return PlayerResponse(
            id=stats["player_id"],
            name=stats["name"],
            global_elo=int(stats.get("global_elo", 1000)),
            current_month_elo=int(stats.get("current_month_elo", 1000)),
            creation_date=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=losses,
        )
    except HTTPException:
        # ##: Re-raise HTTP exceptions.
        raise
    except Exception as exc:
        # ##: Log unexpected errors and return a generic error message.
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
    sort_by: Optional[str] = Query(
        None, description="Field to sort by (name, global_elo, current_month_elo, matches_played, wins, losses)"
    ),
    order: str = Query("asc", description="Sort order (asc or desc)"),
):
    """
    List all players with their details and statistics.

    Parameters
    ----------
    limit : int, optional
        Maximum number of players to return (default: 50, max: 100).
    offset : int, optional
        Number of players to skip for pagination (default: 0).
    sort_by : Optional[str], optional
        Field to sort by (default: None).
    order : str, optional
        Sort order, 'asc' or 'desc' (default: 'asc').

    Returns
    -------
    List[PlayerResponse]
        List of all players with their ELO and statistics.

    Raises
    ------
    HTTPException
        If sorting or pagination fails.
    """
    try:
        # ##: Validate sort parameters.
        valid_sort_fields = ["name", "global_elo", "current_month_elo", "matches_played", "wins", "losses"]
        if sort_by and sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}",
            )

        if order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order. Must be 'asc' or 'desc'"
            )

        # ##: Get all players.
        all_players = get_all_players()
        if not all_players:
            return []

        # ##: Process players and get their stats.
        response = []
        for player in all_players:
            pid = player.get("player_id")
            stats = get_player_stats(pid)

            if not stats:
                continue

            losses = stats["matches_played"] - stats["wins"]
            response.append(
                PlayerResponse(
                    id=pid,
                    name=stats["name"],
                    global_elo=int(stats.get("global_elo", 1000)),
                    current_month_elo=int(stats.get("current_month_elo", 1000)),
                    creation_date=stats.get("created_at"),
                    matches_played=stats["matches_played"],
                    wins=stats["wins"],
                    losses=losses,
                )
            )

        # ##: Sort the response if requested.
        if sort_by:
            reverse = order.lower() == "desc"
            response.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)

        # ##: Apply pagination.
        return response[offset : offset + limit]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error listing players: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing players",
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
        # ##: First check if the player exists.
        player = get_player(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Get player stats.
        stats = get_player_stats(player_id)
        if not stats:
            logger.error(f"Player found but stats missing for ID: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch player statistics"
            )

        # ##: Calculate losses.
        losses = stats["matches_played"] - stats["wins"]

        # ##: Return player response.
        return PlayerResponse(
            id=stats["player_id"],
            name=stats["name"],
            global_elo=int(stats.get("global_elo", 1000)),
            current_month_elo=int(stats.get("current_month_elo", 1000)),
            creation_date=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=losses,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving player {player_id}: {str(exc)}")
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
    try:
        # ##: Validate update data.
        if player.name is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update fields provided")

        # ##: Check if name contains only valid characters.
        if player.name is not None and not player.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Player name cannot be empty or whitespace only"
            )

        # ##: First check if the player exists.
        existing_player = get_player(player_id)
        if not existing_player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Update the player.
        success = update_player(player_id, player.name)
        if not success:
            logger.error(f"Failed to update player ID {player_id} with name {player.name}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update player")

        # ##: Get updated player stats.
        stats = get_player_stats(player_id)
        if not stats:
            logger.error(f"Failed to fetch stats for player ID {player_id} after update")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch player after update"
            )

        # ##: Calculate losses.
        losses = stats["matches_played"] - stats["wins"]

        # ##: Return updated player response.
        return PlayerResponse(
            id=stats["player_id"],
            name=stats["name"],
            global_elo=int(stats.get("global_elo", 1000)),
            current_month_elo=int(stats.get("current_month_elo", 1000)),
            creation_date=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=losses,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error updating player {player_id}: {str(exc)}")
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
        # ##: First check if the player exists.
        existing_player = get_player(player_id)
        if not existing_player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Delete the player.
        success = delete_player(player_id)
        if not success:
            logger.error(f"Failed to delete player ID {player_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete player")

        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error deleting player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the player",
        )


@router.get(
    "/{player_id}/matches",
    response_model=List[MatchResponse],
    summary="Get player match history",
    description="Retrieves a player's match history with pagination and date filtering options.",
)
async def get_player_matches_endpoint(
    player_id: int = Path(..., gt=0, description="The unique identifier of the player"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of matches to return"),
    offset: int = Query(0, ge=0, description="Number of matches to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter matches after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter matches before this date"),
):
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
        # ##: Validate date range if both are provided.
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")

        # ##: First check if the player exists.
        player = get_player(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Get teams for the player.
        teams = get_teams_by_player(player_id)
        if not teams:
            return []

        # ##: Get matches for each team.
        matches = []
        for team in teams:
            team_matches = get_matches_by_team(team["team_id"], limit, offset, start_date, end_date)
            if team_matches:
                matches.extend(team_matches)

        # ##: Sort by date (newest first) and apply pagination.
        matches.sort(key=lambda x: x["match_date"], reverse=True)
        matches = matches[offset : offset + limit]

        # ##: Convert to response model.
        response = []
        for match in matches:
            response.append(
                MatchResponse(
                    id=match["match_id"],
                    team1_id=match["team1_id"],
                    team2_id=match["team2_id"],
                    team1_score=match["team1_score"],
                    team2_score=match["team2_score"],
                    team1_elo_change=match["team1_elo_change"],
                    team2_elo_change=match["team2_elo_change"],
                    match_date=match["match_date"],
                )
            )

        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving matches for player {player_id}: {str(exc)}")
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
):
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
        # ##: Validate date range if both are provided.
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")

        # ##: Validate ELO type.
        if elo_type and elo_type not in ["global", "monthly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ELO type. Must be 'global' or 'monthly'."
            )

        # ##: First check if the player exists.
        player = get_player(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Get ELO history.
        history = get_elo_history(player_id, limit, offset, start_date, end_date, elo_type)

        # ##: If no history found, return empty list (player exists but has no history).
        if not history:
            return []

        # ##: Convert to response model.
        response = []
        for record in history:
            response.append(
                EloHistoryResponse(
                    id=record["history_id"],
                    player_id=record["player_id"],
                    elo_value=record["elo_value"],
                    elo_change=record["elo_change"],
                    match_id=record["match_id"],
                    elo_type=record["elo_type"],
                    timestamp=record["timestamp"],
                )
            )

        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving ELO history for player {player_id}: {str(exc)}")
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
        - current_streak: Current winning/losing streak
        - best_streak: Best winning streak
        - worst_streak: Worst losing streak
        - average_elo_change: Average ELO change per match
        - highest_elo: Highest ELO achieved
        - lowest_elo: Lowest ELO after initial matches

    Raises
    ------
    HTTPException
        If the player is not found or an error occurs.
    """
    try:
        # ##: First check if the player exists.
        player = get_player(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Player with ID {player_id} not found")

        # ##: Get player stats.
        stats = get_player_stats(player_id)
        if not stats:
            logger.error(f"Player found but stats missing for ID: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch player statistics"
            )

        # ##: Get ELO history for additional stats.
        elo_history = get_player_elo_history(player_id, 1000, 0, None, None, "global")

        # ##: Calculate win rate.
        matches_played = stats["matches_played"]
        wins = stats["wins"]
        losses = matches_played - wins
        win_rate = (wins / matches_played) * 100 if matches_played > 0 else 0

        # ##: TODO: Calculate streaks and ELO stats.
        current_streak = 0
        best_streak = 0
        worst_streak = 0
        streak_type = None  # 'win' or 'loss'
        temp_streak = 0

        # ##: Process ELO history if available.
        elo_changes = []
        elo_values = []

        if elo_history:
            elo_changes = [record["elo_change"] for record in elo_history if record["elo_change"] is not None]
            elo_values = [record["elo_value"] for record in elo_history if record["elo_value"] is not None]

        avg_elo_change = sum(elo_changes) / len(elo_changes) if elo_changes else 0
        highest_elo = max(elo_values) if elo_values else stats.get("global_elo", 1000)
        lowest_elo = min(elo_values) if elo_values else stats.get("global_elo", 1000)

        # ##: Return comprehensive statistics.
        return {
            "player_id": player_id,
            "name": stats["name"],
            "global_elo": int(stats.get("global_elo", 1000)),
            "current_month_elo": int(stats.get("current_month_elo", 1000)),
            "matches_played": matches_played,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "current_streak": current_streak,
            "best_streak": best_streak,
            "worst_streak": worst_streak,
            "average_elo_change": round(avg_elo_change, 2),
            "highest_elo": int(highest_elo),
            "lowest_elo": int(lowest_elo),
            "creation_date": stats.get("created_at"),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving statistics for player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving player statistics",
        )
