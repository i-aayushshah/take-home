"""Interview dependency factories."""

from fastapi import Depends

from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.api.v1.candidates.presentation.dependencies import get_candidate_uow, get_email_service
from app.api.v1.interviews.application.interview_service import InterviewService
from app.shared.email_service import EmailService


def get_interview_service(
    uow: CandidateUnitOfWork = Depends(get_candidate_uow),
    email_service: EmailService = Depends(get_email_service),
) -> InterviewService:
    """Return an interview service wired with the shared unit of work."""
    return InterviewService(uow, email_service=email_service)
