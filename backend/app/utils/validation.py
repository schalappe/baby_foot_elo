# -*- coding: utf-8 -*-
"""
Validation utilities for API input validation and error handling.
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


class ValidationErrorResponse(Exception):
    """
    Custom exception for validation errors with standardized format.

    Attributes
    ----------
    status_code : int
        HTTP status code to return
    detail : str
        Error message
    errors : Optional[List[Dict[str, Any]]]
        List of validation errors
    """

    def __init__(
        self,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail: str = "Validation error",
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.errors = errors or []


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors from FastAPI's request validation.

    Parameters
    ----------
    request : Request
        The request that caused the validation error
    exc : RequestValidationError
        The validation error

    Returns
    -------
    JSONResponse
        Standardized error response
    """
    errors = []
    for error in exc.errors():
        error_location = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append(
            {
                "location": error_location,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Input validation error",
            "errors": errors,
        },
    )


async def validation_error_response_handler(request: Request, exc: ValidationErrorResponse) -> JSONResponse:
    """
    Handle custom validation errors.

    Parameters
    ----------
    request : Request
        The request that caused the validation error
    exc : ValidationErrorResponse
        The custom validation error

    Returns
    -------
    JSONResponse
        Standardized error response
    """
    logger.warning(f"Custom validation error: {exc.detail}, errors: {exc.errors}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "errors": exc.errors,
        },
    )


def validate_team_players(player1_id: int, player2_id: int) -> None:
    """
    Validate that player IDs for a team are valid.

    Parameters
    ----------
    player1_id : int
        ID of the first player
    player2_id : int
        ID of the second player

    Raises
    ------
    ValidationErrorResponse
        If validation fails
    """
    errors = []

    if player1_id <= 0:
        errors.append(
            {
                "location": "player1_id",
                "message": "Player ID must be a positive integer",
                "type": "value_error",
            }
        )

    if player2_id <= 0:
        errors.append(
            {
                "location": "player2_id",
                "message": "Player ID must be a positive integer",
                "type": "value_error",
            }
        )

    if player1_id == player2_id:
        errors.append(
            {
                "location": "player1_id, player2_id",
                "message": "Players in a team must be different",
                "type": "value_error",
            }
        )

    if errors:
        raise ValidationErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player IDs for team",
            errors=errors,
        )
