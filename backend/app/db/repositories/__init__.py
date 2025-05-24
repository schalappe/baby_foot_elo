# -*- coding: utf-8 -*-
"""
This module provides a collection of repositories for database operations.
"""

from app.db.repositories.matches import (
    create_match,
    delete_match,
    get_all_matches,
    get_fanny_matches,
    get_match,
    get_matches_by_date_range,
    get_matches_by_player,
    get_matches_by_team,
)
from app.db.repositories.players import (
    batch_insert_players,
    create_player,
    delete_player,
    get_all_players,
    get_player,
    get_player_by_name,
    update_player,
)
from app.db.repositories.players_elo_history import (
    batch_record_elo_updates,
    get_elo_history_by_match,
    get_elo_history_by_player_match,
    get_player_elo_history,
    record_elo_update,
)
from app.db.repositories.stats import get_player_stats, get_team_stats
from app.db.repositories.teams import (
    batch_insert_teams,
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_team_rankings,
    get_teams_by_player,
    update_team,
)
from app.db.repositories.teams_elo_history import (
    batch_record_team_elo_updates,
    get_team_elo_history,
    get_team_elo_history_by_match,
    get_team_elo_history_by_team_match,
    record_team_elo_update,
)

__all__ = [
    # ##: Players.
    "create_player",
    "get_player",
    "get_player_by_name",
    "get_all_players",
    "update_player",
    "delete_player",
    "batch_insert_players",
    # ##: Teams.
    "create_team",
    "get_team",
    "get_all_teams",
    "update_team",
    "delete_team",
    "batch_insert_teams",
    "get_teams_by_player",
    "get_team_rankings",
    # ##: Matches.
    "create_match",
    "get_match",
    "delete_match",
    "get_all_matches",
    "get_matches_by_team",
    "get_matches_by_player",
    "get_matches_by_date_range",
    "get_fanny_matches",
    # ##: Players ELO History.
    "record_elo_update",
    "batch_record_elo_updates",
    "get_player_elo_history",
    "get_elo_history_by_match",
    "get_elo_history_by_player_match",
    # ##: Teams ELO History.
    "record_team_elo_update",
    "batch_record_team_elo_updates",
    "get_team_elo_history",
    "get_team_elo_history_by_match",
    "get_team_elo_history_by_team_match",
    # ##: Stats.
    "get_player_stats",
    "get_team_stats",
]
