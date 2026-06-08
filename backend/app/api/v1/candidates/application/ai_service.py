"""AI summary generation orchestration."""

import asyncio
from typing import Protocol

from app.api.v1.candidates.domain.candidate import CandidateAggregate
from app.api.v1.candidates.domain.exceptions import CandidateNotFoundError
from app.api.v1.candidates.infrastructure.github_models_strategy import GitHubModelsStrategy
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.config import Settings
from app.shared.summary_text import normalize_ai_summary


class SummaryStrategy(Protocol):
    """Interface for pluggable summary generation backends."""

    async def generate(self, context: str) -> str:
        """Generate a summary from the supplied candidate context."""


class MockLLMStrategy:
    """Simulates an async LLM call with a two-second delay."""

    async def generate(self, context: str) -> str:
        """Return a mock summary after a simulated network delay."""
        await asyncio.sleep(2)
        return f"AI-generated summary based on candidate profile. Context length: {len(context)} characters."


def build_summary_strategy(settings: Settings) -> SummaryStrategy:
    """Select the configured summary generation strategy.

    Args:
        settings: Application settings containing GitHub token configuration.

    Returns:
        A GitHub Models strategy when configured, otherwise a mock strategy.
    """
    if settings.github_token and not settings.ai_summary_fallback_mock:
        return GitHubModelsStrategy(settings.github_token, settings.github_model)
    return MockLLMStrategy()


class AiService:
    """Orchestrates summary generation and persistence."""

    def __init__(self, uow: CandidateUnitOfWork, strategy: SummaryStrategy) -> None:
        self._uow = uow
        self._strategy = strategy

    async def generate_summary(self, candidate_id: str) -> str:
        """Generate and store a candidate summary.

        Args:
            candidate_id: UUID of the candidate to summarise.

        Returns:
            The generated summary string.

        Raises:
            CandidateNotFoundError: When the candidate does not exist.
        """
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        context = self._build_context(candidate)
        summary = normalize_ai_summary(await self._strategy.generate(context))
        updated = await self._uow.candidates.update_ai_summary(candidate_id, summary)
        if updated is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        await self._uow.commit()
        return summary

    def _build_context(self, candidate: CandidateAggregate) -> str:
        """Serialize candidate profile fields for the LLM prompt."""
        skills = ", ".join(candidate.skills)
        lines = [
            f"Name: {candidate.name}",
            f"Email: {candidate.email}",
            f"Role: {candidate.role_applied}",
            f"Status: {candidate.status.value}",
            f"Skills: {skills}",
        ]
        if candidate.description:
            lines.append(f"Description: {candidate.description}")
        if candidate.work_experience:
            lines.append("Work Experience:")
            for entry in candidate.work_experience:
                period = f"{entry.start} – {entry.end or 'Present'}"
                lines.append(f"- {entry.title} at {entry.company} ({period})")
                if entry.summary:
                    lines.append(f"  {entry.summary}")
        return "\n".join(lines)
