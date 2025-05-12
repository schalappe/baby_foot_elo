# -*- coding: utf-8 -*-
"""
Pydantic models for match-related operations, mirroring the Matches database schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

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


class MatchCreate(MatchBase):
    """
    Data model for creating a new match record.
    Year, month, and day are derived from played_at.
    """

    year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2200,
        description="Year the match was played (derived from played_at)",
    )
    month: Optional[int] = Field(
        default=None, ge=1, le=12, description="Month the match was played (derived from played_at)"
    )
    day: Optional[int] = Field(
        default=None, ge=1, le=31, description="Day the match was played (derived from played_at)"
    )

    @model_validator(mode="after")
    def validate_teams_and_derive_date_parts(cls, data: MatchCreate) -> MatchCreate:
        """
        Validate that winner_team_id and loser_team_id are different.
        Derive year, month, and day from played_at.
        """
        if data.winner_team_id == data.loser_team_id:
            raise ValueError("Winner and loser team IDs cannot be the same.")

        if data.played_at:
            data.year = data.played_at.year
            data.month = data.played_at.month
            data.day = data.played_at.day
        else:
            raise ValueError("played_at must be provided to derive date parts.")
        return data


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
    year : int
        Year the match was played.
    month : int
        Month the match was played.
    day : int
        Day the match was played.
    winner_team : Optional[TeamResponse]
        Detailed information for the winning team (populated by service layer).
    loser_team : Optional[TeamResponse]
        Detailed information for the losing team (populated by service layer).
    """

    match_id: int = Field(..., gt=0, description="Unique identifier for the match")
    year: int = Field(..., ge=1900, le=2200, description="Year the match was played")
    month: int = Field(..., ge=1, le=12, description="Month the match was played")
    day: int = Field(..., ge=1, le=31, description="Day the match was played")

    winner_team: Optional[TeamResponse] = Field(default=None, description="Details for the winning team")
    loser_team: Optional[TeamResponse] = Field(default=None, description="Details for the losing team")

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
