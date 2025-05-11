# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

import logging
from typing import Any, Dict, List, Optional

from app.db import transaction, with_retry

from .builders import SelectQueryBuilder

logger = logging.getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def create_match(team1_id: int, team2_id: int, winner_team_id: int, match_date: str) -> Optional[int]:
    """
    Record a new match in the database.

    Parameters
    ----------
    team1_id : int
        ID of the first team
    team2_id : int
        ID of the second team
    winner_team_id : int
        ID of the winning team
    match_date : str
        Date and time of the match (ISO format)

    Returns
    -------
    Optional[int]
        ID of the newly created match, or None on failure
    """
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone(
                "INSERT INTO Matches (team1_id, team2_id, winner_team_id, match_date) VALUES (?, ?, ?, ?) RETURNING match_id",
                [team1_id, team2_id, winner_team_id, match_date],
            )
            if result:
                logger.info("Match created successfully with ID: %d", result[0])
                return result[0]

            logger.warning("Match creation did not return an ID.")
            return None
    except Exception as e:
        logger.error("Failed to create match: %s", e)
        return None


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
        .select("match_id", "team1_id", "team2_id", "winner_team_id", "match_date")
        .where("match_id = ?", match_id)
        .execute(fetch_all=False)
    )
    if result:
        return {
            "match_id": result[0],
            "team1_id": result[1],
            "team2_id": result[2],
            "winner_team_id": result[3],
            "match_date": result[4],
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
        .select("match_id", "team1_id", "team2_id", "winner_team_id", "match_date")
        .where("team1_id = ? OR team2_id = ?", team_id, team_id)
        .order_by_clause("match_date DESC")
        .execute()
    )
    return (
        [
            {
                "match_id": r[0],
                "team1_id": r[1],
                "team2_id": r[2],
                "winner_team_id": r[3],
                "match_date": r[4],
            }
            for r in rows
        ]
        if rows
        else []
    )


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
            result = db_manager.fetchone("DELETE FROM Matches WHERE match_id = ? RETURNING match_id", [match_id])
            if result:
                logger.info("Match ID %d deleted successfully.", match_id)
                return True
            logger.warning("Attempted to delete non-existent Match ID %d.", match_id)
            return False
    except Exception as e:
        logger.error("Failed to delete match ID %d: %s", match_id, e)
        return False


def get_all_matches_for_recalculation() -> List[Dict[str, Any]]:
    """
    Get all matches chronologically, including player IDs for winning and losing teams.

    Returns
    -------
    List[Dict[str, Any]]
        List of match data, each dictionary containing:
        'match_id', 'played_at', 'winner_p1_id', 'winner_p2_id',
        'loser_p1_id', 'loser_p2_id'.
    """
    try:
        query = (
            SelectQueryBuilder("Matches m")
            .select(
                "m.match_id",
                "m.played_at",
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
                "winner_p1_id": row[2],
                "winner_p2_id": row[3],
                "loser_p1_id": row[4],
                "loser_p2_id": row[5],
            }
            for row in rows
        ]
        logger.info(f"Successfully fetched {len(matches_data)} matches for ELO recalculation.")
        return matches_data

    except Exception as e:
        logger.error(f"Failed to get all matches for recalculation: {e}")
        return []
