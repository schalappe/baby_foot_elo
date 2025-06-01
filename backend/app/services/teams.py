# -*- coding: utf-8 -*-
"""
This module provides business logic and data transformation for team-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from typing import List

from loguru import logger

from app.db.repositories.players import get_all_players, get_player_by_id_or_name
from app.db.repositories.stats import get_team_stats
from app.db.repositories.teams import (
    create_team_by_player_ids,
    delete_team_by_id,
    get_all_teams,
    get_team_by_id,
    get_teams_by_player_id,
    update_team_elo,
)
from app.exceptions.teams import (
    InvalidTeamDataError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    TeamOperationError,
)
from app.models.team import TeamCreate, TeamResponse, TeamUpdate
from app.services import players as players_service


def get_team(team_id: int) -> TeamResponse:
    """
    Retrieve a team by its ID with associated player details.

    Parameters
    ----------
    team_id : int
        The unique identifier of the team.


    Returns
    -------
    TeamResponse
        The team's details with player information.


    Raises
    ------
    TeamNotFoundError
        If no team with the specified ID is found.
    TeamOperationError
        If there's an error retrieving the team's data.
    """
    try:
        # ##: Get team stats.
        team = get_team_stats(team_id)
        if not team:
            raise TeamNotFoundError(f"ID: {team_id}")

        # ##: Get player details for both team members.
        player1 = players_service.get_player(team["player1_id"])
        player2 = players_service.get_player(team["player2_id"])

        if not player1 or not player2:
            logger.error(f"One or both players not found for team {team_id}")
            raise TeamOperationError("Could not retrieve player details for the team.")

        response = TeamResponse(
            team_id=team_id,
            global_elo=team["global_elo"],
            created_at=team["created_at"],
            last_match_at=team["last_match_at"],
            matches_played=team["matches_played"],
            wins=team["wins"],
            losses=team["losses"],
            win_rate=team["win_rate"],
            player1_id=team["player1_id"],
            player2_id=team["player2_id"],
            player1=player1,
            player2=player2,
        )
        return response

    except (TeamNotFoundError, TeamOperationError):
        raise
    except Exception as exc:
        logger.error(f"Error retrieving team with ID {team_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve team with ID {team_id}") from exc


# ##: TODO: Delete team should also delete all matches associated with it.
# and recalculate ELO ratings for all players.
def delete_team(team_id: int) -> bool:
    """
    Delete a team by its ID.

    Parameters
    ----------
    team_id : int
        The ID of the team to delete.


    Returns
    -------
    bool
        True if the team was deleted successfully, False otherwise.

    Raises
    ------
    TeamOperationError
        If the deletion operation fails.
    """
    try:
        # ##: Check if team exists
        if not get_team(team_id):
            raise TeamNotFoundError(f"ID: {team_id}")

        # ##: Delete the team from the database
        success = delete_team_by_id(team_id)
        if not success:
            raise TeamOperationError(f"Failed to delete team with ID {team_id}")

        logger.info(f"Successfully deleted team with ID {team_id}")
        return True

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error deleting team with ID {team_id}: {exc}")
        raise TeamOperationError(f"Failed to delete team with ID {team_id}") from exc


def create_new_team(team_data: TeamCreate) -> TeamResponse:
    """
    Create a new team with the provided data.

    Parameters
    ----------
    team_data : TeamCreate
        The data for the new team.


    Returns
    -------
    TeamResponse
        The created team's details with player information.


    Raises
    ------
    InvalidTeamDataError
        If the team data is invalid.
    TeamAlreadyExistsError
        If a team with the same players already exists.
    TeamOperationError
        If there's an error creating the team.
    """
    try:
        # ##: Get players to check if they exist.
        player1 = get_player_by_id_or_name(player_id=team_data.player1_id)
        player2 = get_player_by_id_or_name(player_id=team_data.player2_id)

        if not player1 or not player2:
            missing_players = []
            if not player1:
                missing_players.append(str(team_data.player1_id))
            if not player2:
                missing_players.append(str(team_data.player2_id))
            raise InvalidTeamDataError(f"Players not found: {', '.join(missing_players)}")

        # ##: Create the team in the database.
        team_id = create_team_by_player_ids(
            player1_id=team_data.player1_id,
            player2_id=team_data.player2_id,
            global_elo=team_data.global_elo,
        )
        if not team_id:
            raise TeamOperationError("Failed to create team in the database.")

        # ##: Return the created team with full details.
        return get_team(team_id)

    except (TeamAlreadyExistsError, InvalidTeamDataError, TeamOperationError):
        raise
    except Exception as exc:
        logger.error(f"Error creating team: {exc}")
        if "UNIQUE constraint failed" in str(exc):
            raise TeamAlreadyExistsError("A team with these players already exists.") from exc
        raise TeamOperationError("Failed to create team") from exc


def update_existing_team(team_id: int, team_update: TeamUpdate) -> TeamResponse:
    """
    Update an existing team's information.

    Currently, teams are mostly immutable, but this can be used for future updates.

    Parameters
    ----------
    team_id : int
        The ID of the team to update.
    team_update : TeamUpdate
        The updated team data.


    Returns
    -------
    TeamResponse
        The updated team's details.


    Raises
    ------
    TeamNotFoundError
        If no team with the specified ID is found.
    TeamOperationError
        If the update operation fails.
    """
    try:
        # ##: Check if team exists.
        if not get_team_by_id(team_id):
            raise TeamNotFoundError(f"ID: {team_id}")

        # ##: Update the team in the database.
        success = update_team_elo(team_id, global_elo=team_update.global_elo, last_match_at=team_update.last_match_at)
        if not success:
            raise TeamOperationError(f"Failed to update team with ID {team_id}")

        return get_team(team_id)

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error updating team with ID {team_id}: {exc}")
        raise TeamOperationError(f"Failed to update team with ID {team_id}") from exc


def get_teams_by_player(player_id: int) -> List[TeamResponse]:
    """
    Retrieve all teams that include a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player to find teams for.


    Returns
    -------
    List[TeamResponse]
        A list of teams that include the specified player.


    Raises
    ------
    TeamOperationError
        If there's an error retrieving the teams.
    """
    try:
        teams = get_teams_by_player_id(player_id)
        return [get_team(team["team_id"]) for team in teams]
    except Exception as exc:
        logger.error(f"Error retrieving teams for player {player_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve teams for player {player_id}") from exc


def get_all_teams_with_stats(skip: int = 0, limit: int = 100) -> List[TeamResponse]:
    """
    Retrieve all teams with their details, efficiently batch-fetching players to avoid N+1 queries.

    Parameters
    ----------
    skip : int, optional
        Number of teams to skip for pagination, by default 0.
    limit : int, optional
        Maximum number of teams to return, by default 100.

    Returns
    -------
    List[TeamResponse]
        A list of teams with their details.

    Raises
    ------
    TeamOperationError
        If there's an error retrieving the teams.
    """
    try:
        teams = get_all_teams(limit=limit, offset=skip)
        return [TeamResponse(**team) for team in teams]
    except Exception as exc:
        logger.error(f"Error retrieving teams: {exc}")
        raise TeamOperationError("Failed to retrieve teams") from exc
