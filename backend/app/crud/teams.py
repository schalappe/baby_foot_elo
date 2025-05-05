# -*- coding: utf-8 -*-
"""
Operations related to the Teams table.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry

logger = getLogger(__name__)


@with_retry()
def create_team(team_name: str, player1_id: int, player2_id: int) -> Optional[int]:
    """
    Create a new team in the database.

    Parameters
    ----------
    team_name : str
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
            logger.warning(f"Team with players {player1_id} and {player2_id} already exists.")
            return None

        db.execute(
            "INSERT INTO Teams (team_name, player1_id, player2_id) VALUES (?, ?, ?)",
            [team_name, player1_id, player2_id],
        )
        result = db.fetchone("SELECT last_insert_rowid()")
        return result[0] if result else None


@with_retry()
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
    result = db.fetchone("SELECT team_id, team_name, player1_id, player2_id FROM Teams WHERE team_id = ?", [team_id])
    if result:
        return {"team_id": result[0], "team_name": result[1], "player1_id": result[2], "player2_id": result[3]}
    return None


@with_retry()
def get_all_teams() -> List[Dict[str, Any]]:
    """
    Get all teams from the database.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries
    """
    db = DatabaseManager()
    results = db.fetchall("SELECT team_id, team_name, player1_id, player2_id FROM Teams ORDER BY team_name")
    return [{"team_id": row[0], "team_name": row[1], "player1_id": row[2], "player2_id": row[3]} for row in results]


@with_retry()
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
        True if the deletion was successful, False otherwise
    """
    with transaction() as db:
        db.execute("DELETE FROM Teams WHERE team_id = ?", [team_id])
        return db.rowcount > 0


@with_retry()
def batch_insert_teams(teams: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Insert multiple teams in a single transaction.

    Parameters
    ----------
    teams : List[Dict[str, Any]]
        List of team dictionaries, each with 'team_name', 'player1_id', 'player2_id' keys

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created teams, or None for failures
    """
    team_ids = []
    with transaction() as db:
        for team in teams:
            # ##: Consider adding the same check as in create_team here.
            db.execute(
                "INSERT INTO Teams (team_name, player1_id, player2_id) VALUES (?, ?, ?)",
                [team["team_name"], team["player1_id"], team["player2_id"]],
            )
            result = db.fetchone("SELECT last_insert_rowid()")
            team_ids.append(result[0] if result else None)

    return team_ids
