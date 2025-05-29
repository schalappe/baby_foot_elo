# -*- coding: utf-8 -*-
"""
Database initialization logic extracted from DatabaseManager.
"""

from pathlib import Path
from sys import stderr

from loguru import logger

from app.core import config
from app.db.database import DatabaseManager
from app.schemas import matches, players, players_elo_history, teams, teams_elo_history

# ##: Constants for database initialization.
SEQUENCES = [
    players.CREATE_SEQ_PLAYERS,
    teams.CREATE_SEQ_TEAMS,
    matches.CREATE_SEQ_MATCHES,
    players_elo_history.CREATE_SEQ_PLAYERS_ELO_HISTORY,
    teams_elo_history.CREATE_SEQ_TEAMS_ELO_HISTORY,
]

TABLES = [
    players.CREATE_PLAYERS_TABLE,
    teams.CREATE_TEAMS_TABLE,
    matches.CREATE_MATCHES_TABLE,
    players_elo_history.CREATE_PLAYERS_ELO_HISTORY_TABLE,
    teams_elo_history.CREATE_TEAMS_ELO_HISTORY_TABLE,
]

INDEXES = [
    players.CREATE_INDEX_PLAYERS_NAME,
    teams.CREATE_INDEX_TEAMS_PLAYER1_ID,
    teams.CREATE_INDEX_TEAMS_PLAYER2_ID,
    teams.CREATE_INDEX_TEAMS_PLAYER_PAIR_ORDER_INSENSITIVE,
    matches.CREATE_INDEX_MATCHES_WINNER_TEAM_ID,
    matches.CREATE_INDEX_MATCHES_LOSER_TEAM_ID,
    matches.CREATE_INDEX_MATCHES_PLAYED_AT,
    players_elo_history.CREATE_INDEX_PLAYERS_ELOHIST_PLAYER_ID,
    players_elo_history.CREATE_INDEX_PLAYERS_ELOHIST_MATCH_ID,
    players_elo_history.CREATE_INDEX_PLAYERS_ELOHIST_DATE,
    teams_elo_history.CREATE_INDEX_TEAMS_ELOHIST_TEAM_ID,
    teams_elo_history.CREATE_INDEX_TEAMS_ELOHIST_MATCH_ID,
    teams_elo_history.CREATE_INDEX_TEAMS_ELOHIST_DATE,
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
            logger.info(f"Executed sequence statement: {sql.splitlines()[0]}")
        except Exception as exc:
            logger.error(f"Error executing sequence statement: {exc}\nSQL: {sql}")
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
            logger.info(f"Executed table statement: {sql.splitlines()[0]}")
        except Exception as exc:
            logger.error(f"Error executing table statement: {exc}\nSQL: {sql}")
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
            logger.info(f"Executed index statement: {idx_sql.splitlines()[0]}")
        except Exception as exc:
            logger.error(f"Error executing index statement: {exc}\nSQL: {idx_sql}")
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


def main():
    """Main function to initialize the database for PostgreSQL."""

    # ##: Configure Loguru logger.
    logger.remove()
    logger.add(
        stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}", level="INFO"
    )

    db_url = config.get_db_url()
    logger.info(f"Attempting to initialize database using URL: {db_url}")

    db_manager = None
    try:
        db_manager = DatabaseManager()
        logger.info("DatabaseManager initialized for PostgreSQL.")

        initialize_database(db_manager)
        logger.info("Database schema initialization process completed successfully for PostgreSQL.")
    except Exception as e:
        logger.exception("An error occurred during PostgreSQL database schema initialization")
        raise
    finally:
        if db_manager:
            logger.info("Closing database connection.")
            db_manager.close()


if __name__ == "__main__":
    main()
