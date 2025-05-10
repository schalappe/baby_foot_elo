# -*- coding: utf-8 -*-
"""
Database initialization logic extracted from DatabaseManager.
"""

from pathlib import Path
from sys import stderr

from loguru import logger

from app import schema
from app.core import config
from app.db.database import DatabaseManager

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
    schema.CREATE_INDEX_MATCHES_WINNER_TEAM_ID,
    schema.CREATE_INDEX_MATCHES_LOSER_TEAM_ID,
    schema.CREATE_INDEX_MATCHES_PLAYED_AT,
    schema.CREATE_INDEX_ELOHIST_PLAYER_ID,
    schema.CREATE_INDEX_ELOHIST_MATCH_ID,
    schema.CREATE_INDEX_ELOHIST_DATE,
    schema.CREATE_INDEX_PERIODIC_RANKINGS_PLAYER_ID,
    schema.CREATE_INDEX_PERIODIC_RANKINGS_PERIOD,
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
