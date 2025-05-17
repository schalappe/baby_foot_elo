# -*- coding: utf-8 -*-
"""
Pydantic models for match-related operations, mirroring the Matches database schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.team import TeamResponse


class MatchBase(BaseModel):
    """
    Base model for match properties directly corresponding to schema.

    Attributes
    ----------
    winner_team_id : int
        ID of the winning team.
    loser_team_id : int
        ID of the losing team.
    is_fanny : bool, optional
        Whether the match was a 'fanny' (default is False).
    played_at : datetime
        Timestamp when the match was played.
    """

    winner_team_id: int = Field(..., gt=0, description="ID of the winning team")
    loser_team_id: int = Field(..., gt=0, description="ID of the losing team")
    is_fanny: bool = Field(default=False, description="Whether the match was a 'fanny'")
    played_at: datetime = Field(..., description="Timestamp when the match was played")
    notes: Optional[str] = Field(default=None, description="Optional notes about the match")


class MatchCreate(MatchBase):
    """
    Data model for creating a new match record.
    """

    pass


class MatchUpdate(BaseModel):
    """
    Data model for updating an existing match's information.
    Matches are typically immutable once recorded. Placeholder for future needs.
    """

    pass


class MatchResponse(MatchBase):
    """
    Data model for returning match information in API responses.

    Attributes
    ----------
    match_id : int
        Unique identifier for the match.
    winner_team : Optional[TeamResponse]
        Detailed information for the winning team (populated by service layer).
    loser_team : Optional[TeamResponse]
        Detailed information for the losing team (populated by service layer).
    """

    match_id: int = Field(..., gt=0, description="Unique identifier for the match")
    winner_team: Optional[TeamResponse] = Field(default=None, description="Details for the winning team")
    loser_team: Optional[TeamResponse] = Field(default=None, description="Details for the losing team")
    notes: Optional[str] = Field(default=None, description="Optional notes about the match")

    class Config:
        from_attributes = True


class MatchWithEloResponse(MatchResponse):
    """
    Extended match response that includes ELO changes.

    Attributes
    ----------
    elo_changes : dict
        Dictionary mapping player IDs to their ELO changes.
    """

    elo_changes: dict = Field(default_factory=dict, description="ELO changes for each player")
