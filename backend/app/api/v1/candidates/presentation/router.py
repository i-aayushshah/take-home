"""Candidate HTTP routes."""

import asyncio
import json

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.candidates.application.ai_service import AiService
from app.api.v1.candidates.application.audit_service import AuditService
from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.application.resume_service import ResumeService
from app.api.v1.candidates.application.score_service import ScoreService
from app.api.v1.candidates.domain.candidate import WorkExperienceEntry
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.presentation.dependencies import (
    get_ai_service,
    get_audit_service,
    get_candidate_service,
    get_resume_service,
    get_score_service,
)
from app.api.v1.candidates.presentation.schemas import (
    AuditEventListResponse,
    CandidateDetailResponse,
    CandidateListResponse,
    CreateCandidateRequest,
    ParseResumeResponse,
    ScoreResponse,
    ScoreSubmitRequest,
    SummaryResponse,
    UpdateNotesRequest,
    UpdateProfileRequest,
    UpdateStatusRequest,
    WorkExperienceResponse,
    to_audit_response,
    to_detail_response,
    to_list_item,
    to_score_response,
)
from app.api.v1.dependencies import get_current_user, require_admin
from app.shared.rate_limiter import RateLimiter
from app.shared.sse import score_event_bus

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


@router.post("", response_model=CandidateDetailResponse, status_code=201)
async def create_candidate(
    body: CreateCandidateRequest,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Create a new candidate application (admin only)."""
    candidate = await candidate_service.create_candidate(
        name=body.name,
        email=body.email,
        role_applied=body.role_applied,
        skills=body.skills,
        description=body.description,
        actor_id=current_user.id,
        source="admin",
    )
    detail = await candidate_service.get_candidate(candidate.id, current_user.id, True)
    return to_detail_response(detail)


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


@router.get("/{candidate_id}/audit", response_model=AuditEventListResponse)
async def list_audit_events(
    candidate_id: str,
    _: UserEntity = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> AuditEventListResponse:
    """Return audit trail for a candidate (admin only)."""
    await candidate_service.get_candidate(candidate_id, "", True)
    events = await audit_service.list_for_candidate(candidate_id)
    return AuditEventListResponse(items=[to_audit_response(event) for event in events])


@router.get("/{candidate_id}/stream")
async def stream_candidate_scores(
    candidate_id: str,
    current_user: UserEntity = Depends(get_current_user),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> StreamingResponse:
    """Stream score events for a candidate via Server-Sent Events."""
    await candidate_service.get_candidate(candidate_id, current_user.id, current_user.role == Role.ADMIN)

    async def event_generator():
        queue = score_event_bus.subscribe(candidate_id)
        try:
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps({'type': 'score', 'payload': event})}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            score_event_bus.unsubscribe(candidate_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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


@router.post("/{candidate_id}/parse-resume", response_model=ParseResumeResponse)
async def parse_resume(
    candidate_id: str,
    _: UserEntity = Depends(require_admin),
    ai_service: AiService = Depends(get_ai_service),
) -> ParseResumeResponse:
    """Extract structured profile fields from an uploaded resume (admin only)."""
    parsed = await ai_service.parse_resume(candidate_id)
    return ParseResumeResponse(
        skills=list(parsed.get("skills") or []),
        description=parsed.get("description"),
        work_experience=[
            WorkExperienceResponse(
                company=str(item.get("company", "")),
                title=str(item.get("title", "")),
                start=str(item.get("start", "")),
                end=item.get("end"),
                summary=item.get("summary"),
            )
            for item in (parsed.get("work_experience") or [])
            if isinstance(item, dict)
        ],
    )


@router.patch("/{candidate_id}/profile", response_model=CandidateDetailResponse)
async def update_profile(
    candidate_id: str,
    body: UpdateProfileRequest,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Apply reviewed profile fields to a candidate (admin only)."""
    experience = tuple(
        WorkExperienceEntry(
            company=entry.company,
            title=entry.title,
            start=entry.start,
            end=entry.end,
            summary=entry.summary,
        )
        for entry in body.work_experience
    )
    await candidate_service.update_profile(
        candidate_id,
        skills=body.skills,
        description=body.description,
        work_experience=experience,
        actor_id=current_user.id,
    )
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, True)
    return to_detail_response(candidate)


@router.patch("/{candidate_id}/status", response_model=CandidateDetailResponse)
async def update_candidate_status(
    candidate_id: str,
    body: UpdateStatusRequest,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Update hiring pipeline status (admin only)."""
    status = CandidateStatus(body.status)
    await candidate_service.update_status(
        candidate_id,
        status,
        body.rejection_reason,
        actor_id=current_user.id,
    )
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, True)
    return to_detail_response(candidate)


@router.patch("/{candidate_id}/notes", response_model=CandidateDetailResponse)
async def update_notes(
    candidate_id: str,
    body: UpdateNotesRequest,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> CandidateDetailResponse:
    """Update admin-only internal notes for a candidate."""
    await candidate_service.update_internal_notes(
        candidate_id,
        body.internal_notes,
        actor_id=current_user.id,
    )
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, True)
    return to_detail_response(candidate)


@router.post("/{candidate_id}/resume", response_model=CandidateDetailResponse)
async def upload_resume(
    candidate_id: str,
    file: UploadFile = File(...),
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
    resume_service: ResumeService = Depends(get_resume_service),
) -> CandidateDetailResponse:
    """Upload or replace a candidate resume (admin only)."""
    try:
        filename = await resume_service.save_resume(candidate_id, file)
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await candidate_service.attach_resume(candidate_id, filename, actor_id=current_user.id)
    candidate = await candidate_service.get_candidate(candidate_id, current_user.id, True)
    return to_detail_response(candidate)


@router.get("/{candidate_id}/resume")
async def download_resume(
    candidate_id: str,
    _: UserEntity = Depends(get_current_user),
    candidate_service: CandidateService = Depends(get_candidate_service),
    resume_service: ResumeService = Depends(get_resume_service),
) -> FileResponse:
    """Download the candidate resume when available."""
    candidate = await candidate_service.get_candidate(candidate_id, "", True)
    if not candidate.resume_filename:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Resume not uploaded.")

    path = resume_service.resolve_resume_path(candidate_id, candidate.resume_filename)
    if path is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Resume file missing on disk.")

    return FileResponse(path, filename=candidate.resume_filename)


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(
    candidate_id: str,
    current_user: UserEntity = Depends(require_admin),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> None:
    """Soft-delete a candidate record."""
    await candidate_service.soft_delete_candidate(candidate_id, actor_id=current_user.id)
