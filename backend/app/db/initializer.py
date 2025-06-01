# -*- coding: utf-8 -*-
"""
Database initialization logic extracted from DatabaseManager.
"""

from pathlib import Path
from sys import stderr

from loguru import logger

from app.core import config
from app.db.database import DatabaseManager
from app.db.schemas import (
    matches,
    players,
    players_elo_history,
    teams,
    teams_elo_history,
)

# ##: Constants for database initialization.
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
    """Main function to initialize the database."""

    # ##: Configure Loguru logger.
    logger.remove()
    logger.add(
        stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}", level="INFO"
    )

    db_url = config.get_db_url()
    logger.info(f"Using database URL from config: {db_url}")

    # ##: Extract path from URL like duckdb:///path/to/file.duckdb
    if db_url.startswith("duckdb:///"):
        db_path_str = db_url[len("duckdb:///") :]
    elif db_url.startswith("duckdb://:memory:"):
        logger.info("Using in-memory database. No persistent file will be created.")
        db_path_str = ":memory:"
    else:
        logger.error(f"Unsupported DB_URL format: {db_url}")
        return

    db_manager = None
    try:
        if db_path_str != ":memory:":
            db_file_path = Path(db_path_str)
            db_dir = db_file_path.parent
            logger.info(f"Target database file: {db_file_path}")
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured database directory exists: {db_dir}")
            except OSError as e:
                logger.error(f"Error creating database directory {db_dir}: {e}")
                return
            db_manager = DatabaseManager(db_path=str(db_file_path))
        else:
            db_manager = DatabaseManager(db_path=":memory:")

        logger.info(f"Initializing DatabaseManager with path: {db_path_str}")
        initialize_database(db_manager)
        logger.info("Database initialization process completed successfully.")
    except Exception as e:
        logger.exception("An error occurred during database initialization")
        raise
    finally:
        if db_manager:
            logger.info("Closing database connection.")
            db_manager.close()


if __name__ == "__main__":
    main()
