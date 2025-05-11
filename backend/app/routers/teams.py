# -*- coding: utf-8 -*-
"""
This module defines FastAPI endpoints for managing teams in the Baby Foot Elo system.
It supports creating, listing, retrieving, and deleting team records, as well as fetching team rankings and match history.

Endpoints:
    - POST /api/v1/teams/: Create a new team
    - GET /api/v1/teams/: List all teams
    - GET /api/v1/teams/rankings: Get team rankings
    - GET /api/v1/teams/{team_id}: Retrieve a team's details
    - DELETE /api/v1/teams/{team_id}: Delete a team
    - GET /api/v1/teams/{team_id}/matches: Get team's match history
    - GET /api/v1/teams/player/{player_id}: Get teams for a specific player

Notes
-----
- All endpoints return or accept Pydantic models for request and response bodies.
- Team ELO is calculated based on the ELO ratings of its players.
- Teams must consist of exactly two players.
- All endpoints include proper validation and error handling.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from loguru import logger

from app.crud.matches import get_matches_by_team
from app.crud.players import get_player
from app.crud.teams import (
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_team_rankings,
    get_teams_by_player,
)
from app.models.match import MatchResponse
from app.models.team import TeamCreate, TeamResponse
from app.services.elo import calculate_team_elo
from app.utils.validation import ValidationErrorResponse, validate_team_players

router = APIRouter(
    prefix="/api/v1/teams",
    tags=["teams"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request - invalid input parameters"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    description="Create a new team with two players.",
)
async def create_team_endpoint(team: TeamCreate):
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
        - 400: Invalid team data or team already exists
        - 404: Player not found
        - 500: Internal server error
    """
    # ##: Validate team data
    try:
        validate_team_players(team.player1_id, team.player2_id)
    except ValidationErrorResponse as e:
        raise e

    # ##: Validate that both players exist.
    player1 = get_player(team.player1_id)
    if not player1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {team.player1_id} not found",
        )

    player2 = get_player(team.player2_id)
    if not player2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {team.player2_id} not found",
        )

    # ##: Calculate initial team ELO based on player ELOs.
    team.global_elo = calculate_team_elo(player1["global_elo"], player2["global_elo"])
    team.current_month_elo = calculate_team_elo(player1["current_month_elo"], player2["current_month_elo"])

    # ##: Create the team.
    team_id = create_team(
        player1_id=team.player1_id,
        player2_id=team.player2_id,
        global_elo=team.global_elo,
        current_month_elo=team.current_month_elo,
    )

    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create team. Team may already exist.",
        )

    # ##: Get the created team.
    team_data = get_team(team_id)
    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team was created but could not be retrieved.",
        )

    # ##: Create response with player details.
    response = TeamResponse(**team_data)
    response.player1 = player1
    response.player2 = player2

    return response


@router.get(
    "/",
    response_model=List[TeamResponse],
    summary="List all teams",
    description="Get a list of all teams with optional pagination and filtering by ELO rating or player ID.",
)
async def get_teams_endpoint(
    skip: int = Query(0, ge=0, description="Number of teams to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of teams to return"),
    min_elo: Optional[float] = Query(None, ge=0, description="Minimum global ELO rating"),
    max_elo: Optional[float] = Query(None, ge=0, description="Maximum global ELO rating"),
    player_id: Optional[int] = Query(None, gt=0, description="Filter teams by player ID"),
):
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

    Notes
    -----
    - When filtering by player_id, the endpoint uses a specialized query to find teams containing that player
    - Otherwise, it retrieves all teams and applies filters in memory
    - ELO filtering is applied after retrieving the teams
    - Pagination is applied last, after all filtering
    """
    # ##: Get teams based on filters.
    if player_id:
        teams_data = get_teams_by_player(player_id)
    else:
        teams_data = get_all_teams()

    # ##: Apply ELO filters.
    if min_elo is not None:
        teams_data = [t for t in teams_data if t["global_elo"] >= min_elo]
    if max_elo is not None:
        teams_data = [t for t in teams_data if t["global_elo"] <= max_elo]

    # ##: Apply pagination.
    teams_data = teams_data[skip : skip + limit]

    # ##: Populate player details for each team.
    result = []
    for team_data in teams_data:
        team = TeamResponse(**team_data)
        team.player1 = get_player(team.player1_id)
        team.player2 = get_player(team.player2_id)
        result.append(team)

    return result


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team details",
    description="Get detailed information about a specific team including player details.",
)
async def get_team_endpoint(team_id: int = Path(..., gt=0, description="The ID of the team to retrieve")):
    """
    Get detailed information about a specific team.

    This endpoint retrieves comprehensive team information including:
    - Basic team details (ID, creation date, ELO ratings)
    - Complete player information for both team members
    - Calculated team statistics

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve. Must be a positive integer.

    Returns
    -------
    TeamResponse
        Team details including player information, ELO ratings, and statistics.

    Raises
    ------
    HTTPException
        If the team is not found (404 status code).

    Notes
    -----
    - The endpoint automatically fetches player details for both team members
    - Team ELO is stored in the database and not recalculated on retrieval
    - Debug logs are generated to track team data retrieval
    """
    team_data = get_team(team_id)
    logger.info(f"Team data: {team_data}")
    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # ##: Create response with player details.
    response = TeamResponse(**team_data)
    response.player1 = get_player(response.player1_id)
    response.player2 = get_player(response.player2_id)

    return response


@router.get(
    "/{team_id}/matches",
    response_model=List[MatchResponse],
    summary="Get team matches",
    description="Get all matches played by a specific team with optional pagination.",
)
async def get_team_matches_endpoint(
    team_id: int = Path(..., gt=0, description="The ID of the team to retrieve matches for"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of matches to return"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
):
    """
    Get all matches played by a specific team.

    This endpoint retrieves the match history for a specific team with support for:
    - Pagination (skip and limit parameters)
    - Verification of team existence
    - Inclusion of complete match details including opponent information

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve matches for. Must be a positive integer.
    limit : int, optional
        Maximum number of matches to return, by default 50 (max 100).
    skip : int, optional
        Number of matches to skip for pagination, by default 0.

    Returns
    -------
    List[MatchResponse]
        List of matches played by the team, including both won and lost matches.
        Each match includes complete details about the match and opponent team.

    Raises
    ------
    HTTPException
        If the team is not found (404 status code).

    Notes
    -----
    - Matches are returned in descending order by date (newest first)
    - The endpoint includes both matches where the team won and where they lost
    - Each match includes a 'won' field indicating whether the team won that match
    - The team's existence is verified before retrieving matches
    """
    # ##: Verify that the team exists.
    team_data = get_team(team_id)
    if not team_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # ##: Get matches for the team.
    matches = get_matches_by_team(team_id)

    # ##: Apply pagination.
    matches = matches[skip : skip + limit]

    # ##: Convert to response model.
    result = []
    for match in matches:
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
    "/rankings",
    response_model=List[TeamResponse],
    summary="Get team rankings",
    description="Get teams sorted by ELO rating (global or monthly) with rank information.",
)
async def get_team_rankings_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of teams to return"),
    use_monthly_elo: bool = Query(False, description="If True, sort by current month ELO instead of global ELO"),
):
    """
    Get teams sorted by ELO rating for rankings display.

    This endpoint retrieves teams sorted by ELO rating with support for:
    - Limiting the number of results
    - Choosing between global (all-time) or monthly ELO for ranking
    - Automatic inclusion of player details for each team
    - Rank information for each team

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100 (max 1000).
    use_monthly_elo : bool, optional
        If True, sort by current_month_elo instead of global_elo, by default False.
        This allows viewing rankings for the current month only.

    Returns
    -------
    List[TeamResponse]
        List of teams sorted by ELO in descending order with rank information.
        Each team includes complete player details and ELO ratings.

    Notes
    -----
    - Teams are sorted in descending order by the selected ELO type
    - Each team includes a 'rank' field indicating its position in the rankings
    - The endpoint automatically fetches player details for both team members
    - This is useful for leaderboard displays and ranking tables
    """
    # ##: Get ranked teams from database.
    teams_data = get_team_rankings(limit=limit, use_monthly_elo=use_monthly_elo)

    # ##: Populate player details for each team.
    result = []
    for team_data in teams_data:
        team = TeamResponse(**team_data)
        team.player1 = get_player(team.player1_id)
        team.player2 = get_player(team.player2_id)
        result.append(team)

    return result


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="Delete a team by ID. This operation cannot be undone.",
)
async def delete_team_endpoint(team_id: int = Path(..., gt=0, description="The ID of the team to delete")):
    """
    Delete a team by ID.

    This endpoint permanently removes a team from the database with the following process:
    - Verifies that the team exists before attempting deletion
    - Removes the team record from the database
    - Returns a 204 No Content response on success

    Parameters
    ----------
    team_id : int
        ID of the team to delete. Must be a positive integer.

    Raises
    ------
    HTTPException
        If the team is not found (404 status code) or deletion fails (500 status code).

    Notes
    -----
    - This operation cannot be undone
    - Related match records are not deleted and will maintain references to the deleted team ID
    - The endpoint performs validation before attempting deletion to provide appropriate error messages
    - Returns no content (204) on successful deletion
    """
    # ##: First check if the team exists.
    existing_team = get_team(team_id)
    if not existing_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )

    # ##: Delete the team.
    success = delete_team(team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete team with ID {team_id}",
        )
