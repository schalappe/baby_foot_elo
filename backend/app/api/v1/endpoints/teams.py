# -*- coding: utf-8 -*-
"""
This module defines FastAPI endpoints for managing teams in the Baby Foot Elo system.
It supports creating, listing, retrieving, and deleting team records, as well as fetching team rankings and match history.

Endpoints:
    - POST /teams/: Create a new team
    - GET /teams/: List all teams
    - GET /teams/rankings: Get team rankings
    - GET /teams/{team_id}: Retrieve a team's details
    - DELETE /teams/{team_id}: Delete a team
    - GET /teams/{team_id}/matches: Get team's match history
    - GET /teams/player/{player_id}: Get teams for a specific player

Notes
-----
- All endpoints return or accept Pydantic models for request and response bodies.
- Team ELO is calculated based on the ELO ratings of its players.
- Teams must consist of exactly two players.
- All endpoints include proper validation and error handling.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from loguru import logger

from app.exceptions.teams import (
    InvalidTeamDataError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    TeamOperationError,
)
from app.models.match import MatchResponse, MatchWithEloResponse
from app.models.team import TeamCreate, TeamResponse, TeamUpdate
from app.services import stats as stats_service
from app.services import teams as teams_service
from app.utils.error_handlers import ErrorResponse

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad request - invalid input parameters",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Not found",
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
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    description="Create a new team with two players.",
)
async def create_team_endpoint(team: TeamCreate) -> TeamResponse:
    """
    Create a new team with two players.

    This endpoint handles the complete team creation process, including:
    - Validating that both players exist
    - Ensuring players are different (cannot create a team with the same player twice)
    - Calculating initial team ELO based on player ELOs
    - Creating the team record in the database
    - Returning the complete team details with player information

    Parameters
    ----------
    team : TeamCreate
        Team data including player IDs. Must contain player1_id and player2_id.

    Returns
    -------
    TeamResponse
        Created team data including player details and calculated ELO ratings.

    Raises
    ------
    HTTPException
        If player IDs are invalid, players don't exist, or team creation fails.
        Status codes:
        - 400: Invalid input (e.g., same player for both positions)
        - 404: One or both players not found
        - 409: Team with these players already exists
        - 422: Validation error
        - 500: Internal server error
    """
    try:
        return teams_service.create_new_team(team)

    except InvalidTeamDataError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except TeamAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error creating team: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the team"
        )
    except Exception as exc:
        logger.error(f"Unexpected error creating team: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/",
    response_model=List[TeamResponse],
    summary="List all teams",
    description="Get a list of all teams with optional filtering and pagination.",
)
async def get_teams_endpoint(
    skip: int = Query(0, ge=0, description="Number of teams to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of teams to return"),
    min_elo: Optional[float] = Query(None, ge=0, description="Minimum global ELO rating"),
    max_elo: Optional[float] = Query(None, ge=0, description="Maximum global ELO rating"),
    player_id: Optional[int] = Query(None, gt=0, description="Filter teams by player ID"),
) -> List[TeamResponse]:
    """
    Get a list of all teams with optional pagination and filtering.

    This endpoint retrieves teams from the database with support for:
    - Pagination (skip and limit parameters)
    - Filtering by ELO rating range (min_elo and max_elo)
    - Filtering by player ID (returns teams containing the specified player)
    - Automatic inclusion of player details for each team

    Parameters
    ----------
    skip : int, optional
        Number of teams to skip for pagination, by default 0.
    limit : int, optional
        Maximum number of teams to return, by default 100 (max 100).
    min_elo : Optional[float], optional
        Minimum global ELO rating to filter teams, by default None.
    max_elo : Optional[float], optional
        Maximum global ELO rating to filter teams, by default None.
    player_id : Optional[int], optional
        Filter teams by player ID (returns teams containing this player), by default None.

    Returns
    -------
    List[TeamResponse]
        List of teams matching the criteria, each including complete player details.
    """
    try:
        if player_id is not None:
            # ##: Get teams by player ID.
            teams = teams_service.get_teams_by_player_id(player_id)

            # ##: Apply additional ELO filters if needed.
            if min_elo is not None or max_elo is not None:
                filtered_teams = []
                for team in teams:
                    if min_elo is not None and team.global_elo < min_elo:
                        continue
                    if max_elo is not None and team.global_elo > max_elo:
                        continue
                    filtered_teams.append(team)
                teams = filtered_teams

            # ##: Apply pagination.
            return teams[skip : skip + limit]

        # ##: Get all teams with pagination and ELO filtering.
        return teams_service.get_all_teams_with_stats(skip=skip, limit=limit)

    except Exception as exc:
        logger.error(f"Error retrieving teams: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving teams"
        )


@router.get(
    "/rankings",
    response_model=List[TeamResponse],
    summary="Get team rankings",
    description="Get teams ranked by their global ELO rating.",
)
async def get_team_rankings_endpoint(
    limit: int = Query(200, ge=1, le=1000, description="Maximum number of teams to return"),
    days_since_last_match: Optional[int] = Query(
        30, ge=1, description="Only include teams whose last match was at least this many days ago"
    ),
) -> List[TeamResponse]:
    """
    Get teams sorted by ELO rating for rankings display.

    This endpoint retrieves teams sorted by ELO rating with support for:
    - Limiting the number of results
    - Filtering by days since last match
    - Automatic inclusion of player details for each team
    - Rank information for each team

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 200 (max 1000).
    days_since_last_match : Optional[int], optional
        Only include teams whose last match was at least this many days ago, by default 30.

    Returns
    -------
    List[TeamResponse]
        List of teams sorted by ELO in descending order with rank information.
        Each team includes complete player details and ELO ratings.
    """
    try:
        return teams_service.get_active_team_rankings(limit=limit, days_since_last_match=days_since_last_match)

    except Exception as exc:
        logger.error(f"Error retrieving team rankings: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team rankings",
        )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team details",
    description="Retrieve detailed information about a specific team, including player details.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Team not found",
        },
    },
)
async def get_team_endpoint(
    team_id: int = Path(..., gt=0, description="The ID of the team to retrieve")
) -> TeamResponse:
    """
    Retrieve detailed information about a specific team.

    This endpoint provides comprehensive team information including:
    - Team metadata (ID, creation date, ELO ratings)
    - Complete player information for both team members
    - Team statistics (if available)

    Parameters
    ----------
    team_id : int
        The unique identifier of the team to retrieve.


    Returns
    -------
    TeamResponse
        Detailed team information including player details and statistics.


    Raises
    ------
    HTTPException
        If the team is not found (404 status code).
    """
    try:
        return teams_service.get_team_by_id(team_id)

    except TeamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error retrieving team {team_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the team"
        )
    except Exception as exc:
        logger.error(f"Unexpected error retrieving team {team_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{team_id}/statistics",
    response_model=Dict[str, Any],
    summary="Get team statistics",
    description="Retrieve detailed statistics for a specific team.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Team not found",
        },
    },
)
async def get_team_statistics_endpoint(
    team_id: int = Path(..., gt=0, description="The ID of the team")
) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific team.

    This endpoint provides comprehensive statistics for a team, including:
    - Win/loss record
    - ELO rating history
    - Performance metrics

    Parameters
    ----------
    team_id : int
        The unique identifier of the team.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing various statistics about the team.

    Raises
    ------
    HTTPException
        If the team is not found (404 status code) or other errors occur.
    """
    try:
        return stats_service.get_team_statistics(team_id=team_id)

    except TeamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error retrieving statistics for team {team_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team statistics",
        )
    except Exception as exc:
        logger.error(f"Unexpected error retrieving statistics for team {team_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.get(
    "/{team_id}/matches",
    response_model=List[MatchWithEloResponse],
    summary="Get team matches",
    description="Get a list of matches for a specific team with optional filtering.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Team not found",
        },
    },
)
async def get_team_matches_endpoint(
    team_id: int = Path(..., gt=0, description="The ID of the team"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of matches to return"),
) -> List[MatchWithEloResponse]:
    """
    Get a list of matches for a specific team with optional filtering.

    This endpoint retrieves match history for a team with support for:
    - Pagination (skip and limit parameters)

    Parameters
    ----------
    team_id : int
        The ID of the team to get matches for.
    skip : int, optional
        Number of matches to skip for pagination, by default 0.
    limit : int, optional
        Maximum number of matches to return, by default 100 (max 100).

    Returns
    -------
    List[MatchWithEloResponse]
        List of matches involving the specified team.
    """
    try:
        return teams_service.get_team_matches(team_id=team_id, offset=skip, limit=limit)

    except TeamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error retrieving matches for team {team_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving team matches"
        )
    except Exception as exc:
        logger.error(f"Unexpected error retrieving matches for team {team_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team",
    description="Update a team's details.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Team not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid team data",
        },
    },
)
async def update_team_endpoint(
    team_data: TeamUpdate,
    team_id: int = Path(..., gt=0, description="The ID of the team to update"),
) -> TeamResponse:
    """
    Update a team's details.

    This endpoint allows updating various team attributes including:
    - Player assignments (player1_id, player2_id)
    - ELO ratings (global_elo, current_elo)
    - Team metadata (name, description, etc.)

    Parameters
    ----------
    team_data : TeamUpdate
        The updated team data. Only the fields that need to be updated should be included.
    team_id : int
        The ID of the team to update.

    Returns
    -------
    TeamResponse
        The updated team details with complete player information.


    Raises
    ------
    HTTPException
        If the team is not found (404 status code) or the update fails.
    """
    try:
        return teams_service.update_existing_team(team_id=team_id, team_update=team_data)

    except TeamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InvalidTeamDataError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error updating team {team_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the team"
        )
    except Exception as exc:
        logger.error(f"Unexpected error updating team {team_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="Delete a team by ID. This operation cannot be undone.",
)
async def delete_team_endpoint(team_id: int = Path(..., gt=0, description="The ID of the team to delete")) -> None:
    """
    Delete a team by ID.

    This endpoint allows administrators to delete a team from the system.
    The team will be permanently removed from the database.

    Parameters
    ----------
    team_id : int
        The unique identifier of the team to delete.


    Raises
    ------
    HTTPException
        If the team is not found (404 status code) or deletion fails.
    """
    try:
        teams_service.delete_team(team_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except TeamNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TeamOperationError as exc:
        logger.error(f"Error deleting team {team_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the team"
        )
    except Exception as exc:
        logger.error(f"Unexpected error deleting team {team_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
