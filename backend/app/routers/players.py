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
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, status

from app.crud.players import (
    create_player,
    delete_player,
    get_all_players,
    update_player,
)
from app.crud.stats import get_player_stats, get_player_elo_history
from app.crud.matches import get_matches_by_team
from app.crud.elo_history import get_player_elo_history as get_elo_history
from app.crud.teams import get_teams_by_player
from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.models.match import MatchResponse
from app.models.elo_history import EloHistoryResponse

router = APIRouter(prefix="/api/v1/players", tags=["players"])


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player_endpoint(player: PlayerCreate):
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
    player_id = create_player(player.name)
    if not player_id:
        raise HTTPException(status_code=500, detail="Failed to create player")

    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=500, detail="Failed to fetch player after creation")

    losses = stats["matches_played"] - stats["wins"]
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


@router.get("/", response_model=List[PlayerResponse])
def list_players_endpoint():
    """
    List all players with their details and statistics.

    Returns
    -------
    List[PlayerResponse]
        List of all players with their ELO and statistics.
    """
    response = []
    for player in get_all_players():
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
    return response


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player_endpoint(player_id: int):
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
    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")

    losses = stats["matches_played"] - stats["wins"]
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


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player_endpoint(player_id: int, player: PlayerUpdate):
    """
    Update a player's name or initial ELO by player ID.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player to update.
    player : PlayerUpdate
        The updated player data (name and/or initial ELO).

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
    if player.name is None and player.initial_elo is None:
        raise HTTPException(status_code=400, detail="No update fields provided")

    if player.name is not None:
        success = update_player(player_id, player.name)
        if not success:
            raise HTTPException(status_code=404, detail="Player not found")

    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=500, detail="Failed to fetch player after update")

    losses = stats["matches_played"] - stats["wins"]
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


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_endpoint(player_id: int):
    """
    Delete a player by player ID.

    Parameters
    ----------
    player_id : int
        The unique identifier of the player to delete.

    Raises
    ------
    HTTPException
        If the player is not found.
    """
    deleted = delete_player(player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Player not found")
    return None

@router.get("/{player_id}/matches", response_model=List[MatchResponse])
def get_player_matches_endpoint(
    player_id: int, 
    limit: int = Query(10, ge=1, le=100, description="Maximum number of matches to return"),
    offset: int = Query(0, ge=0, description="Number of matches to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter matches after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter matches before this date")
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
        If the player is not found.
    """
    # ##: First check if player exists.
    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # ##: Get all teams the player is a part of.
    teams = get_teams_by_player(player_id)
    if not teams:
        return []
    
    # ##: Get matches for each team and combine results.
    all_matches = []
    for team in teams:
        team_matches = get_matches_by_team(team["team_id"])
        for match in team_matches:
            match["player_won"] = match["winner_team_id"] == team["team_id"]
            all_matches.append(match)
    
    # ##: Apply date filters if provided.
    filtered_matches = all_matches
    if start_date:
        filtered_matches = [m for m in filtered_matches if m["played_at"] >= start_date]
    if end_date:
        filtered_matches = [m for m in filtered_matches if m["played_at"] <= end_date]
    
    # ##: Sort by date (newest first).
    sorted_matches = sorted(filtered_matches, key=lambda x: x["played_at"], reverse=True)
    
    # ##: Apply pagination.
    paginated_matches = sorted_matches[offset:offset+limit]
    
    # ##: Convert to MatchResponse objects.
    return [
        MatchResponse(
            match_id=match["match_id"],
            winner_team_id=match["winner_team_id"],
            loser_team_id=match["loser_team_id"],
            is_fanny=match["is_fanny"],
            played_at=match["played_at"],
            year=match["year"],
            month=match["month"],
            day=match["day"],
            player_won=match["player_won"]
        )
        for match in paginated_matches
    ]


@router.get("/{player_id}/elo-history", response_model=List[EloHistoryResponse])
def get_player_elo_history_endpoint(
    player_id: int,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of history records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter records after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter records before this date"),
    elo_type: Optional[str] = Query(None, description="Filter by ELO type ('global' or 'monthly')")
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
        If the player is not found.
    """
    # ##: First check if player exists.
    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # ##: Get ELO history with filters.
    history = get_elo_history(
        player_id=player_id,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        elo_type=elo_type
    )
    
    if not history:
        return []
    
    # ##: Convert to EloHistoryResponse objects.
    return [
        EloHistoryResponse(
            history_id=record["history_id"],
            player_id=record["player_id"],
            match_id=record["match_id"],
            type=record["type"],
            old_elo=record["old_elo"],
            new_elo=record["new_elo"],
            difference=record["difference"],
            date=record["date"],
            year=record["year"],
            month=record["month"],
            day=record["day"]
        )
        for record in history
    ]


@router.get("/{player_id}/statistics", response_model=Dict[str, Any])
def get_player_statistics_endpoint(player_id: int) -> Dict[str, Any]:
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
        If the player is not found.
    """
    # ##: Get player stats.
    stats = get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # ##: Get ELO history for additional stats.
    elo_history = get_player_elo_history(player_id)
    
    # ##: Calculate additional statistics.
    result = {
        "matches_played": stats["matches_played"],
        "wins": stats["wins"],
        "losses": stats["losses"],
        "win_rate": stats["win_rate"] if "win_rate" in stats else 0,
    }
    
    # ##: Add ELO-based statistics if history exists.
    if elo_history:
        # ##: Calculate average ELO change.
        global_changes = [h["difference"] for h in elo_history if h["type"] == "global"]
        result["average_elo_change"] = sum(global_changes) / len(global_changes) if global_changes else 0
        
        # ##: Find highest and lowest ELO.
        global_elos = [h["new_elo"] for h in elo_history if h["type"] == "global"]
        result["highest_elo"] = max(global_elos) if global_elos else stats.get("global_elo", 1000)
        result["lowest_elo"] = min(global_elos) if global_elos else stats.get("global_elo", 1000)
    
    # ##: Get player's teams.
    teams = get_teams_by_player(player_id)
    
    # ##: TODO: Calculate streaks if we have teams and matches.
    if teams:
        # ##: This would require additional logic to calculate streaks.
        # ##: For now, we'll set placeholder values.
        result["current_streak"] = 0
        result["best_streak"] = 0
        result["worst_streak"] = 0
    
    return result
