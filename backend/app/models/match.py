# -*- coding: utf-8 -*-
"""
Pydantic models for match-related operations in the Baby Foot Elo backend.

This module defines data models for creating and returning match information.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel

from .player import PlayerResponse


class MatchCreate(BaseModel):
    """
    Data model for creating a new match.

    Attributes
    ----------
    winning_team_players : List[int]
        Player IDs for the winning team.
    losing_team_players : List[int]
        Player IDs for the losing team.
    winner_score : int
        Score of the winning team.
    loser_score : int
        Score of the losing team.
    is_fanny : bool
        Whether the match is a 'fanny' match (default False).
    """
    winning_team_players: List[int]
    losing_team_players: List[int]
    winner_score: int
    loser_score: int
    is_fanny: bool = False


class EloChangeResponse(BaseModel):
    """
    Data model for individual ELO changes resulting from a match.

    Attributes
    ----------
    player_id : int
        ID of the player whose elo changed.
    old_elo : int
        ELO rating before the match.
    new_elo : int
        ELO rating after the match.
    change : int
        Difference between new and old ELO (new_elo - old_elo).
    """
    player_id: int
    old_elo: int
    new_elo: int
    change: int


class TeamResponse(BaseModel):
    """
    Data model for returning a team's data in match responses.

    Attributes
    ----------
    players : List[PlayerResponse]
        List of players on the team.
    team_elo : int
        Combined ELO rating for the team.
    """
    players: List[PlayerResponse]
    team_elo: int


class MatchResponse(BaseModel):
    """
    Data model for returning match information in API responses.

    Attributes
    ----------
    id : int
        Unique identifier for the match.
    winning_team : TeamResponse
        Data for the winning team.
    losing_team : TeamResponse
        Data for the losing team.
    winner_score : int
        Score of the winning team.
    loser_score : int
        Score of the losing team.
    is_fanny : bool
        Whether the match is a 'fanny' match.
    date : datetime
        Date and time when the match was played.
    elo_changes : List[EloChangeResponse]
        List of ELO changes for all involved players.
    """
    id: int
    winning_team: TeamResponse
    losing_team: TeamResponse
    winner_score: int
    loser_score: int
    is_fanny: bool
    date: datetime
    elo_changes: List[EloChangeResponse]

    class Config:
        from_attributes = True
