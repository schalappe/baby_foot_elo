"""
This module defines FastAPI endpoints for managing players in the Baby Foot Elo system.
It supports creating, listing, retrieving, updating, and deleting player records, as well as fetching player statistics.

Endpoints:
    - POST /api/players/: Create a new player
    - GET /api/players/: List all players
    - GET /api/players/{player_id}: Retrieve a player's details
    - PUT /api/players/{player_id}: Update a player's information
    - DELETE /api/players/{player_id}: Delete a player

Notes
-----
- All endpoints return or accept Pydantic models for request and response bodies.
- ELO updates are not supported via the update endpoint.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.crud.players import create_player, get_all_players, update_player, delete_player
from app.crud.stats import get_player_stats

router = APIRouter(prefix="/api/players",tags=["players"])

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
        elo=int(stats.get("current_elo", 1000)),
        creation_date=stats.get("created_at"),
        matches_played=stats["matches_played"],
        wins=stats["wins"],
        losses=losses
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
        response.append(PlayerResponse(
            id=pid,
            name=stats["name"],
            elo=int(stats.get("current_elo", 1000)),
            creation_date=stats.get("created_at"),
            matches_played=stats["matches_played"],
            wins=stats["wins"],
            losses=losses
        ))
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
        elo=int(stats.get("current_elo", 1000)),
        creation_date=stats.get("created_at"),
        matches_played=stats["matches_played"],
        wins=stats["wins"],
        losses=losses
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
        elo=int(stats.get("current_elo", 1000)),
        creation_date=stats.get("created_at"),
        matches_played=stats["matches_played"],
        wins=stats["wins"],
        losses=losses
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
