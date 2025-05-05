# -*- coding: utf-8 -*-
"""
Batch database operations for performance.
"""

from typing import Any, Dict, List, Optional

from app.db import transaction, with_retry


@with_retry()
def batch_insert_players(players: List[Dict[str, str]]) -> List[Optional[int]]:
    """
    Insert multiple players in a single transaction.

    Parameters
    ----------
    players : List[Dict[str, str]]
        List of player dictionaries, each with a 'name' key

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created players, or None for failures
    """
    player_ids = []
    with transaction() as db:
        for player in players:
            db.execute("INSERT INTO Players (name) VALUES (?)", [player["name"]])
            result = db.fetchone("SELECT last_insert_rowid()")
            player_ids.append(result[0] if result else None)

    return player_ids


@with_retry()
def batch_insert_teams(teams: List[Dict[str, str]]) -> List[Optional[int]]:
    """
    Insert multiple teams in a single transaction.

    Parameters
    ----------
    teams : List[Dict[str, str]]
        List of team dictionaries, each with a 'name' key

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created teams, or None for failures
    """
    team_ids = []
    with transaction() as db:
        for team in teams:
            db.execute("INSERT INTO Teams (name) VALUES (?)", [team["name"]])
            result = db.fetchone("SELECT last_insert_rowid()")
            team_ids.append(result[0] if result else None)

    return team_ids


@with_retry()
def batch_record_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Record multiple ELO updates in a single transaction.

    Parameters
    ----------
    elo_updates : List[Dict[str, Any]]
        List of ELO update dictionaries, each with 'player_id', 'match_id', and 'elo_score' keys

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created ELO history records, or None for failures
    """
    history_ids = []
    with transaction() as db:
        for update in elo_updates:
            db.execute(
                "INSERT INTO ELO_History (player_id, match_id, elo_score) VALUES (?, ?, ?)",
                [update["player_id"], update["match_id"], update["elo_score"]],
            )
            result = db.fetchone("SELECT last_insert_rowid()")
            history_ids.append(result[0] if result else None)

    return history_ids
