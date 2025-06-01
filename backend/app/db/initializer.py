# -*- coding: utf-8 -*-
"""
Database initialization logic extracted from DatabaseManager.
"""

from loguru import logger
from postgrest.exceptions import APIError
from supabase import Client

from app.core import config
from app.db.database import supabase
from app.db.schemas import (
    matches,
    players,
    players_elo_history,
    teams,
    teams_elo_history,
)

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


def create_tables(client: Client):
    """
    Create all database tables using Supabase RPC.

    Parameters
    ----------
    client : Client
        The Supabase client instance.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements via RPC.
    """
    for sql_statement in TABLES:
        try:
            client.rpc("execute_ddl_statement", {"sql_query": sql_statement}).execute()
            logger.info(f"Executed table statement via RPC: {sql_statement.splitlines()[0]}")
        except APIError as api_exc:
            logger.error(
                f"Error executing table statement via RPC (APIError): {api_exc.message}\nSQL: {sql_statement}"
            )
            raise Exception(f"RPC APIError for SQL: {sql_statement.splitlines()[0]} - {api_exc.message}") from api_exc
        except Exception as exc:
            logger.error(f"Error executing table statement via RPC (General Exception): {exc}\nSQL: {sql_statement}")
            raise


def create_indexes_for_optimization(client: Client):
    """
    Create all indexes needed for optimal query performance using Supabase RPC.

    Parameters
    ----------
    client : Client
        The Supabase client instance.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements via RPC.
    """
    for idx_sql_statement in INDEXES:
        try:
            client.rpc("execute_ddl_statement", {"sql_query": idx_sql_statement}).execute()
            logger.info(f"Executed index statement via RPC: {idx_sql_statement.splitlines()[0]}")
        except APIError as api_exc:
            logger.error(
                f"Error executing index statement via RPC (APIError): {api_exc.message}\nSQL: {idx_sql_statement}"
            )
            raise Exception(
                f"RPC APIError for SQL: {idx_sql_statement.splitlines()[0]} - {api_exc.message}"
            ) from api_exc
        except Exception as exc:
            logger.error(
                f"Error executing index statement via RPC (General Exception): {exc}\nSQL: {idx_sql_statement}"
            )
            raise


def initialize_database(client: Client):
    """
    Initialize the database: create tables and indexes if they do not exist using Supabase RPC.

    Parameters
    ----------
    client : Client
        The Supabase client instance.

    Raises
    ------
    Exception
        If an error occurs while executing the SQL statements via RPC.
    """
    # ##: Create tables.
    create_tables(client)

    # ##: Create indexes for performance optimization.
    create_indexes_for_optimization(client)
    logger.info("Database initialization complete via RPC. All tables and indexes ensured.")


def main():
    """Main function to initialize the database using Supabase client and RPC."""
    logger.info(f"Attempting to initialize database using Supabase client from app.db.database")
    logger.info(f"Supabase URL: {config.supabase_url}")

    try:
        logger.info("Using global Supabase client for initialization.")

        initialize_database(supabase)
        logger.info("Database schema initialization process via RPC completed successfully.")
    except Exception:
        logger.exception("An error occurred during Supabase database schema initialization via RPC")
        raise


if __name__ == "__main__":
    main()
