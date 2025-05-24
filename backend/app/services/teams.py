# -*- coding: utf-8 -*-
"""
This module provides business logic and data transformation for team-related operations.
It acts as an intermediary between the API routes and the database repositories.
"""

from datetime import datetime
from statistics import mean
from typing import Dict, List, Optional

from loguru import logger

from app.db.repositories.matches import get_matches_by_team
from app.db.repositories.players import get_player
from app.db.repositories.stats import get_team_stats
from app.db.repositories.teams import (
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_team_rankings,
    get_teams_by_player,
    update_team,
)
from app.exceptions.teams import (
    InvalidTeamDataError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    TeamOperationError,
)
from app.models.match import MatchWithEloResponse
from app.models.team import TeamCreate, TeamResponse, TeamUpdate
from app.services import players as players_service
from app.services.elo import calculate_team_elo


def get_team_by_id(team_id: int) -> TeamResponse:
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
        player1 = players_service.get_player_by_id(team["player1_id"])
        player2 = players_service.get_player_by_id(team["player2_id"])

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
        player1 = get_player(team_data.player1_id)
        player2 = get_player(team_data.player2_id)

        if not player1 or not player2:
            missing_players = []
            if not player1:
                missing_players.append(str(team_data.player1_id))
            if not player2:
                missing_players.append(str(team_data.player2_id))
            raise InvalidTeamDataError(f"Players not found: {', '.join(missing_players)}")

        # ##: Create the team in the database.
        team_id = create_team(
            player1_id=team_data.player1_id,
            player2_id=team_data.player2_id,
            global_elo=team_data.global_elo,
        )
        if not team_id:
            raise TeamOperationError("Failed to create team in the database.")

        # ##: Return the created team with full details.
        return get_team_by_id(team_id)

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
        if not get_team(team_id):
            raise TeamNotFoundError(f"ID: {team_id}")

        # ##: Update the team in the database.
        success = update_team(team_id, global_elo=team_update.global_elo, last_match_at=team_update.last_match_at)
        if not success:
            raise TeamOperationError(f"Failed to update team with ID {team_id}")

        return get_team_by_id(team_id)

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error updating team with ID {team_id}: {exc}")
        raise TeamOperationError(f"Failed to update team with ID {team_id}") from exc


# ##: TODO: Delete team should also delete all matches associated with it.
# and recalculate ELO ratings for all players.
def delete_team_by_id(team_id: int) -> bool:
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
        success = delete_team(team_id)
        if not success:
            raise TeamOperationError(f"Failed to delete team with ID {team_id}")

        logger.info(f"Successfully deleted team with ID {team_id}")
        return True

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error deleting team with ID {team_id}: {exc}")
        raise TeamOperationError(f"Failed to delete team with ID {team_id}") from exc


def get_all_teams_with_stats(skip: int = 0, limit: int = 100) -> List[TeamResponse]:
    """
    Retrieve all teams with their details.

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
        responses = [get_team_by_id(team["team_id"]) for team in teams]
        return responses
    except Exception as exc:
        logger.error(f"Error retrieving teams: {exc}")
        raise TeamOperationError("Failed to retrieve teams") from exc


def get_team_elo_history(team: TeamResponse, match_id: int) -> Dict[str, int]:
    """
    Retrieve the ELO history for a team based on a specific match.

    Parameters
    ----------
    team : TeamResponse
        The team for which to retrieve the ELO history.
    match_id : int
        The ID of the match for which to retrieve the ELO history.

    Returns
    -------
    Dict[str, int]
        A dictionary containing the old ELO, new ELO, and difference in ELO.
    """
    player1_elo_history = get_elo_history_by_player_match(team.player1_id, match_id)
    player2_elo_history = get_elo_history_by_player_match(team.player2_id, match_id)

    return {
        "old_elo": calculate_team_elo(player1_elo_history["old_elo"], player2_elo_history["old_elo"]),
        "new_elo": calculate_team_elo(player1_elo_history["new_elo"], player2_elo_history["new_elo"]),
        "difference": int(mean([player1_elo_history["difference"], player2_elo_history["difference"]])),
    }


def get_teams_by_player_id(player_id: int) -> List[TeamResponse]:
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
        teams = get_teams_by_player(player_id)
        return [get_team_by_id(team["team_id"]) for team in teams]
    except Exception as exc:
        logger.error(f"Error retrieving teams for player {player_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve teams for player {player_id}") from exc


def get_team_matches(team_id: int, limit: int = 100, offset: int = 0) -> List[MatchWithEloResponse]:
    """
    Retrieve a paginated list of matches for a specific team.

    Parameters
    ----------
    team_id : int
        The ID of the team.
    limit : int, optional
        Maximum number of matches to return (default: 100).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).

    Returns
    -------
    List[MatchWithEloResponse]
        A list of matches the team participated in.
    """
    try:
        # ##: Check if team exists
        if not get_team(team_id):
            raise TeamNotFoundError(f"ID: {team_id}")

        # ##: Get matches from repository
        matches = get_matches_by_team(team_id, limit=limit, offset=offset)

        # ##: Convert to MatchWithEloResponse models
        result = []
        for match in matches:
            try:
                # ##: Get teams.
                winner_team = get_team_by_id(match["winner_team_id"])
                loser_team = get_team_by_id(match["loser_team_id"])

                # ##: Get ELO change.
                elo_changes = {
                    winner_team.team_id: get_team_elo_history(winner_team, match["match_id"]),
                    loser_team.team_id: get_team_elo_history(loser_team, match["match_id"]),
                }

                # ##: Create match response.
                match_response = MatchWithEloResponse(
                    **match,
                    winner_team=winner_team,
                    loser_team=loser_team,
                    elo_changes=elo_changes,
                )
                result.append(match_response)
            except Exception as e:
                logger.warning(f"Skipping match {match.get('match_id')} due to error: {e}")
                continue

        return result

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving matches for team {team_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve matches for team {team_id}") from exc


def get_active_team_rankings(limit: int = 100, days_since_last_match: Optional[int] = None) -> List[TeamResponse]:
    """
    Retrieve team rankings based on ELO ratings.

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100.
    days_since_last_match : Optional[int], optional
        Only include teams whose last match was at least this many days ago, by default None.

    Returns
    -------
    List[TeamResponse]
        A list of teams sorted by ELO in descending order, with rank information.

    Raises
    ------
    TeamOperationError
        If there's an error retrieving the rankings.
    """
    try:
        # ##: Get team rankings from repository.
        teams = get_team_rankings(limit=limit)

        # ##: Apply additional filters.
        if days_since_last_match is not None:
            filtered_teams = []
            for team in teams:
                if team["last_match_at"] is None:
                    continue

                days = (datetime.now() - team["last_match_at"]).days
                if days >= days_since_last_match:
                    continue

                filtered_teams.append(team)

            # ##: Re-sort after filtering.
            teams = sorted(filtered_teams, key=lambda x: x["global_elo"], reverse=True)

        # ##: Convert to TeamResponse models with rank information.
        result = []
        for rank, team in enumerate(teams, 1):
            try:
                team_response = get_team_by_id(team["team_id"])
                team_response.rank = rank
                result.append(team_response)
            except Exception as e:
                logger.warning(f"Skipping team {team.get('team_id')} in rankings due to error: {e}")
                continue

        return result

    except Exception as exc:
        logger.error(f"Error retrieving team rankings: {exc}")
        raise TeamOperationError("Failed to retrieve team rankings") from exc
