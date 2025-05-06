# -*- coding: utf-8 -*-
"""
Operations related to the Teams table.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry

logger = getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def create_team(name: str, player1_id: int, player2_id: int) -> Optional[int]:
    """
    Create a new team in the database.

    Parameters
    ----------
    name : str
        Name of the team
    player1_id : int
        ID of the first player
    player2_id : int
        ID of the second player

    Returns
    -------
    Optional[int]
        ID of the newly created team, or None on failure
    """
    with transaction() as db:
        # ##: Check if team with the same players already exists (regardless of order).
        existing_team = db.fetchone(
            """SELECT team_id FROM Teams 
               WHERE (player1_id = ? AND player2_id = ?) OR (player1_id = ? AND player2_id = ?)""",
            [player1_id, player2_id, player2_id, player1_id],
        )
        if existing_team:
            logger.warning(
                "Attempted to create duplicate team for players %d and %d",
                player1_id,
                player2_id,
            )
            return None

        # ##: Use RETURNING clause for consistency and reliability across DBs.
        query = "INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?) RETURNING team_id"
        result = db.fetchone(query, [player1_id, player2_id])
        
        if result and result[0]:
            logger.info(f"Created team '{name}' with ID: {result[0]}")
            return result[0]
        else:
            logger.error(f"Failed to create team '{name}' or retrieve its ID.")
            return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_team(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a team by ID.

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve

    Returns
    -------
    Optional[Dict[str, Any]]
        Team data as a dictionary, or None if not found
    """
    db = DatabaseManager()
    result = db.fetchone("SELECT team_id, player1_id, player2_id FROM Teams WHERE team_id = ?", [team_id])
    if result:
        return {"team_id": result[0], "player1_id": result[1], "player2_id": result[2]}
    return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_teams() -> List[Dict[str, Any]]:
    """
    Get all teams from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries.
    """
    db = DatabaseManager()
    results = db.fetchall("SELECT team_id, player1_id, player2_id FROM Teams ORDER BY player1_id")
    return [{"team_id": row[0], "player1_id": row[1], "player2_id": row[2]} for row in results]


@with_retry(max_retries=3, retry_delay=0.5)
def delete_team(team_id: int) -> bool:
    """
    Delete a team from the database.

    Parameters
    ----------
    team_id : int
        ID of the team to delete

    Returns
    -------
    bool
        True if the deletion was successful, False otherwise.
    """
    with transaction() as db:
        db.execute("DELETE FROM Teams WHERE team_id = ?", [team_id])
        return db.rowcount > 0


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_teams(teams: List[Dict[str, Any]]) -> List[Optional[int]]:
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
    with transaction() as db:
        for team in teams:
            # ##: Ensure players are ordered consistently.
            p1_id = team["player1_id"]
            p2_id = team["player2_id"]
            if p1_id > p2_id:
                p1_id, p2_id = p2_id, p1_id
            
            # ##: Consider adding the same check as in create_team here.
            query = "INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?) RETURNING team_id"
            result = db.fetchone(query, [p1_id, p2_id])
            
            team_ids.append(result[0] if result else None)

    return team_ids
