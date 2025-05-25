# -*- coding: utf-8 -*-
"""
This module defines FastAPI endpoints for managing matches in the Baby Foot Elo system.
It supports recording, listing, retrieving, and exporting match records, as well as updating ELO ratings.

Endpoints:
    - POST /matches/: Record a new match and update ELO ratings
    - GET /matches/: List all matches with pagination and filtering
    - GET /matches/{match_id}: Retrieve match details including ELO changes
    - GET /matches/export: Export all matches as JSON

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

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.exceptions.matches import (
    InvalidMatchTeamsError,
    MatchCreationError,
    MatchDeletionError,
    MatchNotFoundError,
)
from app.models.match import MatchCreate, MatchResponse, MatchWithEloResponse
from app.services import matches as service_matches
from app.utils.error_handlers import ErrorResponse

router = APIRouter(
    prefix="/matches",
    tags=["matches"],
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
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal server error",
        },
    },
)


@router.post(
    "/",
    response_model=MatchWithEloResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new match",
    description="Records a new match between two teams and updates ELO ratings for all involved players.",
    responses={
        status.HTTP_201_CREATED: {"description": "Match created successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input data"},
        status.HTTP_404_NOT_FOUND: {"description": "Team or player not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def record_match_endpoint(match_data: MatchCreate) -> MatchWithEloResponse:
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
        - 400: If the request data is invalid
        - 404: If a team or player is not found
        - 500: If there's an internal server error
    """
    try:
        return service_matches.create_new_match(match_data)

    except MatchCreationError as exc:
        logger.error(f"Match creation failed: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc) or "Failed to create match")
    except InvalidMatchTeamsError as exc:
        logger.warning(f"Invalid match teams: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc) or "Invalid match teams")
    except Exception as exc:
        logger.error(f"Unexpected error in record_match_endpoint: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the match",
        )


@router.get(
    "/",
    response_model=List[MatchResponse],
    summary="List all matches",
    description="Returns a paginated list of matches with optional filtering by team, date range, or fanny status.",
    responses={
        status.HTTP_200_OK: {"description": "List of matches retrieved successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid filter parameters"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def list_matches(
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of matches to return"),
    team_id: Optional[int] = Query(None, description="Filter matches by team ID"),
    start_date: Optional[datetime] = Query(None, description="Filter matches by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter matches by end date"),
    is_fanny: Optional[bool] = Query(None, description="Filter by fanny matches"),
) -> List[MatchResponse]:
    """
    List matches with pagination and filtering options.

    This endpoint retrieves matches from the database with support for:
    - Pagination (skip and limit parameters)
    - Filtering by team ID
    - Filtering by date range
    - Filtering by fanny status (10-0 matches)

    Parameters
    ----------
    skip : int, optional
        Number of matches to skip for pagination (default: 0)
    limit : int, optional
        Maximum number of matches to return (default: 100, max: 1000)
    team_id : Optional[int], optional
        Filter matches by team ID
    start_date : Optional[datetime], optional
        Filter matches by start date (inclusive)
    end_date : Optional[datetime], optional
        Filter matches by end date (inclusive)
    is_fanny : Optional[bool], optional
        Filter by fanny matches (10-0 results)

    Returns
    -------
    List[MatchResponse]
        List of matches matching the criteria with team and player details

    Raises
    ------
    HTTPException
        - 400: If filter parameters are invalid
        - 500: If there's an internal server error
    """
    try:
        # ##: Build filter parameters.
        filters = {}
        if team_id is not None:
            filters["team_id"] = team_id
        if start_date is not None:
            filters["start_date"] = start_date
        if end_date is not None:
            filters["end_date"] = end_date
        if is_fanny is not None:
            filters["is_fanny"] = is_fanny

        # ##: Get matches using the service layer.
        return service_matches.get_matches(skip=skip, limit=limit, **filters)

    except ValueError as exc:
        logger.warning(f"Invalid filter parameters: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid filter parameters: {str(exc)}")
    except Exception as exc:
        logger.error(f"Error listing matches: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving matches"
        )


@router.get(
    "/export",
    response_model=List[MatchResponse],
    summary="Export all matches",
    description="Exports all matches in the system as a JSON array for backup or analysis purposes.",
    responses={
        status.HTTP_200_OK: {"description": "All matches exported successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def export_matches() -> List[MatchResponse]:
    """
    Export all matches as JSON.

    This endpoint retrieves all matches from the database without pagination limits,
    making it suitable for data export, backup, or external analysis.

    Returns
    -------
    List[MatchResponse]
        List of all matches in the system with complete details including teams and players

    Raises
    ------
    HTTPException
        - 500: If there's an error retrieving the matches
    """
    try:
        return service_matches.get_matches(limit=100000)

    except Exception as exc:
        logger.error(f"Error exporting matches: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while exporting matches"
        )


@router.get(
    "/{match_id}/player",
    response_model=MatchWithEloResponse,
    summary="Get match with player details",
    description="Retrieves detailed information about a specific match.",
    responses={
        status.HTTP_200_OK: {"description": "Match details retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Match not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def get_match_with_player_details(match_id: int) -> MatchWithEloResponse:
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
        Match details including ELO changes and player information

    Raises
    ------
    HTTPException
        - 404: If the match is not found
        - 500: If there's an internal server error
    """
    try:
        # ##: Get match details with ELO information using the service layer.
        match_with_elo = service_matches.get_match_with_elo_player(match_id)

        if not match_with_elo:
            raise MatchNotFoundError(f"Match with ID {match_id} not found")
        return match_with_elo

    except MatchNotFoundError as exc:
        logger.warning(f"Match not found: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or "Match not found")
    except Exception as exc:
        logger.error(f"Error retrieving match details: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving match details",
        )


@router.get(
    "/{match_id}/team",
    response_model=MatchWithEloResponse,
    summary="Get match with team details",
    description="Retrieves detailed information about a specific match.",
    responses={
        status.HTTP_200_OK: {"description": "Match details retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Match not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def get_match_with_team_details(match_id: int) -> MatchWithEloResponse:
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
        Match details including ELO changes and team information

    Raises
    ------
    HTTPException
        - 404: If the match is not found
        - 500: If there's an internal server error
    """
    try:
        # ##: Get match details with ELO information using the service layer.
        match_with_elo = service_matches.get_match_with_elo_team(match_id)

        if not match_with_elo:
            raise MatchNotFoundError(f"Match with ID {match_id} not found")
        return match_with_elo

    except MatchNotFoundError as exc:
        logger.warning(f"Match not found: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or "Match not found")
    except Exception as exc:
        logger.error(f"Error retrieving match details: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving match details",
        )


@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a match",
    description="""Deletes a match and reverts all associated ELO changes.""",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Match deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Match not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def delete_match(match_id: int) -> None:
    """
    Delete a match and revert all associated ELO changes.

    This endpoint handles the complete match deletion process, including:
    - Validating the match exists
    - Reverting ELO changes for all players involved
    - Updating team statistics
    - Removing the match record

    Parameters
    ----------
    match_id : int
        ID of the match to delete

    Raises
    ------
    HTTPException
        - 404: If the match is not found
        - 500: If there's an error during deletion
    """
    try:
        # ##: Verify the match exists.
        match_data = service_matches.get_match(match_id)
        if not match_data:
            raise MatchNotFoundError(f"Match with ID {match_id} not found")

        # ##: Delete the match using the service layer.
        success = service_matches.delete_match(match_id)

        if not success:
            raise MatchDeletionError(f"Failed to delete match with ID {match_id}")
        return None

    except MatchNotFoundError as exc:
        logger.warning(f"Match not found for deletion: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or "Match not found")
    except MatchDeletionError as exc:
        logger.error(f"Error deleting match: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc) or "Failed to delete match"
        )
    except Exception as exc:
        logger.error(f"Unexpected error in delete_match: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the match",
        )
