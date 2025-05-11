# -*- coding: utf-8 -*-
"""
Centralized error handling utilities for the Baby Foot Elo API.

This module provides standardized error handling for the API, including:
- Custom exception handlers for FastAPI
- Standardized error response models
- Helper functions for raising consistent errors
"""

from typing import Any, List, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """
    Model for a single error detail.

    Attributes
    ----------
    loc : List[str]
        Location of the error (e.g., path, query, body).
    msg : str
        Error message.
    type : str
        Error type.
    """

    loc: List[Union[str, int]] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """
    Standardized error response model.

    Attributes
    ----------
    status_code : int
        HTTP status code.
    detail : Union[str, List[ErrorDetail]]
        Error details, either as a string or a list of ErrorDetail objects.
    """

    status_code: int = Field(..., description="HTTP status code")
    detail: Union[str, List[ErrorDetail]] = Field(..., description="Error details")


def setup_error_handlers(app: FastAPI) -> None:
    """
    Set up global error handlers for a FastAPI application.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle validation errors and return a standardized response.

        Parameters
        ----------
        request : Request
            The request that caused the validation error.
        exc : RequestValidationError
            The validation error.

        Returns
        -------
        JSONResponse
            A standardized error response.
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=exc.errors(),
            ).model_dump(),
        )

    @app.exception_handler(status.HTTP_404_NOT_FOUND)
    async def not_found_exception_handler(request: Request, exc: Any) -> JSONResponse:
        """
        Handle 404 errors and return a standardized response.

        Parameters
        ----------
        request : Request
            The request that caused the 404 error.
        exc : Any
            The exception.

        Returns
        -------
        JSONResponse
            A standardized error response.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            ).model_dump(),
        )
