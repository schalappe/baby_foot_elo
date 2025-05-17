# -*- coding: utf-8 -*-
"""
Pydantic models for ELO history, mirroring the ELO_History database schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

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
    old_elo: int = Field(..., ge=0, description="ELO before the match")
    new_elo: int = Field(..., ge=0, description="ELO after the match")
    difference: int = Field(..., description="Change in ELO (new_elo - old_elo)")
    date: datetime = Field(..., description="Timestamp of the ELO change event")


class EloHistoryCreate(EloHistoryBase):
    """
    Data model for creating a new ELO history entry.
    Year, month, and day are derived from the date field.
    """

    pass

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
    """

    history_id: int = Field(..., gt=0, description="Unique ID for the ELO history entry")

    class Config:
        from_attributes = True
