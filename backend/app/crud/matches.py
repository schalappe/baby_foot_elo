# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

import logging
from typing import Any, Dict, List, Optional

from app.db import transaction, with_retry

logger = logging.getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def create_match(
    team1_id: int, team2_id: int, winner_team_id: int, match_date: str
) -> Optional[int]:
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
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone(
                "SELECT match_id, team1_id, team2_id, winner_team_id, match_date FROM Matches WHERE match_id = ?",
                [match_id],
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
    except Exception as e:
        logger.error("Failed to get match by ID %d: %s", match_id, e)
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
    try:
        with transaction() as db_manager:
            results = db_manager.fetchall(
                """
                SELECT match_id, team1_id, team2_id, winner_team_id, match_date 
                FROM Matches 
                WHERE team1_id = ? OR team2_id = ?
                ORDER BY match_date DESC
                """,
                [team_id, team_id],
            )
            if results:
                return [
                    {
                        "match_id": row[0],
                        "team1_id": row[1],
                        "team2_id": row[2],
                        "winner_team_id": row[3],
                        "match_date": row[4],
                    }
                    for row in results
                ]
            return []
    except Exception as e:
        logger.error("Failed to get matches by team ID %d: %s", team_id, e)
        return []


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
            result = db_manager.fetchone(
                "DELETE FROM Matches WHERE match_id = ? RETURNING match_id", [match_id]
            )
            if result:
                logger.info("Match ID %d deleted successfully.", match_id)
                return True
            logger.warning("Attempted to delete non-existent Match ID %d.", match_id)
            return False
    except Exception as e:
        logger.error("Failed to delete match ID %d: %s", match_id, e)
        return False
