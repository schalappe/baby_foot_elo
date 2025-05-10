# -*- coding: utf-8 -*-
"""
Pydantic models for periodic team rankings, mirroring the Team_Periodic_Rankings database schema.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .team import TeamResponse


class TeamPeriodicRankingBase(BaseModel):
    """
    Base model for periodic team ranking properties.

    Attributes
    ----------
    team_id : int
        ID of the team.
    year : int
        Year of the ranking period.
    month : int
        Month of the ranking period.
    day : int
        Day of the ranking period (snapshot day).
    initial_elo : float
        Team's ELO at the start of the period.
    final_elo : float
        Team's ELO at the end of the period (snapshot time).
    ranking : int
        Team's rank in this period.
    matches_played : int
        Number of matches played by the team in this period.
    wins : int
        Number of matches won by the team in this period.
    losses : int
        Number of matches lost by the team in this period.
    """

    team_id: int = Field(..., gt=0, description="ID of the team")
    year: int = Field(..., ge=1900, le=2200, description="Year of the ranking period")
    month: int = Field(..., ge=1, le=12, description="Month of the ranking period")
    day: int = Field(..., ge=1, le=31, description="Day of the ranking snapshot")
    initial_elo: float = Field(..., ge=0, description="Team's ELO at the start of the period")
    final_elo: float = Field(..., ge=0, description="Team's ELO at the time of the ranking snapshot")
    ranking: int = Field(..., gt=0, description="Team's rank for this period")
    matches_played: int = Field(..., ge=0, description="Matches played by the team in this period")
    wins: int = Field(..., ge=0, description="Matches won by the team in this period")
    losses: int = Field(..., ge=0, description="Matches lost by the team in this period")


class TeamPeriodicRankingCreate(TeamPeriodicRankingBase):
    """
    Data model for creating a new periodic team ranking entry.
    All fields from TeamPeriodicRankingBase are required.
    """

    pass


class TeamPeriodicRankingUpdate(BaseModel):
    """
    Data model for updating a periodic team ranking entry.
    Periodic rankings are typically immutable.
    """

    pass


class TeamPeriodicRankingResponse(TeamPeriodicRankingBase):
    """
    Data model for returning periodic team ranking information.

    Attributes
    ----------
    team_ranking_id : int
        Unique identifier for the periodic team ranking entry.
    team : Optional[TeamResponse]
        Detailed information for the team (populated by service layer).
    """

    team_ranking_id: int = Field(..., gt=0, description="Unique ID for the periodic team ranking entry")
    team: Optional[TeamResponse] = Field(default=None, description="Details for the ranked team")

    model_config = {"from_attributes": True}
