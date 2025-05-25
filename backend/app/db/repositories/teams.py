# -*- coding: utf-8 -*-
"""
Operations related to the Teams table.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from duckdb import ConstraintException
from loguru import logger

from app.db.builders import (
    DeleteQueryBuilder,
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)
from app.db.session import transaction, with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def create_team_by_player_ids(
    player1_id: int,
    player2_id: int,
    global_elo: int = 1000,
    last_match_at: Optional[Union[str, datetime]] = None,
) -> Optional[int]:
    """
    Create a new team in the database.

    Parameters
    ----------
    player1_id : int
        ID of the first player.
    player2_id : int
        ID of the second player.
    global_elo : int, optional
        Initial global ELO rating, by default 1000.
    last_match_at : Optional[Union[str, datetime]], optional
        Timestamp of the last match, by default None.

    Returns
    -------
    Optional[int]
        ID of the newly created team, or the existing team ID if a duplicate is found.
    """
    try:
        with transaction() as db_manager:
            # ##: Check if team with same players exists (order-insensitive).
            existing_team = db_manager.fetchone(
                """
                SELECT team_id FROM Teams
                WHERE (player1_id = ? AND player2_id = ?) OR (player1_id = ? AND player2_id = ?)
                """,
                [player1_id, player2_id, player2_id, player1_id],
            )
            if existing_team:
                logger.warning(
                    f"Attempted to create duplicate team for players {player1_id} and {player2_id}. Returning existing team ID: {existing_team[0]}"
                )
                return existing_team[0]

            builder = InsertQueryBuilder("Teams")
            builder.set(
                player1_id=player1_id,
                player2_id=player2_id,
                global_elo=global_elo,
            )
            if last_match_at is not None:
                last_match_at = (
                    datetime.fromisoformat(last_match_at) if isinstance(last_match_at, str) else last_match_at
                )
                builder.set(last_match_at=last_match_at)

            query, params = builder.build()
            result = db_manager.fetchone(f"{query} RETURNING team_id", params)

            if result and result[0]:
                logger.info(f"Created team with ID: {result[0]}")
                return result[0]
            logger.error("Failed to create team or retrieve its ID.")
            return None
    except ConstraintException as constraint_exc:
        logger.error(f"Constraint error on create_team: {constraint_exc}")
        return None
    except Exception as exc:
        logger.error(f"Failed to create team: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_teams_by_player_ids(teams: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Insert multiple teams in a single transaction.

    Parameters
    ----------
    teams : List[Dict[str, Any]]
        List of team dictionaries, each with 'player1_id', 'player2_id' keys.

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created teams, or None for failures.
    """
    team_ids = []
    with transaction() as db_manager:
        for team in teams:
            # ##: Ensure players are ordered consistently.
            p1_id = team["player1_id"]
            p2_id = team["player2_id"]
            if p1_id > p2_id:
                p1_id, p2_id = p2_id, p1_id

            query, params = InsertQueryBuilder("Teams").set(player1_id=p1_id, player2_id=p2_id).build()
            query += " RETURNING team_id"
            result = db_manager.fetchone(query, params)
            team_ids.append(result[0] if result else None)

    return team_ids


@with_retry(max_retries=3, retry_delay=0.5)
def get_team_by_id(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a team by ID.

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve.

    Returns
    -------
    Optional[Dict[str, Any]]
        Team data as a dictionary, or None if not found.
    """
    try:
        result = (
            SelectQueryBuilder("Teams")
            .select(
                "team_id",
                "player1_id",
                "player2_id",
                "global_elo",
                "created_at",
                "last_match_at",
            )
            .where("team_id = ?", team_id)
            .execute(fetch_all=False)
        )
        if result:
            return {
                "team_id": result[0],
                "player1_id": result[1],
                "player2_id": result[2],
                "global_elo": result[3],
                "created_at": result[4],
                "last_match_at": result[5],
            }
        return None
    except Exception as exc:
        logger.error(f"Failed to get team by ID {team_id}: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_teams_by_player_id(player_id: int) -> List[Dict[str, Any]]:
    """
    Get all teams that a specific player is part of.

    Parameters
    ----------
    player_id : int
        ID of the player to find teams for.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries, each containing team details.
    """
    try:
        results = (
            SelectQueryBuilder("Teams")
            .select(
                "team_id",
                "player1_id",
                "player2_id",
                "global_elo",
                "created_at",
                "last_match_at",
            )
            .where("player1_id = ? OR player2_id = ?", player_id, player_id)
            .order_by_clause("created_at DESC")
            .execute()
        )

        if not results:
            return []

        teams = []
        for result in results:
            teams.append(
                {
                    "team_id": result[0],
                    "player1_id": result[1],
                    "player2_id": result[2],
                    "global_elo": result[3],
                    "created_at": result[4],
                    "last_match_at": result[5],
                    "is_player1": result[1] == player_id,
                    "partner_id": result[2] if result[1] == player_id else result[1],
                }
            )

        return teams
    except Exception as exc:
        logger.error(f"Failed to get teams for player ID {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_teams(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all teams from the database.

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100.
    offset : int, optional
        Number of teams to skip for pagination, by default 0.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries.
    """
    try:
        rows = (
            SelectQueryBuilder("Teams")
            .select(
                "team_id",
                "player1_id",
                "player2_id",
                "global_elo",
                "created_at",
                "last_match_at",
            )
            .order_by_clause("global_elo DESC")
            .limit(limit)
            .offset(offset)
            .execute()
        )
        return (
            [
                {
                    "team_id": row[0],
                    "player1_id": row[1],
                    "player2_id": row[2],
                    "global_elo": row[3],
                    "created_at": row[4],
                    "last_match_at": row[5],
                    "rank": idx + 1,
                }
                for idx, row in enumerate(rows)
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get all teams: {exc}")
        return []


def update_team_elo(
    team_id: int,
    global_elo: Optional[int] = None,
    last_match_at: Optional[Union[str, datetime]] = None,
) -> bool:
    """
    Update a team's ELO ratings or last match timestamp.

    Parameters
    ----------
    team_id : int
        ID of the team to update.
    global_elo : Optional[float], optional
        New global ELO value.
    last_match_at : Optional[Union[str, datetime]], optional
        New last match timestamp.

    Returns
    -------
    bool
        True if update was successful, False otherwise.
    """
    if global_elo is None and last_match_at is None:
        logger.warning(f"No fields provided to update for team {team_id}")
        return False

    builder = UpdateQueryBuilder("Teams")
    if global_elo is not None:
        builder.set(global_elo=global_elo)
    if last_match_at is not None:
        last_match_at = datetime.fromisoformat(last_match_at) if isinstance(last_match_at, str) else last_match_at
        builder.set(last_match_at=last_match_at)

    builder.where("team_id = ?", team_id)
    query, params = builder.build()

    with transaction() as db_manager:
        result = db_manager.fetchone(query, params)
        return bool(result[0])


@with_retry(max_retries=3, retry_delay=0.5)
def batch_update_teams_elo(teams: List[Dict[str, Any]]) -> List[bool]:
    """
    Batch update teams in the database.

    Parameters
    ----------
    teams : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary represents a team
        and contains 'team_id' and other fields to update (e.g., 'global_elo', 'last_match_at').

    Returns
    -------
    List[bool]
        A list of booleans indicating the success of each individual team update.
    """
    results: List[bool] = []
    queries_and_params: List[tuple[str, tuple]] = []

    for team_data in teams:
        team_id = team_data.get("team_id")
        if team_id is None:
            logger.warning("Skipping team data without 'team_id' in batch update.")
            results.append(False)
            continue

        update_builder = UpdateQueryBuilder("Teams")
        updated_fields = False
        if "global_elo" in team_data:
            update_builder.set(global_elo=team_data["global_elo"])
            updated_fields = True
        if "last_match_at" in team_data:
            last_match_at = team_data["last_match_at"]
            if isinstance(last_match_at, str):
                last_match_at = datetime.fromisoformat(last_match_at)
            update_builder.set(last_match_at=last_match_at)
            updated_fields = True

        if not updated_fields:
            logger.warning(f"No fields to update for team ID {team_id}.")
            results.append(False)
            continue

        update_builder.where("team_id = ?", team_id)
        query, params = update_builder.build()
        queries_and_params.append((query, params))

    if not queries_and_params:
        return []

    with transaction() as db_manager:
        for query, params in queries_and_params:
            try:
                result = db_manager.fetchone(query, params)
                results.append(bool(result[0]) if result else False)
            except Exception as exc:
                logger.error(f"Error updating team in batch: {exc}")
                results.append(False)
    return results


@with_retry(max_retries=3, retry_delay=0.5)
def delete_team_by_id(team_id: int) -> bool:
    """
    Delete a team from the database.

    Parameters
    ----------
    team_id : int
        ID of the team to delete.

    Returns
    -------
    bool
        True if the deletion was successful, False otherwise.
    """
    query, params = DeleteQueryBuilder("Teams").where("team_id = ?", team_id).build()
    with transaction() as db_manager:
        result = db_manager.fetchone(query, params)
        return bool(result[0])
