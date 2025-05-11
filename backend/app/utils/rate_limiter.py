# -*- coding: utf-8 -*-
"""
Rate limiting utilities for the Baby Foot Elo API.

This module provides rate limiting functionality for API endpoints to prevent abuse.
"""

import time
from collections import defaultdict
from typing import Callable, Dict, Optional, Tuple

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.error_handlers import ErrorResponse


class RateLimiter:
    """
    Simple in-memory rate limiter implementation.

    Attributes
    ----------
    requests : Dict[str, Dict[str, Tuple[int, float]]]
        Dictionary to track requests by IP and endpoint.
    """

    def __init__(self):
        """Initialize the rate limiter."""
        self.requests: Dict[str, Dict[str, Tuple[int, float]]] = defaultdict(dict)

    def is_rate_limited(self, key: str, endpoint: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Check if a request should be rate limited.

        Parameters
        ----------
        key : str
            Unique identifier for the client (e.g., IP address).
        endpoint : str
            API endpoint being accessed.
        limit : int
            Maximum number of requests allowed in the time window.
        window : int
            Time window in seconds.

        Returns
        -------
        Tuple[bool, int, int]
            A tuple containing:
            - Whether the request is rate limited (True if limited)
            - Remaining requests allowed
            - Time until reset in seconds
        """
        current_time = time.time()

        # ##: Initialize or get existing count and timestamp.
        if endpoint not in self.requests[key]:
            self.requests[key][endpoint] = (0, current_time)

        count, timestamp = self.requests[key][endpoint]

        # ##: Reset count if window has passed.
        if current_time - timestamp > window:
            count = 0
            timestamp = current_time

        # ##: Increment count and check limit.
        count += 1
        self.requests[key][endpoint] = (count, timestamp)

        # ##: Calculate remaining requests and time until reset.
        remaining = max(0, limit - count)
        reset_time = int(window - (current_time - timestamp))

        return count > limit, remaining, reset_time


# ##: Global rate limiter instance.
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.

    Attributes
    ----------
    rate_limiter : RateLimiter
        The rate limiter instance.
    default_limit : int
        Default request limit per time window.
    default_window : int
        Default time window in seconds.
    endpoint_limits : Dict[str, Tuple[int, int]]
        Custom limits for specific endpoints.
    """

    def __init__(
        self,
        app: FastAPI,
        default_limit: int = 100,
        default_window: int = 60,
        endpoint_limits: Optional[Dict[str, Tuple[int, int]]] = None,
    ):
        """
        Initialize the rate limit middleware.

        Parameters
        ----------
        app : FastAPI
            The FastAPI application.
        default_limit : int, optional
            Default request limit per time window (default: 100).
        default_window : int, optional
            Default time window in seconds (default: 60).
        endpoint_limits : Optional[Dict[str, Tuple[int, int]]], optional
            Custom limits for specific endpoints (default: None).
            Format: {"/path": (limit, window)}
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.default_limit = default_limit
        self.default_window = default_window
        self.endpoint_limits = endpoint_limits or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting.

        Parameters
        ----------
        request : Request
            The incoming request.
        call_next : Callable
            The next middleware or endpoint handler.

        Returns
        -------
        Response
            The response, either from the next handler or a rate limit error.
        """
        # ##: Get client IP.
        client_ip = request.client.host if request.client else "unknown"

        # ##: Get endpoint path.
        path = request.url.path

        # ##: Determine limit and window for this endpoint.
        limit, window = self.endpoint_limits.get(path, (self.default_limit, self.default_window))

        # ##: Check rate limit.
        is_limited, remaining, reset = self.rate_limiter.is_rate_limited(client_ip, path, limit, window)

        # ##: If rate limited, return 429 response.
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ErrorResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                ).model_dump(),
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset),
                    "Retry-After": str(reset),
                },
            )

        # ##: Process the request.
        response = await call_next(request)

        # ##: Add rate limit headers to response.
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)

        return response


def setup_rate_limiting(
    app: FastAPI,
    default_limit: int = 100,
    default_window: int = 60,
    endpoint_limits: Optional[Dict[str, Tuple[int, int]]] = None,
) -> None:
    """
    Set up rate limiting for a FastAPI application.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    default_limit : int, optional
        Default request limit per time window (default: 100).
    default_window : int, optional
        Default time window in seconds (default: 60).
    endpoint_limits : Optional[Dict[str, Tuple[int, int]]], optional
        Custom limits for specific endpoints (default: None).
        Format: {"/path": (limit, window)}
    """
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=default_limit,
        default_window=default_window,
        endpoint_limits=endpoint_limits,
    )
