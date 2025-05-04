# -*- coding: utf-8 -*-
"""
Simple test endpoint for project info (for frontend-backend integration test)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test-info")
def test_info():
    return {
        "project": "baby-foot-elo",
        "status": "integration working",
        "backend": "FastAPI"
    }
