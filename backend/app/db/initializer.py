# -*- coding: utf-8 -*-
"""
Database initialization logic extracted from DatabaseManager.
"""

from logging import getLogger

from app import schema

from .database import DatabaseManager

logger = getLogger(__name__)

# ##: Constants for database initialization.
SEQUENCES = [
    schema.CREATE_SEQ_PLAYERS,
    schema.CREATE_SEQ_TEAMS,
    schema.CREATE_SEQ_MATCHES,
    schema.CREATE_SEQ_ELO_HISTORY,
    schema.CREATE_SEQ_PERIODIC_RANKINGS,
    schema.CREATE_SEQ_TEAM_PERIODIC_RANKINGS,
]

TABLES = [
    schema.CREATE_PLAYERS_TABLE,
    schema.CREATE_TEAMS_TABLE,
    schema.CREATE_MATCHES_TABLE,
    schema.CREATE_ELO_HISTORY_TABLE,
    schema.CREATE_PERIODIC_RANKINGS_TABLE,
    schema.CREATE_TEAM_PERIODIC_RANKINGS_TABLE,
]

INDEXES = [
    schema.CREATE_INDEX_PLAYERS_NAME,
    schema.CREATE_INDEX_MATCHES_TEAM1,
    schema.CREATE_INDEX_MATCHES_TEAM2,
    schema.CREATE_INDEX_MATCHES_WINNER,
    schema.CREATE_INDEX_ELOHIST_PLAYER,
    schema.CREATE_INDEX_ELOHIST_MATCH,
    schema.CREATE_INDEX_PERIODIC_PLAYER,
    schema.CREATE_INDEX_PERIODIC_PERIOD_PLAYER,
    schema.CREATE_INDEX_MATCHES_DATE,
    schema.CREATE_INDEX_ELOHIST_UPDATED,
]


def create_sequences(db_manager: DatabaseManager):
    """
    Create all database sequences.

    Parameters
    ----------
    db_manager : DatabaseManager
        The database manager to use for executing the SQL statements.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements.
    """
    for sql in SEQUENCES:
        try:
            db_manager.execute(sql)
            logger.info("Executed sequence statement: %s", sql.splitlines()[0])
        except Exception as exc:
            logger.error("Error executing sequence statement: %s\nSQL: %s", exc, sql)
            raise


def create_tables(db_manager: DatabaseManager):
    """
    Create all database tables.

    Parameters
    ----------
    db_manager : DatabaseManager
        The database manager to use for executing the SQL statements.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements.
    """
    for sql in TABLES:
        try:
            db_manager.execute(sql)
            logger.info("Executed table statement: %s", sql.splitlines()[0])
        except Exception as exc:
            logger.error("Error executing table statement: %s\nSQL: %s", exc, sql)
            raise


def create_indexes_for_optimization(db_manager: DatabaseManager):
    """
    Create all indexes needed for optimal query performance.

    Parameters
    ----------
    db_manager : DatabaseManager
        The database manager to use for executing the SQL statements.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements.
    """
    for idx_sql in INDEXES:
        try:
            db_manager.execute(idx_sql)
            logger.info("Executed index statement: %s", idx_sql.splitlines()[0])
        except Exception as exc:
            logger.error("Error executing index statement: %s\nSQL: %s", exc, idx_sql)
            raise


def initialize_database(db_manager: DatabaseManager):
    """
    Initialize the database: create sequences and tables if they do not exist.

    Parameters
    ----------
    db_manager : DatabaseManager
        The database manager to use for executing the SQL statements.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements.
    """
    create_sequences(db_manager)
    create_tables(db_manager)

    # ##: Create indexes for performance optimization.
    create_indexes_for_optimization(db_manager)
    logger.info("Database initialization complete. All tables and indexes ensured.")
