# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry


@with_retry()
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
    with transaction() as db:
        db.execute(
            "INSERT INTO Matches (team1_id, team2_id, winner_team_id, match_date) VALUES (?, ?, ?, ?)",
            [team1_id, team2_id, winner_team_id, match_date],
        )
        result = db.fetchone("SELECT last_insert_rowid()")
        return result[0] if result else None


@with_retry()
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
    db = DatabaseManager()
    result = db.fetchone(
        "SELECT match_id, team1_id, team2_id, winner_team_id, match_date FROM Matches WHERE match_id = ?", [match_id]
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


@with_retry()
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
    db = DatabaseManager()
    results = db.fetchall(
        """
        SELECT match_id, team1_id, team2_id, winner_team_id, match_date 
        FROM Matches 
        WHERE team1_id = ? OR team2_id = ?
        ORDER BY match_date DESC
        """,
        [team_id, team_id],
    )
    return [
        {"match_id": row[0], "team1_id": row[1], "team2_id": row[2], "winner_team_id": row[3], "match_date": row[4]}
        for row in results
    ]


@with_retry()
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
    with transaction() as db:
        db.execute("DELETE FROM Matches WHERE match_id = ?", [match_id])
        return db.rowcount > 0
