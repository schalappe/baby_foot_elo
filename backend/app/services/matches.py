# -*- coding: utf-8 -*-
"""
This module provides business logic for match operations, acting as an intermediary between the API endpoints
and the data access layer. It handles validation, business rules, and orchestrates calls to the repository layer.
"""

from datetime import datetime, timezone
from typing import List, Optional, Union

from loguru import logger

from app.db.repositories.matches import (
    create_match,
    delete_match,
    get_all_matches,
    get_match,
    get_matches_by_team,
)
from app.db.repositories.players import batch_update_players
from app.db.repositories.players_elo_history import (
    batch_record_player_elo_updates,
    get_player_elo_history_by_match,
)
from app.db.repositories.teams import batch_update_teams
from app.db.repositories.teams_elo_history import (
    batch_record_team_elo_updates,
    get_team_elo_history_by_match,
)
from app.exceptions.matches import (
    InvalidMatchTeamsError,
    MatchCreationError,
    MatchDeletionError,
    MatchNotFoundError,
)
from app.models.match import MatchCreate, MatchResponse, MatchWithEloResponse
from app.services.elo import process_match_result
from app.services.teams import get_team_by_id


def create_new_match(match_data: MatchCreate) -> MatchWithEloResponse:
    """
    Create a new match and update ELO ratings for all involved players.

    This service method orchestrates the complete match creation process:
    1. Validates the match data
    2. Creates the match record
    3. Updates player ELO ratings
    4. Updates team ELO ratings
    5. Records ELO history

    Parameters
    ----------
    match_data : MatchCreate
        The match data including winner and loser team IDs.

    Returns
    -------
    MatchWithEloResponse
        The created match with ELO changes.

    Raises
    ------
    InvalidMatchTeamsError
        If the winner and loser teams are the same.
    MatchCreationError
        If there's an error creating the match.
    """
    # ##: Validate teams are different.
    if match_data.winner_team_id == match_data.loser_team_id:
        raise InvalidMatchTeamsError()

    try:
        # ##: Get team details.
        winner_team = get_team_by_id(match_data.winner_team_id)
        loser_team = get_team_by_id(match_data.loser_team_id)

        if not winner_team or not loser_team:
            raise MatchCreationError(detail="One or both teams not found")

        # ##: Create match record.
        match_id = create_match(
            winner_team_id=match_data.winner_team_id,
            loser_team_id=match_data.loser_team_id,
            played_at=match_data.played_at,
            is_fanny=match_data.is_fanny,
            notes=match_data.notes,
        )

        if not match_id:
            raise MatchCreationError(detail="Failed to create match record")

        # ##: Process ELO updates.
        players_change, teams_change = process_match_result(winning_team=winner_team, losing_team=loser_team)

        # ##: Update players.
        batch_update_players(
            [{"player_id": player_id, "global_elo": change["new_elo"]} for player_id, change in players_change.items()]
        )

        # ##: Update players' ELO history.
        batch_record_player_elo_updates(
            [
                {
                    "player_id": player_id,
                    "match_id": match_id,
                    "old_elo": change["old_elo"],
                    "new_elo": change["new_elo"],
                    "date": match_data.played_at,
                }
                for player_id, change in players_change.items()
            ]
        )

        # ##: Update teams.
        batch_update_teams(
            [
                {"team_id": team_id, "global_elo": change["new_elo"], "last_match_at": match_data.played_at}
                for team_id, change in teams_change.items()
            ]
        )

        # ##: Update teams' ELO history.
        batch_record_team_elo_updates(
            [
                {
                    "team_id": team_id,
                    "match_id": match_id,
                    "old_elo": change["old_elo"],
                    "new_elo": change["new_elo"],
                    "date": match_data.played_at,
                }
                for team_id, change in teams_change.items()
            ]
        )

        # ##: Prepare response.
        response = MatchWithEloResponse(
            match_id=match_id,
            winner_team=winner_team,
            loser_team=loser_team,
            winner_team_id=match_data.winner_team_id,
            loser_team_id=match_data.loser_team_id,
            is_fanny=match_data.is_fanny,
            played_at=match_data.played_at,
            notes=match_data.notes,
            elo_changes=players_change,
        )

        return response

    except Exception as exc:
        logger.error(f"Error creating match: {str(exc)}")
        if not isinstance(exc, (InvalidMatchTeamsError, MatchCreationError)):
            raise MatchCreationError(detail=str(exc)) from exc
        raise


def get_match_by_id(match_id: int) -> MatchResponse:
    """
    Retrieve a match by its ID.

    Parameters
    ----------
    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    MatchResponse
        The match details.

    Raises
    ------
    MatchNotFoundError
        If no match is found with the given ID.
    """
    match_data = get_match(match_id)
    if not match_data:
        raise MatchNotFoundError(identifier=str(match_id))

    # ##: Fetch team details.
    return MatchResponse(
        match_id=match_data["match_id"],
        winner_team=get_team_by_id(match_data["winner_team_id"]),
        loser_team=get_team_by_id(match_data["loser_team_id"]),
        winner_team_id=match_data["winner_team_id"],
        loser_team_id=match_data["loser_team_id"],
        is_fanny=match_data["is_fanny"],
        played_at=match_data["played_at"],
        notes=match_data.get("notes"),
    )


def get_matches(
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[int] = None,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
    is_fanny: Optional[bool] = None,
) -> List[MatchResponse]:
    """
    Retrieve a list of matches with optional filtering.

    Parameters
    ----------
    skip : int, optional
        Number of matches to skip for pagination.
    limit : int, optional
        Maximum number of matches to return.
    team_id : int, optional
        Filter matches by team ID.
    start_date : Union[datetime, str], optional
        Filter matches by start date.
    end_date : Union[datetime, str], optional
        Filter matches by end date.
    is_fanny : bool, optional
        Filter by fanny matches.

    Returns
    -------
    List[MatchResponse]
        List of matches matching the criteria.
    """
    logger.debug(
        "Retrieving matches with filters", team_id=team_id, start_date=start_date, end_date=end_date, is_fanny=is_fanny
    )

    try:
        if team_id:
            matches_data = get_matches_by_team(
                team_id,
                limit=limit,
                offset=skip,
                is_fanny=is_fanny,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            matches_data = get_all_matches(limit=limit, offset=skip)

        # ##: Convert to response models.
        matches = []
        for match_data in matches_data:
            try:
                match = MatchResponse(
                    match_id=match_data["match_id"],
                    winner_team=get_team_by_id(match_data["winner_team_id"]),
                    loser_team=get_team_by_id(match_data["loser_team_id"]),
                    winner_team_id=match_data["winner_team_id"],
                    loser_team_id=match_data["loser_team_id"],
                    is_fanny=match_data["is_fanny"],
                    played_at=match_data["played_at"],
                    notes=match_data.get("notes"),
                )
                matches.append(match)
            except Exception as exc:
                logger.error(f"Error processing match {match_data.get('match_id')}: {str(exc)}")
                continue

        return matches

    except Exception as exc:
        logger.error(f"Error retrieving matches: {str(exc)}")
        raise


# ##: TODO: Reverse the Elo changes when deleting a match.
def delete_match_by_id(match_id: int) -> bool:
    """
    Delete a match by its ID.

    Parameters
    ----------
    match_id : int
        The ID of the match to delete.

    Returns
    -------
    bool
        True if the match was deleted successfully, False otherwise.

    Raises
    ------
    MatchDeletionError
        If there's an error deleting the match.
    """
    try:
        # ##: Verify match exists.
        if not get_match(match_id):
            raise MatchNotFoundError(identifier=str(match_id))

        success = delete_match(match_id)
        if not success:
            raise MatchDeletionError(detail="Failed to delete match")
        return True

    except Exception as exc:
        logger.error(f"Error deleting match {match_id}: {exc}")
        if not isinstance(exc, MatchDeletionError):
            raise MatchDeletionError(detail=str(exc)) from exc
        raise


def get_match_with_elo_player(match_id: int) -> MatchWithEloResponse:
    """
    Get a match with ELO changes for all players.

    Parameters
    ----------
    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    MatchWithEloResponse
        The match details with ELO changes.

    Raises
    ------
    MatchNotFoundError
        If no match is found with the given ID.
    """
    logger.debug(f"Retrieving match with ELO changes for match ID: {match_id}")

    try:
        # ##: Get basic match data.
        match_data = get_match(match_id)
        if not match_data:
            raise MatchNotFoundError(identifier=str(match_id))

        # ##: Get ELO history for this match.
        elo_history = get_player_elo_history_by_match(match_id)

        # ##: Convert to response model.
        response = MatchWithEloResponse(
            match_id=match_data["match_id"],
            winner_team=get_team_by_id(match_data["winner_team_id"]),
            loser_team=get_team_by_id(match_data["loser_team_id"]),
            winner_team_id=match_data["winner_team_id"],
            loser_team_id=match_data["loser_team_id"],
            is_fanny=match_data["is_fanny"],
            played_at=match_data["played_at"],
            notes=match_data.get("notes"),
            elo_changes=(
                {
                    eh["player_id"]: {
                        "old_elo": eh["old_elo"],
                        "new_elo": eh["new_elo"],
                        "difference": eh["difference"],
                    }
                    for eh in elo_history
                }
                if elo_history
                else {}
            ),
        )

        return response

    except Exception as exc:
        logger.error(f"Error retrieving match with ELO changes: {exc}")
        if not isinstance(exc, MatchNotFoundError):
            raise MatchNotFoundError(identifier=str(match_id)) from exc
        raise


def get_match_with_elo_team(match_id: int) -> MatchWithEloResponse:
    """
    Get a match with ELO changes for all teams.

    Parameters
    ----------
    match_id : int
        The ID of the match to retrieve.

    Returns
    -------
    MatchWithEloResponse
        The match details with ELO changes.

    Raises
    ------
    MatchNotFoundError
        If no match is found with the given ID.
    """
    logger.debug(f"Retrieving match with ELO changes for match ID: {match_id}")

    try:
        # ##: Get basic match data.
        match_data = get_match(match_id)
        if not match_data:
            raise MatchNotFoundError(identifier=str(match_id))

        # ##: Get ELO history for this match.
        elo_history = get_team_elo_history_by_match(match_id)

        # ##: Convert to response model.
        response = MatchWithEloResponse(
            match_id=match_data["match_id"],
            winner_team=get_team_by_id(match_data["winner_team_id"]),
            loser_team=get_team_by_id(match_data["loser_team_id"]),
            winner_team_id=match_data["winner_team_id"],
            loser_team_id=match_data["loser_team_id"],
            is_fanny=match_data["is_fanny"],
            played_at=match_data["played_at"],
            notes=match_data.get("notes"),
            elo_changes=(
                {
                    eh["team_id"]: {
                        "old_elo": eh["old_elo"],
                        "new_elo": eh["new_elo"],
                        "difference": eh["difference"],
                    }
                    for eh in elo_history
                }
                if elo_history
                else {}
            ),
        )

        return response

    except Exception as exc:
        logger.error(f"Error retrieving match with ELO changes: {exc}")
        if not isinstance(exc, MatchNotFoundError):
            raise MatchNotFoundError(identifier=str(match_id)) from exc
        raise
