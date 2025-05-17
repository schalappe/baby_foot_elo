# -*- coding: utf-8 -*-
"""
Module containing health check endpoint.
"""

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "OK",
        },
    },
)


@router.get("/", status_code=status.HTTP_200_OK)
def health_check():
    """
    Simple health check endpoint returning a JSON payload with a single key "status" valued at "ok".
    """
    return {"status": "ok"}
