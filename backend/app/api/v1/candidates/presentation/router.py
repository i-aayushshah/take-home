"""Candidate HTTP routes."""

from fastapi import APIRouter, Depends, Query

from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.candidates.application.ai_service import AiService
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.application.score_service import ScoreService
from app.api.v1.candidates.presentation.dependencies import (
    get_ai_service,
    get_candidate_service,
    get_score_service,
)
from app.api.v1.candidates.presentation.schemas import (
    CandidateDetailResponse,
    CandidateListResponse,
    ScoreResponse,
    ScoreSubmitRequest,
    SummaryResponse,
    UpdateNotesRequest,
    to_detail_response,
    to_list_item,
    to_score_response,
)
from app.api.v1.dependencies import get_current_user, require_admin
from app.shared.rate_limiter import RateLimiter

router = APIRouter()

_summary_limiter = RateLimiter(max_requests=5, window_seconds=60)
_score_limiter = RateLimiter(max_requests=30, window_seconds=60)


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    status: CandidateStatus | None = Query(default=None),
    role_applied: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
    _: UserEntity = Depends(get_current_user),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateListResponse:
    """List candidates with SQL-level filters and pagination."""
    result = await candidate_service.list_candidates(status, role_applied, skill, keyword, offset, limit)
    return CandidateListResponse(
        items=[to_list_item(item) for item in result.items],
        total=result.total,
        offset=result.offset,
        limit=result.limit,
    )


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(
    candidate_id: str,
    current_user: UserEntity = Depends(get_current_user),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Return candidate detail with role-aware scores and notes."""
    is_admin = current_user.role == Role.ADMIN
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, is_admin)
    return to_detail_response(candidate)


@router.post("/{candidate_id}/scores", response_model=ScoreResponse, dependencies=[Depends(_score_limiter)])
async def submit_score(
    candidate_id: str,
    body: ScoreSubmitRequest,
    current_user: UserEntity = Depends(get_current_user),
    score_service: ScoreService = Depends(get_score_service),
) -> ScoreResponse:
    """Submit a reviewer score for a candidate category."""
    score = await score_service.submit_score(
        candidate_id,
        current_user.id,
        body.category,
        body.score,
        body.note,
    )
    return to_score_response(score)


@router.post("/{candidate_id}/summary", response_model=SummaryResponse, dependencies=[Depends(_summary_limiter)])
async def trigger_summary(
    candidate_id: str,
    _: UserEntity = Depends(get_current_user),
    ai_service: AiService = Depends(get_ai_service),
) -> SummaryResponse:
    """Trigger AI summary generation for a candidate."""
    summary = await ai_service.generate_summary(candidate_id)
    return SummaryResponse(summary=summary)


@router.patch("/{candidate_id}/notes", response_model=CandidateDetailResponse)
async def update_notes(
    candidate_id: str,
    body: UpdateNotesRequest,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Update admin-only internal notes for a candidate."""
    await candidate_service.update_internal_notes(candidate_id, body.internal_notes)
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, True)
    return to_detail_response(candidate)


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(
    candidate_id: str,
    _: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> None:
    """Soft-delete a candidate record."""
    await candidate_service.soft_delete_candidate(candidate_id)
