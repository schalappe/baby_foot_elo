# -*- coding: utf-8 -*-
"""
This module provides a collection of repositories for database operations.
"""

from app.db.repositories.matches import (
    create_match_by_team_ids,
    delete_match_by_id,
    get_all_matches,
    get_fanny_matches,
    get_match_by_id,
    get_matches_by_date_range,
    get_matches_by_player_id,
    get_matches_by_team_id,
)
from app.db.repositories.players import (
    batch_insert_players_by_name,
    create_player_by_name,
    delete_player_by_id,
    get_all_players,
    get_player_by_id_or_name,
    update_player_name_or_elo,
)
from app.db.repositories.players_elo_history import (
    batch_record_player_elo_updates,
    get_player_elo_history_by_id,
    get_player_elo_history_by_match_id,
    get_players_elo_history_by_match_id,
    record_player_elo_update,
)
from app.db.repositories.stats import get_player_stats, get_team_stats
from app.db.repositories.teams import (
    batch_insert_teams_by_player_ids,
    create_team_by_player_ids,
    delete_team_by_id,
    get_all_teams,
    get_team_by_id,
    get_teams_by_player_id,
    update_team_elo,
)
from app.db.repositories.teams_elo_history import (
    batch_record_team_elo_updates,
    get_team_elo_history_by_id,
    get_team_elo_history_by_match_id,
    get_teams_elo_history_by_match_id,
    record_team_elo_update,
)

__all__ = [
    # ##: Players.
    "create_player_by_name",
    "get_player_by_id_or_name",
    "get_all_players",
    "update_player_name_or_elo",
    "delete_player_by_id",
    "batch_insert_players_by_name",
    # ##: Teams.
    "create_team_by_player_ids",
    "get_team_by_id",
    "get_all_teams",
    "update_team_elo",
    "delete_team_by_id",
    "batch_insert_teams_by_player_ids",
    "get_teams_by_player_id",
    # ##: Matches.
    "create_match_by_team_ids",
    "get_match_by_id",
    "delete_match_by_id",
    "get_all_matches",
    "get_matches_by_team_id",
    "get_matches_by_player_id",
    "get_matches_by_date_range",
    "get_fanny_matches",
    # ##: Players ELO History.
    "record_player_elo_update",
    "batch_record_player_elo_updates",
    "get_player_elo_history_by_id",
    "get_player_elo_history_by_match_id",
    "get_players_elo_history_by_match_id",
    # ##: Teams ELO History.
    "record_team_elo_update",
    "batch_record_team_elo_updates",
    "get_team_elo_history_by_id",
    "get_team_elo_history_by_match_id",
    "get_teams_elo_history_by_match_id",
    # ##: Stats.
    "get_player_stats",
    "get_team_stats",
]
