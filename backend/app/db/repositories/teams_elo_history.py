# -*- coding: utf-8 -*-
"""
Operations related to Teams ELO history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.db.builders.insert import InsertQueryBuilder
from app.db.builders.select import SelectQueryBuilder
from app.db.session.retry import with_retry
from app.db.session.transaction import transaction


@with_retry(max_retries=3, retry_delay=0.5)
def record_team_elo_update(
    team_id: int,
    match_id: int,
    old_elo: int,
    new_elo: int,
    date: Optional[datetime] = None,
) -> Optional[int]:
    """
    Record a team's ELO score update after a match.

    Parameters
    ----------
    team_id : int
        ID of the team.
    match_id : int
        ID of the match.
    old_elo : int
        Previous ELO score before the match.
    new_elo : int
        New ELO score after the match.
    date : Optional[datetime], optional
        Date of the update, by default current time.

    Returns
    -------
    Optional[int]
        ID of the newly created ELO history record, or None on failure.
    """
    try:
        if date is None:
            date = datetime.now()

        difference = new_elo - old_elo
        builder = InsertQueryBuilder("Teams_ELO_History", returning_column="history_id").set(
            team_id=team_id,
            match_id=match_id,
            old_elo=old_elo,
            new_elo=new_elo,
            difference=difference,
            date=date,
        )
        history_id = builder.execute()
        if history_id is not None:
            logger.info(f"Recorded ELO update for team {team_id}: {old_elo} -> {new_elo} (diff: {difference:+d})")
            return history_id
            return None
    except Exception as exc:
        logger.error(f"Failed to record team ELO update: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_record_team_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Record multiple team ELO updates in a single transaction.

    Parameters
    ----------
    elo_updates : List[Dict[str, Any]]
        List of ELO update dictionaries, each with required keys:
        - 'team_id': int - ID of the team
        - 'match_id': int - ID of the match
        - 'old_elo': int - Previous ELO score
        - 'new_elo': int - New ELO score
        Optional keys:
        - 'date': datetime - Date of the update

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created ELO history records, or None for failures.
    """
    try:
        results = []
        for update in elo_updates:
            date = update.get("date", datetime.now())
            difference = update["new_elo"] - update["old_elo"]

            builder = InsertQueryBuilder("Teams_ELO_History", returning_column="history_id").set(
                team_id=update["team_id"],
                match_id=update["match_id"],
                old_elo=update["old_elo"],
                new_elo=update["new_elo"],
                difference=difference,
                date=date,
            )
            history_id = builder.execute()
            results.append(history_id)

        logger.info(
            f"Batch recorded {len(results)} team ELO updates, successful inserts: {sum(1 for r in results if r is not None)}"
        )
        return results
    except Exception as exc:
        logger.error(f"Failed to batch record team ELO updates: {exc}")
        return [None] * len(elo_updates)


@with_retry(max_retries=3, retry_delay=0.5)
def get_team_elo_history_by_id(
    team_id: int,
    limit: int = 100,
    offset: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Get the ELO history for a team with optional filtering.

    Parameters
    ----------
    team_id : int
        ID of the team.
    limit : int, optional
        Maximum number of records to return, by default 100.
    offset : int, optional
        Number of records to skip, by default 0.
    start_date : Optional[datetime], optional
        Filter by start date, by default None.
    end_date : Optional[datetime], optional
        Filter by end date, by default None.

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records.
    """
    try:
        with transaction() as db:
            query_builder = SelectQueryBuilder("Teams_ELO_History").select("*").where("team_id = ?", team_id)

            if start_date:
                query_builder.where("date >= ?", start_date)
            if end_date:
                query_builder.where("date <= ?", end_date)

            query_builder.order_by_clause("date DESC").limit(limit).offset(offset)

            query, params = query_builder.build()
            rows = db.fetchall(query, params)

            return [
                {
                    "history_id": row[0],
                    "team_id": row[1],
                    "match_id": row[2],
                    "old_elo": row[3],
                    "new_elo": row[4],
                    "difference": row[5],
                    "date": row[6],
                }
                for row in rows
            ]
    except Exception as exc:
        logger.error(f"Failed to get team ELO history: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_team_elo_history_by_match_id(team_id: int, match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the ELO history record for a specific team and match combination.

    Parameters
    ----------
    team_id : int
        ID of the team.
    match_id : int
        ID of the match.

    Returns
    -------
    Optional[Dict[str, Any]]
        ELO history record if found, None otherwise.
    """
    try:
        with transaction() as db:
            query, params = (
                SelectQueryBuilder("Teams_ELO_History")
                .select("*")
                .where("team_id = ?", team_id)
                .where("match_id = ?", match_id)
                .build()
            )

            row = db.fetchone(query, params)
            if row:
                return {
                    "history_id": row[0],
                    "team_id": row[1],
                    "match_id": row[2],
                    "old_elo": row[3],
                    "new_elo": row[4],
                    "difference": row[5],
                    "date": row[6],
                }
            return None
    except Exception as exc:
        logger.error(f"Failed to get team ELO history by team and match: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_teams_elo_history_by_match_id(match_id: int) -> List[Dict[str, Any]]:
    """
    Get all team ELO history records for a specific match.

    Parameters
    ----------
    match_id : int
        ID of the match.

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records for the match.
    """
    try:
        with transaction() as db:
            query, params = (
                SelectQueryBuilder("Teams_ELO_History")
                .select("*")
                .where("match_id = ?", match_id)
                .order_by_clause("history_id ASC")
                .build()
            )

            rows = db.fetchall(query, params)
            return [
                {
                    "history_id": row[0],
                    "team_id": row[1],
                    "match_id": row[2],
                    "old_elo": row[3],
                    "new_elo": row[4],
                    "difference": row[5],
                    "date": row[6],
                }
                for row in rows
            ]
    except Exception as exc:
        logger.error(f"Failed to get team ELO history by match: {exc}")
        return []
