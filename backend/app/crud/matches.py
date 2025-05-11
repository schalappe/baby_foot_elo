# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.db import transaction, with_retry

from .builders import DeleteQueryBuilder, InsertQueryBuilder, SelectQueryBuilder


@with_retry(max_retries=3, retry_delay=0.5)
def create_match(
    winner_team_id: int, loser_team_id: int, played_at: Union[datetime, str], is_fanny: bool = False
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

    Returns
    -------
    Optional[int]
        ID of the newly created match, or None on failure
    """
    try:
        # ##: Convert string to datetime if necessary.
        if isinstance(played_at, str):
            played_at = datetime.fromisoformat(played_at)

        # ##: Extract date components.
        year = played_at.year
        month = played_at.month
        day = played_at.day

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
                year=year,
                month=month,
                day=day,
            )

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
def delete_match(match_id: int) -> bool:
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
            query_builder.where("match_id = ?", match_id)
            query, params = query_builder.build()

            result = bool(db_manager.fetchone(query, params)[0])
            if result:
                logger.info(f"Match ID {match_id} deleted successfully.")
            logger.warning(f"Attempted to delete non-existent Match ID {match_id}.")
            return result
    except Exception as exc:
        logger.error(f"Failed to delete match ID {match_id}: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def get_match(match_id: int) -> Optional[Dict[str, Any]]:
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
        .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "year", "month", "day")
        .where("match_id = ?", match_id)
        .execute(fetch_all=False)
    )
    if result:
        return {
            "match_id": result[0],
            "winner_team_id": result[1],
            "loser_team_id": result[2],
            "is_fanny": result[3],
            "played_at": result[4],
            "year": result[5],
            "month": result[6],
            "day": result[7],
        }
    return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_team(team_id: int) -> List[Dict[str, Any]]:
    """
    Get all matches involving a specific team.

    Parameters
    ----------
    team_id : int
        ID of the team

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    rows = (
        SelectQueryBuilder("Matches")
        .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "year", "month", "day")
        .where("winner_team_id = ? OR loser_team_id = ?", team_id, team_id)
        .order_by_clause("played_at DESC")
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
                "year": r[5],
                "month": r[6],
                "day": r[7],
                "won": r[1] == team_id,
            }
            for r in rows
        ]
        if rows
        else []
    )


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_matches_for_recalculation() -> List[Dict[str, Any]]:
    """
    Get all matches chronologically, including player IDs for winning and losing teams.

    Returns
    -------
    List[Dict[str, Any]]
        List of match data, each dictionary containing:
        'match_id', 'played_at', 'winner_p1_id', 'winner_p2_id',
        'loser_p1_id', 'loser_p2_id', 'is_fanny'.
    """
    try:
        query = (
            SelectQueryBuilder("Matches m")
            .select(
                "m.match_id",
                "m.played_at",
                "m.is_fanny",
                "wt.player1_id AS winner_p1_id",
                "wt.player2_id AS winner_p2_id",
                "lt.player1_id AS loser_p1_id",
                "lt.player2_id AS loser_p2_id",
            )
            .join("Teams wt ON m.winner_team_id = wt.team_id")
            .join("Teams lt ON m.loser_team_id = lt.team_id")
            .order_by_clause("m.played_at ASC")
        )
        rows = query.execute()

        if not rows:
            logger.info("No matches found for recalculation.")
            return []

        matches_data = [
            {
                "match_id": row[0],
                "played_at": row[1],
                "is_fanny": row[2],
                "winner_p1_id": row[3],
                "winner_p2_id": row[4],
                "loser_p1_id": row[5],
                "loser_p2_id": row[6],
            }
            for row in rows
        ]
        logger.info(f"Successfully fetched {len(matches_data)} matches for ELO recalculation.")
        return matches_data

    except Exception as exc:
        logger.error(f"Failed to get all matches for recalculation: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_date_range(
    start_date: Union[datetime, str], end_date: Union[datetime, str]
) -> List[Dict[str, Any]]:
    """
    Get all matches within a specific date range.

    Parameters
    ----------
    start_date : Union[datetime, str]
        Start date of the range (inclusive)
    end_date : Union[datetime, str]
        End date of the range (inclusive)

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    # ##: Convert string dates to datetime if necessary.
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    try:
        rows = (
            SelectQueryBuilder("Matches")
            .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "year", "month", "day")
            .where("played_at >= ? AND played_at <= ?", start_date, end_date)
            .order_by_clause("played_at ASC")
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
                    "year": r[5],
                    "month": r[6],
                    "day": r[7],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get matches by date range: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_fanny_matches() -> List[Dict[str, Any]]:
    """
    Get all matches that were fannies (10-0).

    Returns
    -------
    List[Dict[str, Any]]
        List of fanny match dictionaries
    """

    try:
        rows = (
            SelectQueryBuilder("Matches")
            .select("match_id", "winner_team_id", "loser_team_id", "played_at", "year", "month", "day")
            .where("is_fanny = ?", True)
            .order_by_clause("played_at DESC")
            .execute()
        )

        return (
            [
                {
                    "match_id": r[0],
                    "winner_team_id": r[1],
                    "loser_team_id": r[2],
                    "played_at": r[3],
                    "year": r[4],
                    "month": r[5],
                    "day": r[6],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get fanny matches: {exc}")
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
            .select("match_id", "winner_team_id", "loser_team_id", "is_fanny", "played_at", "year", "month", "day")
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
                    "year": r[5],
                    "month": r[6],
                    "day": r[7],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as exc:
        logger.error(f"Failed to get all matches: {exc}")
        return []
