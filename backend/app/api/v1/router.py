"""API v1 router assembly."""

from fastapi import APIRouter

from app.api.v1.auth.presentation.router import router as auth_router
from app.api.v1.candidates.presentation.router import router as candidates_router
from app.api.v1.health.router import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(candidates_router, prefix="/candidates", tags=["candidates"])
router.include_router(health_router, prefix="/health", tags=["health"])
