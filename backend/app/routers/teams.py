# -*- coding: utf-8 -*-
"""
Router for team-related endpoints.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger

from app.crud.matches import create_match, get_matches_by_team
from app.crud.players import get_player
from app.crud.teams import (
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_team_rankings,
    get_teams_by_player,
    update_team,
)
from app.models.match import MatchBase, MatchCreate, MatchResponse
from app.models.team import TeamCreate, TeamResponse
from app.services.elo import (
    calculate_elo_change,
    calculate_team_elo,
    calculate_win_probability,
)

router = APIRouter(
    prefix="/api/v1/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
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

    Parameters
    ----------
    team : TeamCreate
        Team data including player IDs.

    Returns
    -------
    TeamResponse
        Created team data.

    Raises
    ------
    HTTPException
        If player IDs are invalid or team creation fails.
    """
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
    description="Get a list of all teams with optional pagination and filtering.",
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

    Parameters
    ----------
    skip : int, optional
        Number of teams to skip, by default 0.
    limit : int, optional
        Maximum number of teams to return, by default 100.
    min_elo : Optional[float], optional
        Minimum global ELO rating, by default None.
    max_elo : Optional[float], optional
        Maximum global ELO rating, by default None.
    player_id : Optional[int], optional
        Filter teams by player ID, by default None.

    Returns
    -------
    List[TeamResponse]
        List of teams matching the criteria.
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
    description="Get detailed information about a specific team.",
)
async def get_team_endpoint(team_id: int):
    """
    Get detailed information about a specific team.

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve.

    Returns
    -------
    TeamResponse
        Team details including player information.

    Raises
    ------
    HTTPException
        If the team is not found.
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
    summary="Get team's match history",
    description="Get all matches played by a specific team.",
)
async def get_team_matches_endpoint(
    team_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of matches to return"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
):
    """
    Get all matches played by a specific team.

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve matches for.
    limit : int, optional
        Maximum number of matches to return, by default 50.
    skip : int, optional
        Number of matches to skip, by default 0.

    Returns
    -------
    List[MatchResponse]
        List of matches played by the team.

    Raises
    ------
    HTTPException
        If the team is not found.
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
    description="Get teams sorted by ELO rating (global or monthly).",
)
async def get_team_rankings_endpoint(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of teams to return"),
    use_monthly_elo: bool = Query(False, description="If True, sort by current month ELO instead of global ELO"),
):
    """
    Get teams sorted by ELO rating.

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100
    use_monthly_elo : bool, optional
        If True, sort by current_month_elo instead of global_elo, by default False

    Returns
    -------
    List[TeamResponse]
        List of teams sorted by ELO in descending order with rank information
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
    summary="Delete a team",
    description="Delete a team by ID.",
)
async def delete_team_endpoint(team_id: int):
    """
    Delete a team by ID.

    Parameters
    ----------
    team_id : int
        ID of the team to delete.

    Raises
    ------
    HTTPException
        If the team is not found or deletion fails.
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
