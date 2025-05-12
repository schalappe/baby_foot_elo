# -*- coding: utf-8 -*-
"""
Operations related to ELO history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.db import transaction, with_retry

from app.crud.builders import InsertQueryBuilder, SelectQueryBuilder


@with_retry(max_retries=3, retry_delay=0.5)
def record_elo_update(
    player_id: int,
    match_id: int,
    old_elo: int,
    new_elo: int,
    date: Optional[datetime] = None,
) -> Optional[int]:
    """
    Record an ELO score update after a match.

    Parameters
    ----------
    player_id : int
        ID of the player
    match_id : int
        ID of the match
    old_elo : int
        Previous ELO score before the match
    new_elo : int
        New ELO score after the match
    date : Optional[datetime], optional
        Date of the update, by default current time

    Returns
    -------
    Optional[int]
        ID of the newly created ELO history record, or None on failure
    """
    try:
        if date is None:
            date = datetime.now()

        with transaction() as db:
            query, params = (
                InsertQueryBuilder("ELO_History")
                .set(
                    player_id=player_id,
                    match_id=match_id,
                    old_elo=old_elo,
                    new_elo=new_elo,
                    difference=new_elo - old_elo,
                    date=date,
                    year=date.year,
                    month=date.month,
                    day=date.day,
                )
                .build()
            )

            result = db.fetchone(f"{query} RETURNING history_id", params)

            if result and result[0]:
                return result[0]
            return None
    except Exception as e:
        logger.error(f"Failed to record ELO update: {e}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_record_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Record multiple ELO updates in a single transaction.

    Parameters
    ----------
    elo_updates : List[Dict[str, Any]]
        List of ELO update dictionaries, each with required keys:
        - 'player_id': int - ID of the player
        - 'match_id': int - ID of the match
        - 'old_elo': int - Previous ELO score
        - 'new_elo': int - New ELO score
        Optional keys:
        - 'date': datetime - Date of the update

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created ELO history records, or None for failures
    """
    if not elo_updates:
        return []

    history_ids = []
    try:
        with transaction() as db:
            for update in elo_updates:
                # ##: Get date from update or use current time.
                date = update.get("date", datetime.now())
                year = date.year
                month = date.month
                day = date.day

                query, params = (
                    InsertQueryBuilder("ELO_History")
                    .set(
                        player_id=update["player_id"],
                        match_id=update["match_id"],
                        old_elo=update["old_elo"],
                        new_elo=update["new_elo"],
                        difference=update["new_elo"] - update["old_elo"],
                        date=date,
                        year=year,
                        month=month,
                        day=day,
                    )
                    .build()
                )

                result = db.fetchone(f"{query} RETURNING history_id", params)
                if result and result[0] is not None:
                    history_ids.append(result[0])

        return history_ids
    except Exception as e:
        logger.error(f"Failed to batch record ELO updates: {e}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_elo_history(
    player_id: int,
    limit: int = 100,
    offset: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Get the ELO history for a player with optional filtering.

    Parameters
    ----------
    player_id : int
        ID of the player
    limit : int, optional
        Maximum number of records to return, by default 100
    offset : int, optional
        Number of records to skip, by default 0
    start_date : Optional[datetime], optional
        Filter by start date, by default None
    end_date : Optional[datetime], optional
        Filter by end date, by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records
    """
    try:
        builder = SelectQueryBuilder("ELO_History").select("*").where("player_id = ?", player_id)

        if start_date:
            builder = builder.where("date >= ?", start_date)

        if end_date:
            builder = builder.where("date <= ?", end_date)

        results = builder.order_by_clause("date DESC").limit(limit).offset(offset).execute(fetch_all=True)

        if not results:
            return []

        history_records = []
        for record in results:
            history_records.append(
                {
                    "history_id": record[0],
                    "player_id": record[1],
                    "match_id": record[2],
                    "old_elo": record[3],
                    "new_elo": record[4],
                    "difference": record[5],
                    "date": record[6],
                    "year": record[7],
                    "month": record[8],
                    "day": record[9],
                }
            )

        return history_records
    except Exception as e:
        logger.error(f"Failed to get ELO history for player ID {player_id}: {e}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_elo_by_date(player_id: int, target_date: datetime) -> Optional[int]:
    """
    Get the ELO score for a player at a specific date.

    Parameters
    ----------
    player_id : int
        ID of the player
    target_date : datetime
        The date to get the ELO score for

    Returns
    -------
    Optional[int]
        ELO score at the specified date, or None if no record exists
    """
    try:
        result = (
            SelectQueryBuilder("ELO_History")
            .select("new_elo")
            .where("player_id = ?", player_id)
            .where("date <= ?", target_date)
            .order_by_clause("date DESC")
            .limit(1)
            .execute(fetch_all=False)
        )
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Failed to get ELO by date for player ID {player_id}: {e}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_monthly_elo_history(player_id: int, year: int, month: int) -> List[Dict[str, Any]]:
    """
    Get the monthly ELO history for a player for a specific year and month.

    Parameters
    ----------
    player_id : int
        ID of the player
    year : int
        Year to filter by
    month : int
        Month to filter by

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records for the specified month
    """
    try:
        results = (
            SelectQueryBuilder("ELO_History")
            .select("*")
            .where("player_id = ?", player_id)
            .where("year = ?", year)
            .where("month = ?", month)
            .order_by_clause("date ASC")
            .execute(fetch_all=True)
        )

        if not results:
            return []

        history_records = []
        for record in results:
            history_records.append(
                {
                    "history_id": record[0],
                    "player_id": record[1],
                    "match_id": record[2],
                    "old_elo": record[3],
                    "new_elo": record[4],
                    "difference": record[5],
                    "date": record[6],
                    "year": record[7],
                    "month": record[8],
                    "day": record[9],
                }
            )

        return history_records
    except Exception as e:
        logger.error(f"Failed to get monthly ELO history for player ID {player_id}: {e}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_elo_history_by_match(match_id: int) -> List[Dict[str, Any]]:
    """
    Get all ELO history records for a specific match.

    Parameters
    ----------
    match_id : int
        ID of the match

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records for the match
    """
    try:
        results = SelectQueryBuilder("ELO_History").select("*").where("match_id = ?", match_id).execute(fetch_all=True)

        if not results:
            return []

        history_records = []
        for record in results:
            history_records.append(
                {
                    "history_id": record[0],
                    "player_id": record[1],
                    "match_id": record[2],
                    "old_elo": record[3],
                    "new_elo": record[4],
                    "difference": record[5],
                    "date": record[6],
                    "year": record[7],
                    "month": record[8],
                    "day": record[9],
                }
            )
        return history_records
    except Exception as e:
        logger.error(f"Failed to get ELO history for match {match_id}: {e}")
        return []
