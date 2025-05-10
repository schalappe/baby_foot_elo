# -*- coding: utf-8 -*-
"""
Pydantic models for periodic player rankings, mirroring the Periodic_Rankings database schema.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .player import PlayerResponse


class PeriodicRankingBase(BaseModel):
    """
    Base model for periodic ranking properties.

    Attributes
    ----------
    player_id : int
        ID of the player.
    year : int
        Year of the ranking period.
    month : int
        Month of the ranking period.
    day : int
        Day of the ranking period (snapshot day).
    initial_elo : int
        Player's ELO at the start of the period.
    final_elo : int
        Player's ELO at the end of the period (snapshot time).
    ranking : int
        Player's rank in this period.
    matches_played : int
        Number of matches played by the player in this period.
    wins : int
        Number of matches won by the player in this period.
    losses : int
        Number of matches lost by the player in this period.
    """

    player_id: int = Field(..., gt=0, description="ID of the player")
    year: int = Field(..., ge=1900, le=2200, description="Year of the ranking period")
    month: int = Field(..., ge=1, le=12, description="Month of the ranking period")
    day: int = Field(..., ge=1, le=31, description="Day of the ranking snapshot")
    initial_elo: int = Field(..., ge=0, description="Player's ELO at the start of the period")
    final_elo: int = Field(..., ge=0, description="Player's ELO at the time of the ranking snapshot")
    ranking: int = Field(..., gt=0, description="Player's rank for this period")
    matches_played: int = Field(..., ge=0, description="Matches played by the player in this period")
    wins: int = Field(..., ge=0, description="Matches won by the player in this period")
    losses: int = Field(..., ge=0, description="Matches lost by the player in this period")


class PeriodicRankingCreate(PeriodicRankingBase):
    """
    Data model for creating a new periodic ranking entry.
    All fields from PeriodicRankingBase are required.
    """

    pass


class PeriodicRankingUpdate(BaseModel):
    """
    Data model for updating a periodic ranking entry.
    Periodic rankings are typically immutable.
    """

    pass


class PeriodicRankingResponse(PeriodicRankingBase):
    """
    Data model for returning periodic ranking information.

    Attributes
    ----------
    ranking_id : int
        Unique identifier for the periodic ranking entry.
    player : Optional[PlayerResponse]
        Detailed information for the player (populated by service layer).
    """

    ranking_id: int = Field(..., gt=0, description="Unique ID for the periodic ranking entry")
    player: Optional[PlayerResponse] = Field(default=None, description="Details for the ranked player")

    model_config = {"from_attributes": True}
