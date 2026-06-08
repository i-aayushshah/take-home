"""Public application submission routes (no authentication)."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.application.resume_service import ResumeService
from app.api.v1.candidates.presentation.dependencies import get_candidate_service, get_resume_service
from app.api.v1.candidates.presentation.schemas import ApplicationSubmittedResponse
from app.shared.rate_limiter import RateLimiter

router = APIRouter()

_application_limiter = RateLimiter(max_requests=5, window_seconds=60)


@router.post("", response_model=ApplicationSubmittedResponse, status_code=201, dependencies=[Depends(_application_limiter)])
async def submit_application(
    name: str = Form(..., min_length=1, max_length=255),
    email: str = Form(..., min_length=3, max_length=255),
    role_applied: str = Form(..., min_length=1, max_length=100),
    skills: str = Form(..., min_length=1),
    description: str | None = Form(default=None),
    resume: UploadFile | None = File(default=None),
    candidate_service: CandidateService = Depends(get_candidate_service),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ApplicationSubmittedResponse:
    """Allow candidates to self-apply without authentication."""
    skill_list = [item.strip() for item in skills.split(",") if item.strip()]
    if not skill_list:
        raise HTTPException(status_code=400, detail="Provide at least one skill.")

    candidate = await candidate_service.create_candidate(
        name=name.strip(),
        email=email.strip().lower(),
        role_applied=role_applied.strip(),
        skills=skill_list,
        description=description.strip() if description else None,
        actor_id=None,
        source="public",
    )

    if resume and resume.filename:
        try:
            filename = await resume_service.save_resume(candidate.id, resume)
            await candidate_service.attach_resume(candidate.id, filename, actor_id=None)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ApplicationSubmittedResponse(
        id=candidate.id,
        message="Application received. Our hiring team will review your profile shortly.",
    )
