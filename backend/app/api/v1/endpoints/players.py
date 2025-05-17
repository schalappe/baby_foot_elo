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

from app.db.builders import SelectQueryBuilder
from app.db.repositories.elo_history import get_player_elo_history
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
from app.models.elo_history import EloHistoryResponse
from app.models.match import MatchWithEloResponse
from app.models.team import TeamResponse
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
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
        # ##: Check if name contains only valid characters.
        if not player.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Player name cannot be empty or whitespace only"
            )

        # ##: Check if a player with this name already exists.
        existing_player = get_player_by_name(player.name)
        if existing_player:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"A player with the name '{player.name}' already exists"
            )

        # ##: Create the player.
        player_id = create_player(player.name, global_elo=player.global_elo)

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

        # ##: Return player response.
        return PlayerResponse(**stats)
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

            response.append(
                PlayerResponse(
                    player_id=pid,
                    name=stats["name"],
                    global_elo=int(stats.get("global_elo", 1000)),
                    created_at=stats.get("created_at"),
                    matches_played=stats["matches_played"],
                    wins=stats["wins"],
                    losses=stats["losses"],
                    win_rate=stats["win_rate"],
                )
            )

        # ##: Apply pagination.
        return response[offset : offset + limit]
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
    description="Retrieves a list of players sorted by global ELO rating who have played at least one match and their last match was at least one month ago.",
)
async def get_player_rankings_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of players to return")
):
    """
    Get players sorted by ELO rating for rankings display.

    Parameters
    ----------
    limit : int, optional
        Maximum number of players to return (default: 100, max: 1000).

    Returns
    -------
    List[PlayerResponse]
        List of players sorted by ELO in descending order.
        Each player includes complete details and ELO ratings.

    Notes
    -----
    - Players are sorted in descending order by global ELO
    - Only includes players who have played at least one match
    - Only includes players whose last match was at least one month ago
    - This is useful for leaderboard displays and ranking tables
    """
    try:
        # ##: Get all players.
        all_players = get_all_players()
        if not all_players:
            return []

        # ##: Get current date to calculate one month ago
        current_date = datetime.now()
        one_month_ago = current_date.replace(
            month=current_date.month - 1 if current_date.month > 1 else 12,
            year=current_date.year if current_date.month > 1 else current_date.year - 1,
        )

        # ##: Process players and get their stats.
        response = []
        for player in all_players:
            pid = player.get("player_id")
            stats = get_player_stats(pid)

            if not stats:
                continue

            # ##: Skip players with no matches
            if stats["matches_played"] == 0:
                continue

            # ##: Get the player's last match date
            last_match_query = (
                SelectQueryBuilder("Matches m")
                .select("MAX(m.played_at)")
                .join("Teams tw", "m.winner_team_id = tw.team_id")
                .join("Teams tl", "m.loser_team_id = tl.team_id")
                .where(
                    "tw.player1_id = ? OR tw.player2_id = ? OR tl.player1_id = ? OR tl.player2_id = ?",
                    pid,
                    pid,
                    pid,
                    pid,
                )
                .execute(fetch_all=False)
            )

            # ##: Skip if no last match found (shouldn't happen if matches_played > 0)
            if not last_match_query or not last_match_query[0]:
                continue
            last_match_date = last_match_query[0]

            # ##: Skip players whose last match is less than a month ago
            if one_month_ago >= last_match_date:
                continue

            response.append(
                PlayerResponse(
                    player_id=pid,
                    name=stats["name"],
                    global_elo=int(stats.get("global_elo", 1000)),
                    created_at=stats.get("created_at"),
                    matches_played=stats["matches_played"],
                    wins=stats["wins"],
                    losses=stats["losses"],
                    win_rate=stats["win_rate"],
                )
            )

        # ##: Sort by global ELO in descending order.
        response.sort(key=lambda x: x.global_elo, reverse=True)

        # ##: Apply limit.
        return response[:limit]
    except Exception as exc:
        logger.exception(f"Unexpected error getting player rankings: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting player rankings",
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

        # ##: Return player response.
        return PlayerResponse(
            player_id=stats["player_id"],
            name=stats["name"],
            global_elo=int(stats.get("global_elo", 1000)),
            created_at=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=stats["losses"],
            win_rate=stats["win_rate"],
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

        # ##: Return updated player response.
        return PlayerResponse(
            player_id=stats["player_id"],
            name=stats["name"],
            global_elo=int(stats.get("global_elo", 1000)),
            created_at=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=stats["losses"],
            win_rate=stats["win_rate"],
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

        # ##: Get matches for the player.
        matches = get_matches_by_player(player_id, limit, offset, start_date, end_date)

        # ##: Sort by date (newest first) and apply pagination.
        matches.sort(key=lambda x: x["played_at"], reverse=True)
        matches = matches[offset : offset + limit]

        # ##: Convert to response model.
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
        history = get_player_elo_history(player_id, limit, offset, start_date, end_date, elo_type)

        # ##: If no history found, return empty list (player exists but has no history).
        if not history:
            return []

        # ##: Convert to response model.
        response = [EloHistoryResponse(**record) for record in history]

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
        elo_history = get_player_elo_history(player_id, 1000, 0, None, None)

        # ##: Get last 30 matches for recent performance stats
        recent_matches = get_player_elo_history(player_id, 30, 0, None, None)

        # ##: Calculate win rate.
        matches_played = stats["matches_played"]
        wins = stats["wins"]
        losses = stats["losses"]
        win_rate = (wins / matches_played) * 100 if matches_played > 0 else 0

        # ##: Process ELO history if available.
        elo_changes = []
        elo_values = []

        if elo_history:
            elo_changes = [record["difference"] for record in elo_history if record["difference"] is not None]
            elo_values = [record["new_elo"] for record in elo_history if record["new_elo"] is not None]

        # ##: Process recent matches (last 30).
        recent_wins = 0
        recent_losses = 0
        recent_elo_changes = []

        if recent_matches:
            for match in recent_matches:
                if match["difference"] is not None:
                    recent_elo_changes.append(match["difference"])
                    if match["difference"] > 0:
                        recent_wins += 1
                    elif match["difference"] < 0:
                        recent_losses += 1

        avg_elo_change = sum(elo_changes) / len(elo_changes) if elo_changes else 0
        highest_elo = max(elo_values) if elo_values else stats.get("global_elo", 1000)
        lowest_elo = min(elo_values) if elo_values else stats.get("global_elo", 1000)

        # ##: Calculate recent stats
        recent_matches_played = recent_wins + recent_losses
        recent_win_rate = (recent_wins / recent_matches_played * 100) if recent_matches_played > 0 else 0
        recent_avg_elo_change = sum(recent_elo_changes) / len(recent_elo_changes) if recent_elo_changes else 0

        # ##: Return comprehensive statistics.
        return {
            "player_id": player_id,
            "name": stats["name"],
            "global_elo": int(stats.get("global_elo", 1000)),
            "matches_played": matches_played,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "elo_difference": elo_changes,
            "elo_values": elo_values,
            "average_elo_change": round(avg_elo_change, 2),
            "highest_elo": int(highest_elo),
            "lowest_elo": int(lowest_elo),
            "creation_date": stats.get("created_at"),
            # ##: Recent performance (last 30 matches).
            "recent": {
                "matches_played": recent_matches_played,
                "wins": recent_wins,
                "losses": recent_losses,
                "win_rate": round(recent_win_rate, 2),
                "average_elo_change": round(recent_avg_elo_change, 2),
                "elo_changes": recent_elo_changes[:30],
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error retrieving statistics for player {player_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving player statistics",
        )
