"""Interview scheduling HTTP routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.dependencies import get_current_user, require_admin
from app.api.v1.interviews.application.interview_service import InterviewService
from app.api.v1.interviews.presentation.dependencies import get_interview_service
from app.api.v1.interviews.presentation.schemas import (
    InterviewListResponse,
    InterviewResponse,
    ScheduleInterviewRequest,
    UpdateInterviewRequest,
    to_interview_response,
)
from app.shared.time import to_naive_utc

router = APIRouter()


@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    from_date: datetime = Query(..., alias="from"),
    to_date: datetime = Query(..., alias="to"),
    _: UserEntity = Depends(require_admin),
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewListResponse:
    """List interviews scheduled within a date range (admin only)."""
    items = await interview_service.list_between(to_naive_utc(from_date), to_naive_utc(to_date))
    return InterviewListResponse(items=[to_interview_response(item) for item in items])


@router.get("/candidate/{candidate_id}", response_model=InterviewListResponse)
async def list_candidate_interviews(
    candidate_id: str,
    _: UserEntity = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewListResponse:
    """List interviews for a specific candidate."""
    items = await interview_service.list_for_candidate(candidate_id)
    return InterviewListResponse(items=[to_interview_response(item) for item in items])


@router.post("/candidate/{candidate_id}", response_model=InterviewResponse, status_code=201)
async def schedule_interview(
    candidate_id: str,
    body: ScheduleInterviewRequest,
    current_user: UserEntity = Depends(require_admin),
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    """Schedule an interview for a candidate (admin only)."""
    interview = await interview_service.schedule_interview(
        candidate_id=candidate_id,
        reviewer_id=body.reviewer_id,
        scheduled_at=to_naive_utc(body.scheduled_at),
        interview_type=body.interview_type,
        location_or_link=body.location_or_link,
        notes=body.notes,
        actor_id=current_user.id,
    )
    return to_interview_response(interview)


@router.patch("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    body: UpdateInterviewRequest,
    current_user: UserEntity = Depends(require_admin),
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    """Update a scheduled interview (admin only)."""
    interview = await interview_service.update_interview(
        interview_id,
        reviewer_id=body.reviewer_id,
        scheduled_at=to_naive_utc(body.scheduled_at),
        interview_type=body.interview_type,
        location_or_link=body.location_or_link,
        notes=body.notes,
        actor_id=current_user.id,
    )
    return to_interview_response(interview)


@router.delete("/{interview_id}", status_code=204)
async def cancel_interview(
    interview_id: str,
    current_user: UserEntity = Depends(require_admin),
    interview_service: InterviewService = Depends(get_interview_service),
) -> None:
    """Cancel a scheduled interview (admin only)."""
    await interview_service.delete_interview(interview_id, actor_id=current_user.id)
