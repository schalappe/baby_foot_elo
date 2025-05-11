# -*- coding: utf-8 -*-
"""
This module defines FastAPI endpoints for managing matches in the Baby Foot Elo system.
It supports recording, listing, retrieving, and exporting match records, as well as updating ELO ratings.

Endpoints:
    - POST /api/v1/matches/: Record a new match and update ELO ratings
    - GET /api/v1/matches/: List all matches with pagination and filtering
    - GET /api/v1/matches/{match_id}: Retrieve match details including ELO changes
    - GET /api/v1/matches/export: Export all matches as JSON

Notes
-----
- All endpoints return or accept Pydantic models for request and response bodies.
- Match recording automatically updates player and team ELO ratings.
- ELO history is recorded for each player involved in a match.
- All endpoints include proper validation and error handling.
- Transaction handling ensures atomicity of match recording and ELO updates.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.crud.elo_history import batch_record_elo_updates, get_elo_history_by_match
from app.crud.matches import (
    create_match,
    get_all_matches,
    get_fanny_matches,
    get_match,
    get_matches_by_date_range,
    get_matches_by_team,
)
from app.crud.players import get_player, update_player
from app.crud.teams import get_team, update_team
from app.models.match import MatchCreate, MatchResponse, MatchWithEloResponse
from app.models.team import TeamResponse
from app.services.elo.calculator import calculate_team_elo, process_match_result

router = APIRouter(
    prefix="/api/v1/matches",
    tags=["matches"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    response_model=MatchWithEloResponse,
    status_code=201,
    summary="Record a new match",
    description="Records a new match between two teams and updates ELO ratings for all involved players.",
)
async def record_match_endpoint(match_data: MatchCreate):
    """
    Record a new match and update ELO ratings for all involved players.

    This endpoint handles the complete match recording process, including:
    - Validating team and player existence
    - Recording the match in the database
    - Calculating ELO changes for all players
    - Updating player ELO ratings
    - Recording ELO history for each player
    - Updating team ELO ratings

    Parameters
    ----------
    match_data : MatchCreate
        Match data including winner and loser team IDs, is_fanny flag, and optional played_at timestamp.

    Returns
    -------
    MatchWithEloResponse
        Match details including ELO changes for all involved players.

    Raises
    ------
    HTTPException
        If teams don't exist, are the same, or if any other validation fails.
    """
    # ##: Set default played_at time if not provided.
    played_at = match_data.played_at or datetime.now()

    # ##: Validate teams exist.
    winner_team = get_team(match_data.winner_team_id)
    if not winner_team:
        raise HTTPException(status_code=404, detail=f"Winner team with ID {match_data.winner_team_id} not found")

    loser_team = get_team(match_data.loser_team_id)
    if not loser_team:
        raise HTTPException(status_code=404, detail=f"Loser team with ID {match_data.loser_team_id} not found")

    # ##: Validate teams are different.
    if match_data.winner_team_id == match_data.loser_team_id:
        raise HTTPException(status_code=400, detail="Winner and loser teams cannot be the same")

    # ##: Get player data for ELO calculations.
    winner_player1 = get_player(winner_team["player1_id"])
    winner_player2 = get_player(winner_team["player2_id"])
    loser_player1 = get_player(loser_team["player1_id"])
    loser_player2 = get_player(loser_team["player2_id"])

    if not all([winner_player1, winner_player2, loser_player1, loser_player2]):
        raise HTTPException(status_code=404, detail="One or more players not found")

    # ##: Use a transaction to ensure atomicity.
    try:
        # ##: Record the match.
        match_id = create_match(
            winner_team_id=match_data.winner_team_id,
            loser_team_id=match_data.loser_team_id,
            played_at=played_at,
            is_fanny=match_data.is_fanny,
        )

        if not match_id:
            raise HTTPException(status_code=500, detail="Failed to create match record")

        # ##: Calculate ELO changes.
        elo_changes = process_match_result(
            winner_team=[
                {"id": winner_player1["player_id"], "elo": winner_player1["global_elo"]},
                {"id": winner_player2["player_id"], "elo": winner_player2["global_elo"]},
            ],
            losing_team=[
                {"id": loser_player1["player_id"], "elo": loser_player1["global_elo"]},
                {"id": loser_player2["player_id"], "elo": loser_player2["global_elo"]},
            ],
        )

        # ##: Update player ELO ratings and record ELO history.
        elo_history_records = []
        for player_id, changes in elo_changes.items():
            old_elo = changes["old_elo"]
            new_elo = changes["new_elo"]

            # Update player ELO
            update_player(player_id, global_elo=new_elo)

            # Record ELO history
            elo_history_records.append(
                {
                    "player_id": player_id,
                    "match_id": match_id,
                    "old_elo": old_elo,
                    "new_elo": new_elo,
                    "type": "global",
                    "date": played_at,
                }
            )

        # ##: Record all ELO history entries in a batch.
        batch_record_elo_updates(elo_history_records)

        # ##: Update team ELO ratings.
        winner_team_elo = calculate_team_elo(
            elo_changes[winner_player1["player_id"]]["new_elo"], elo_changes[winner_player2["player_id"]]["new_elo"]
        )

        loser_team_elo = calculate_team_elo(
            elo_changes[loser_player1["player_id"]]["new_elo"], elo_changes[loser_player2["player_id"]]["new_elo"]
        )

        # ##: Update team ELO and last match timestamp.
        update_team(match_data.winner_team_id, global_elo=winner_team_elo, last_match_at=played_at.isoformat())

        update_team(match_data.loser_team_id, global_elo=loser_team_elo, last_match_at=played_at.isoformat())

        # ##: Get match details for response.
        match_data = get_match(match_id)

        # ##: Create response with ELO changes.
        response = MatchWithEloResponse(
            match_id=match_id,
            winner_team_id=match_data["winner_team_id"],
            loser_team_id=match_data["loser_team_id"],
            is_fanny=match_data["is_fanny"],
            played_at=match_data["played_at"],
            year=match_data["year"],
            month=match_data["month"],
            day=match_data["day"],
            elo_changes=elo_changes,
        )

        return response

    except Exception as e:
        logger.error(f"Error recording match: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process match: {str(e)}")


@router.get(
    "/",
    response_model=List[MatchResponse],
    summary="List all matches",
    description="Returns a paginated list of matches with optional filtering by team, date range, or fanny status.",
)
async def list_matches(
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of matches to return"),
    team_id: Optional[int] = Query(None, description="Filter matches by team ID"),
    start_date: Optional[datetime] = Query(None, description="Filter matches by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter matches by end date"),
    is_fanny: Optional[bool] = Query(None, description="Filter by fanny matches"),
):
    """
    List matches with pagination and filtering options.

    This endpoint retrieves matches from the database with support for:
    - Pagination (skip and limit parameters)
    - Filtering by team ID
    - Filtering by date range
    - Filtering by fanny status (10-0 matches)

    Parameters
    ----------
    skip : int
        Number of matches to skip for pagination
    limit : int
        Maximum number of matches to return
    team_id : Optional[int]
        Filter matches by team ID
    start_date : Optional[datetime]
        Filter matches by start date
    end_date : Optional[datetime]
        Filter matches by end date
    is_fanny : Optional[bool]
        Filter by fanny matches

    Returns
    -------
    List[MatchResponse]
        List of matches matching the criteria
    """
    # ##: Determine which query to use based on filters.
    if is_fanny is not None and is_fanny:
        matches_data = get_fanny_matches()
    elif team_id is not None:
        matches_data = get_matches_by_team(team_id)
    elif start_date is not None and end_date is not None:
        matches_data = get_matches_by_date_range(start_date, end_date)
    else:
        matches_data = get_all_matches(limit=limit, offset=skip)

    # ##: Convert to response model.
    result = []
    for match in matches_data:
        match_response = MatchResponse(
            match_id=match["match_id"],
            winner_team_id=match["winner_team_id"],
            loser_team_id=match["loser_team_id"],
            is_fanny=match["is_fanny"],
            played_at=match["played_at"],
            year=match["year"],
            month=match["month"],
            day=match["day"],
        )
        result.append(match_response)

    return result


@router.get(
    "/{match_id}",
    response_model=MatchWithEloResponse,
    summary="Get match details",
    description="Retrieves detailed information about a specific match, including ELO changes for all players involved.",
)
async def get_match_details(match_id: int):
    """
    Get detailed information about a specific match.

    This endpoint retrieves comprehensive match information including:
    - Basic match details (winner/loser teams, date, etc.)
    - ELO changes for all players involved
    - Team information for both winner and loser teams

    Parameters
    ----------
    match_id : int
        ID of the match to retrieve

    Returns
    -------
    MatchWithEloResponse
        Match details including ELO changes

    Raises
    ------
    HTTPException
        If the match is not found
    """
    match_data = get_match(match_id)
    if not match_data:
        raise HTTPException(status_code=404, detail=f"Match with ID {match_id} not found")

    # ##: Get ELO history records for this match to show ELO changes.
    elo_changes = {}

    # ##: Get ELO history records for this match.
    elo_history_records = get_elo_history_by_match(match_id)

    # ##: Format ELO changes for response.
    for record in elo_history_records:
        player_id = record["player_id"]
        elo_changes[player_id] = {
            "old_elo": record["old_elo"],
            "new_elo": record["new_elo"],
            "change": record["difference"],
        }

    # ##: Get team details.
    winner_team = get_team(match_data["winner_team_id"])
    loser_team = get_team(match_data["loser_team_id"])

    # ##: Convert to response models.
    winner_team_response = None
    loser_team_response = None

    if winner_team:
        winner_team_response = TeamResponse(
            team_id=winner_team["team_id"],
            player1_id=winner_team["player1_id"],
            player2_id=winner_team["player2_id"],
            global_elo=winner_team["global_elo"],
            created_at=winner_team["created_at"],
            last_match_at=winner_team["last_match_at"],
        )

    if loser_team:
        loser_team_response = TeamResponse(
            team_id=loser_team["team_id"],
            player1_id=loser_team["player1_id"],
            player2_id=loser_team["player2_id"],
            global_elo=loser_team["global_elo"],
            created_at=loser_team["created_at"],
            last_match_at=loser_team["last_match_at"],
        )

    return MatchWithEloResponse(
        match_id=match_data["match_id"],
        winner_team_id=match_data["winner_team_id"],
        loser_team_id=match_data["loser_team_id"],
        is_fanny=match_data["is_fanny"],
        played_at=match_data["played_at"],
        year=match_data["year"],
        month=match_data["month"],
        day=match_data["day"],
        winner_team=winner_team_response,
        loser_team=loser_team_response,
        elo_changes=elo_changes,
    )


@router.get(
    "/export",
    response_model=List[MatchResponse],
    summary="Export all matches",
    description="Exports all matches in the system as a JSON array for backup or analysis purposes.",
)
async def export_matches():
    """
    Export all matches as JSON.

    This endpoint retrieves all matches from the database without pagination limits,
    making it suitable for data export, backup, or external analysis.

    Returns
    -------
    List[MatchResponse]
        List of all matches in the system
    """
    # Get all matches without pagination limits
    matches_data = get_all_matches(limit=10000, offset=0)

    # Convert to response model
    result = []
    for match in matches_data:
        match_response = MatchResponse(
            match_id=match["match_id"],
            winner_team_id=match["winner_team_id"],
            loser_team_id=match["loser_team_id"],
            is_fanny=match["is_fanny"],
            played_at=match["played_at"],
            year=match["year"],
            month=match["month"],
            day=match["day"],
        )
        result.append(match_response)

    return result
