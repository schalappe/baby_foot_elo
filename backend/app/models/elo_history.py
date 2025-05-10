# -*- coding: utf-8 -*-
"""
Pydantic models for ELO history, mirroring the ELO_History database schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class EloHistoryBase(BaseModel):
    """
    Base model for ELO history properties.

    Attributes
    ----------
    player_id : int
        ID of the player.
    match_id : int
        ID of the match that caused the ELO change.
    type : Literal['global', 'monthly']
        Type of ELO (global or monthly).
    old_elo : int
        ELO before the match.
    new_elo : int
        ELO after the match.
    difference : int
        Change in ELO (new_elo - old_elo).
    date : datetime
        Timestamp of when the ELO change was recorded (usually match time).
    """

    player_id: int = Field(..., gt=0, description="ID of the player")
    match_id: int = Field(..., gt=0, description="ID of the match")
    type: Literal["global", "monthly"] = Field(..., description="Type of ELO: 'global' or 'monthly'")
    old_elo: int = Field(..., ge=0, description="ELO before the match")
    new_elo: int = Field(..., ge=0, description="ELO after the match")
    difference: int = Field(..., description="Change in ELO (new_elo - old_elo)")
    date: datetime = Field(..., description="Timestamp of the ELO change event")


class EloHistoryCreate(EloHistoryBase):
    """
    Data model for creating a new ELO history entry.
    Year, month, and day are derived from the date field.
    """

    year: Optional[int] = Field(default=None, ge=1900, le=2200, description="Year of ELO change (derived from date)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month of ELO change (derived from date)")
    day: Optional[int] = Field(default=None, ge=1, le=31, description="Day of ELO change (derived from date)")

    @model_validator(mode="after")
    def derive_date_parts(cls, data: EloHistoryCreate) -> EloHistoryCreate:
        """
        Derive year, month, and day from the date field.
        Also validates that new_elo - old_elo == difference.
        """
        if data.date:
            data.year = data.date.year
            data.month = data.date.month
            data.day = data.date.day
        else:
            raise ValueError("date must be provided to derive date parts.")

        if (data.new_elo - data.old_elo) != data.difference:
            raise ValueError("ELO difference does not match new_elo - old_elo.")

        return data


class EloHistoryUpdate(BaseModel):
    """
    Data model for updating an ELO history entry.
    ELO history entries are typically immutable.
    """

    pass


class EloHistoryResponse(EloHistoryBase):
    """
    Data model for returning ELO history information.

    Attributes
    ----------
    history_id : int
        Unique identifier for the ELO history entry.
    year : int
        Year of the ELO change.
    month : int
        Month of the ELO change.
    day : int
        Day of the ELO change.
    """

    history_id: int = Field(..., gt=0, description="Unique ID for the ELO history entry")
    year: int = Field(..., ge=1900, le=2200, description="Year of ELO change")
    month: int = Field(..., ge=1, le=12, description="Month of ELO change")
    day: int = Field(..., ge=1, le=31, description="Day of ELO change")

    model_config = {"from_attributes": True}
