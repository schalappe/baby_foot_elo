# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.db.builders.delete import DeleteQueryBuilder
from app.db.builders.insert import InsertQueryBuilder
from app.db.builders.select import SelectQueryBuilder
from app.db.session import transaction, with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def create_match_by_team_ids(
    winner_team_id: int,
    loser_team_id: int,
    played_at: Union[datetime, str],
    is_fanny: bool = False,
    notes: Optional[str] = None,
) -> Optional[int]:
    """
    Record a new match in the database.

    Parameters
    ----------
    winner_team_id : int
        ID of the winning team
    loser_team_id : int
        ID of the losing team
    played_at : Union[datetime, str]
        Date and time when the match was played
    is_fanny : bool, optional
        Whether the match was a fanny (10-0), by default False
    notes : Optional[str], optional
        Optional notes about the match, by default None

    Returns
    -------
    Optional[int]
        ID of the newly created match, or None on failure
    """
    try:
        # ##: Convert string to datetime if necessary.
        if isinstance(played_at, str):
            played_at = datetime.fromisoformat(played_at)

        # ##: Validate teams are different.
        if winner_team_id == loser_team_id:
            logger.error("Winner and loser team IDs cannot be the same")
            return None

        with transaction() as db_manager:
            query_builder = InsertQueryBuilder("Matches")
            query_builder.set(
                winner_team_id=winner_team_id,
                loser_team_id=loser_team_id,
                is_fanny=is_fanny,
                played_at=played_at,
            )

            # ##: Add notes if provided
            if notes is not None:
                query_builder.set(notes=notes)

            query, params = query_builder.build()
            result = db_manager.fetchone(f"{query} RETURNING match_id", params)

            if result:
                logger.info(f"Match created successfully with ID: {result[0]}")
                return result[0]

            logger.warning("Match creation did not return an ID.")
            return None
    except Exception as exc:
        logger.error(f"Failed to create match: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_match_by_id(match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a match by ID.

    Parameters
    ----------
    match_id : int
        ID of the match to retrieve

    Returns
    -------
    Optional[Dict[str, Any]]
        Match data as a dictionary, or None if not found
    """
    result = (
        SelectQueryBuilder("Matches")
        .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "notes")
        .where("match_id = %s", match_id)
        .execute(fetch_all=False)
    )
    if result:
        return {
            "match_id": result[0],
            "winner_team_id": result[1],
            "loser_team_id": result[2],
            "is_fanny": result[3],
            "played_at": result[4],
            "notes": result[5],
        }
    return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_team_id(
    team_id: int,
    limit: int = 100,
    offset: int = 0,
    is_fanny: bool = False,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Get all matches involving a specific team.

    Parameters
    ----------
    team_id : int
        ID of the team
    limit : int, optional
        Maximum number of matches to return (default: 100).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).
    is_fanny : bool, optional
        Whether to filter matches by fanny (10-0), by default False
    start_date : Optional[Union[datetime, str]], optional
        Start date to filter matches (inclusive), by default None
    end_date : Optional[Union[datetime, str]], optional
        End date to filter matches (inclusive), by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    try:
        # ##: Convert string dates to datetime objects.
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if end_date is not None:
            end_date = datetime.combine(end_date, datetime.max.time())

        # ##: Build the query using SelectQueryBuilder.
        query_builder = (
            SelectQueryBuilder("Teams_ELO_History eh")
            .select(
                "m.match_id",
                "m.winner_team_id",
                "m.loser_team_id",
                "m.is_fanny",
                "m.played_at",
                "m.notes",
                "eh.old_elo",
                "eh.new_elo",
                "eh.difference as elo_change",
            )
            .join("Matches m", "eh.match_id = m.match_id")
            .where("eh.team_id = %s", team_id)
            .order_by_clause("m.played_at DESC")
            .limit(limit)
            .offset(offset)
        )

        # ##: Add date range filtering if provided.
        if start_date is not None:
            query_builder.where("m.played_at >= %s", start_date)
        if end_date is not None:
            query_builder.where("m.played_at <= %s", end_date)
        if is_fanny:
            query_builder.where("m.is_fanny = %s", True)

        # ##: Execute the query and fetch results.
        matches = []
        with transaction() as db_manager:
            query, params = query_builder.build()
            results = db_manager.fetchall(query, params)

        for row in results:
            matches.append(
                {
                    "match_id": row[0],
                    "winner_team_id": row[1],
                    "loser_team_id": row[2],
                    "is_fanny": row[3],
                    "played_at": row[4],
                    "notes": row[5],
                    "won": row[1] == team_id,
                    "elo_changes": {
                        team_id: {
                            "old_elo": row[6],
                            "new_elo": row[7],
                            "difference": row[8],
                        }
                    },
                }
            )
        return matches
    except Exception as exc:
        logger.error(f"Failed to get matches for team ID {team_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_player_id(
    player_id: int,
    limit: int = 100,
    offset: int = 0,
    is_fanny: bool = False,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Get all matches involving a specific player with optional filtering and pagination.

    Parameters
    ----------
    player_id : int
        ID of the player
    limit : int, optional
        Maximum number of matches to return, by default 100
    offset : int, optional
        Number of matches to skip, by default 0
    is_fanny : bool, optional
        Whether to filter matches by fanny (10-0), by default False
    start_date : Optional[Union[datetime, str]], optional
        Start date to filter matches (inclusive), by default None
    end_date : Optional[Union[datetime, str]], optional
        End date to filter matches (inclusive), by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries including match details and player's ELO change
    """
    try:
        # ##: Convert string dates to datetime objects.
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if end_date is not None:
            end_date = datetime.combine(end_date, datetime.max.time())

        # ##: Build the query using SelectQueryBuilder.
        query_builder = (
            SelectQueryBuilder("Players_ELO_History eh")
            .select(
                "m.match_id",
                "m.winner_team_id",
                "m.loser_team_id",
                "m.is_fanny",
                "m.played_at",
                "m.notes",
                "eh.old_elo",
                "eh.new_elo",
                "eh.difference as elo_change",
            )
            .join("Matches m", "eh.match_id = m.match_id")
            .where("eh.player_id = %s", player_id)
            .order_by_clause("m.played_at DESC")
            .limit(limit)
            .offset(offset)
        )

        # ##: Add date range filtering if provided.
        if start_date is not None:
            query_builder.where("m.played_at >= %s", start_date)
        if end_date is not None:
            query_builder.where("m.played_at <= %s", end_date)
        if is_fanny:
            query_builder.where("m.is_fanny = %s", True)

        matches = []
        with transaction() as db_manager:
            query, params = query_builder.build()
            results = db_manager.fetchall(query, params)

            for row in results:
                matches.append(
                    {
                        "match_id": row[0],
                        "winner_team_id": row[1],
                        "loser_team_id": row[2],
                        "is_fanny": row[3],
                        "played_at": row[4],
                        "notes": row[5],
                        "elo_changes": {
                            player_id: {
                                "old_elo": row[6],
                                "new_elo": row[7],
                                "difference": row[8],
                            }
                        },
                    }
                )

        return matches

    except Exception as exc:
        logger.error(f"Failed to get matches for player {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_matches(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all matches with pagination support.

    Parameters
    ----------
    limit : int, optional
        Maximum number of matches to return, by default 100
    offset : int, optional
        Number of matches to skip, by default 0

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    try:
        rows = (
            SelectQueryBuilder("Matches")
            .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "notes")
            .order_by_clause("played_at DESC")
            .limit(limit)
            .offset(offset)
            .execute()
        )

        return (
            [
                {
                    "match_id": r[0],
                    "winner_team_id": r[1],
                    "loser_team_id": r[2],
                    "is_fanny": r[3],
                    "played_at": r[4],
                    "notes": r[5],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get all matches: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def delete_match_by_id(match_id: int) -> bool:
    """
    Delete a match from the database.

    Parameters
    ----------
    match_id : int
        ID of the match to delete

    Returns
    -------
    bool
        True if the deletion was successful, False otherwise
    """
    try:
        with transaction() as db_manager:
            query_builder = DeleteQueryBuilder("Matches")
            query_builder.where("match_id = %s", match_id)
            query, params = query_builder.build()

            result = bool(db_manager.fetchone(query, params)[0])
            if result:
                logger.info(f"Match ID {match_id} deleted successfully.")
            logger.warning(f"Attempted to delete non-existent Match ID {match_id}.")
            return result
    except Exception as exc:
        logger.error(f"Failed to delete match ID {match_id}: {exc}")
        return False
