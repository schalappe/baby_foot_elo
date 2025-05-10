# -*- coding: utf-8 -*-
"""
ELO Recalculation Service

This module provides utilities to recalculate historical ELO ratings for all players.
It allows for replaying matches with potentially different ELO calculation parameters.
"""

from typing import Any, Dict

from loguru import logger

from app.crud import matches as crud_matches
from app.crud import players as crud_players
from app.services.elo.calculator import (
    calculate_elo_change,
    calculate_team_elo,
    calculate_win_probability,
)


def recalculate_all_elos(initial_elo: int = 1000) -> Dict[str, Any]:
    """
    Recalculate ELO ratings for all players by replaying all historical matches.

    Parameters
    ----------
    initial_elo : int, optional
        The ELO rating to assign to all players at the start of the recalculation.
        Default is 1000.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - 'final_recalculated_elos': Dict[player_id, new_elo]
        - 'original_elos_for_comparison': Dict[player_id, original_db_elo]
        - 'elo_evolution_log': List of recalculation steps for analysis.
    """
    logger.info(f"Starting ELO recalculation with initial_elo={initial_elo}")

    all_players_db = crud_players.get_all_players()
    if not all_players_db:
        logger.warning("No players found in the database. Aborting recalculation.")
        return {
            "final_recalculated_elos": {},
            "original_elos_for_comparison": {},
            "elo_evolution_log": [],
        }

    recalculated_elos: Dict[int, int] = {}
    original_elos_for_comparison: Dict[int, int] = {}
    for player_data in all_players_db:
        player_id = player_data["player_id"]
        recalculated_elos[player_id] = initial_elo
        original_elos_for_comparison[player_id] = player_data.get("global_elo", initial_elo)

    historical_matches = crud_matches.get_all_matches_for_recalculation()
    if not historical_matches:
        logger.info("No historical matches found. Returning initial ELOs.")
        return {
            "final_recalculated_elos": recalculated_elos,
            "original_elos_for_comparison": original_elos_for_comparison,
            "elo_evolution_log": [],
        }

    elo_evolution_log = []
    match_count = 0

    for match in historical_matches:
        match_count += 1
        match_id = match["match_id"]
        logger.debug(f"Processing match_id: {match_id} ({match_count}/{len(historical_matches)})")

        winner_p1_id = match["winner_p1_id"]
        winner_p2_id = match["winner_p2_id"]
        loser_p1_id = match["loser_p1_id"]
        loser_p2_id = match["loser_p2_id"]

        # ##: Get current recalculated ELOs for players in the match.
        # ##: Default to initial_elo if a player somehow wasn't in the initial player list (should not happen).
        elo_w1 = recalculated_elos.get(winner_p1_id, initial_elo)
        elo_w2 = recalculated_elos.get(winner_p2_id, initial_elo)
        elo_l1 = recalculated_elos.get(loser_p1_id, initial_elo)
        elo_l2 = recalculated_elos.get(loser_p2_id, initial_elo)

        winning_team_elo = calculate_team_elo(elo_w1, elo_w2)
        losing_team_elo = calculate_team_elo(elo_l1, elo_l2)

        # ##: Probability from perspective of the winning team.
        win_prob_for_winners = calculate_win_probability(winning_team_elo, losing_team_elo)
        win_prob_for_losers = 1 - win_prob_for_winners

        # ##: Update ELOs for winning team players.
        for p_id, old_elo in [(winner_p1_id, elo_w1), (winner_p2_id, elo_w2)]:
            change = calculate_elo_change(old_elo, win_prob_for_winners, 1)
            new_elo = old_elo + change
            recalculated_elos[p_id] = new_elo
            elo_evolution_log.append(
                {
                    "match_id": match_id,
                    "player_id": p_id,
                    "team_type": "winner",
                    "old_elo": old_elo,
                    "change": change,
                    "new_elo": new_elo,
                    "win_probability_for_team": win_prob_for_winners,
                }
            )

        # ##: Update ELOs for losing team players.
        for p_id, old_elo in [(loser_p1_id, elo_l1), (loser_p2_id, elo_l2)]:
            change = calculate_elo_change(old_elo, win_prob_for_losers, 0)
            new_elo = old_elo + change
            recalculated_elos[p_id] = new_elo
            elo_evolution_log.append(
                {
                    "match_id": match_id,
                    "player_id": p_id,
                    "team_type": "loser",
                    "old_elo": old_elo,
                    "change": change,
                    "new_elo": new_elo,
                    "win_probability_for_team": win_prob_for_losers,
                }
            )
        logger.debug(f"Match {match_id} processed. Current ELOs (sample): {dict(list(recalculated_elos.items())[:2])}")

    logger.info(f"ELO recalculation completed. Processed {len(historical_matches)} matches.")
    logger.info(f"Final recalculated ELOs: {recalculated_elos}")
    logger.info(f"Original DB ELOs for comparison: {original_elos_for_comparison}")

    return {
        "final_recalculated_elos": recalculated_elos,
        "original_elos_for_comparison": original_elos_for_comparison,
        "elo_evolution_log": elo_evolution_log,
    }
