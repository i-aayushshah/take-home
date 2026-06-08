"""Operational health endpoints."""

import httpx
from fastapi import APIRouter, Depends

from app.api.v1.dependencies import require_admin
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/ai")
async def ai_health(settings: Settings = Depends(get_settings), _: object = Depends(require_admin)) -> dict:
    """Validate GitHub Models configuration without generating a full summary."""
    if not settings.github_token:
        return {"status": "mock", "detail": "GITHUB_TOKEN not set — using mock summaries."}
    if settings.ai_summary_fallback_mock:
        return {"status": "mock", "detail": "AI_SUMMARY_FALLBACK_MOCK=true — token present but mock enabled."}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://models.github.ai/catalog/models",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {settings.github_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"status": "error", "detail": str(exc)}

    return {"status": "ok", "model": settings.github_model, "detail": "GitHub Models token is valid."}
