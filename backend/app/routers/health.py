# -*- coding: utf-8 -*-
"""
Module containing health check endpoint.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Simple health check endpoint returning a JSON payload with a single key "status" valued at "ok".
    """
    return {"status": "ok"}