"""Resume parsing strategies using GitHub Models or mock data."""

import json

import httpx

from app.api.v1.candidates.domain.exceptions import AISummaryError
from app.api.v1.candidates.infrastructure.github_models_strategy import GITHUB_API_VERSION, GITHUB_MODELS_URL


class MockResumeParseStrategy:
    """Returns deterministic parsed resume fields for local development."""

    async def parse(self, resume_text: str) -> dict:
        """Simulate AI resume parsing."""
        preview = resume_text[:120].replace("\n", " ")
        return {
            "skills": ["Python", "React", "PostgreSQL"],
            "description": f"Experienced professional with a background reflected in their resume ({len(resume_text)} chars). {preview}…",
            "work_experience": [
                {
                    "company": "Example Corp",
                    "title": "Software Engineer",
                    "start": "2021-01",
                    "end": None,
                    "summary": "Built and maintained production web applications.",
                }
            ],
        }


class GitHubResumeParseStrategy:
    """Parses resume text into structured fields via GitHub Models."""

    def __init__(self, token: str, model: str) -> None:
        self._token = token
        self._model = model

    async def parse(self, resume_text: str) -> dict:
        """Extract structured candidate fields from resume text."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    GITHUB_MODELS_URL,
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {self._token}",
                        "X-GitHub-Api-Version": GITHUB_API_VERSION,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Extract candidate profile data from the resume. "
                                    "Respond with valid JSON only — no markdown, no commentary. "
                                    "Schema: {\"skills\": [string], \"description\": string, "
                                    "\"work_experience\": [{\"company\": string, \"title\": string, "
                                    "\"start\": string, \"end\": string|null, \"summary\": string|null}]}"
                                ),
                            },
                            {"role": "user", "content": resume_text[:12000]},
                        ],
                        "max_tokens": 1200,
                    },
                    timeout=45.0,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise AISummaryError(f"GitHub Models resume parse failed ({exc.response.status_code}).") from exc
            except httpx.RequestError as exc:
                raise AISummaryError(f"GitHub Models request failed: {exc}") from exc

        payload = response.json()
        try:
            raw = payload["choices"][0]["message"]["content"]
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed = json.loads(cleaned)
            return {
                "skills": list(parsed.get("skills") or []),
                "description": parsed.get("description"),
                "work_experience": list(parsed.get("work_experience") or []),
            }
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AISummaryError("GitHub Models returned invalid resume parse JSON.") from exc


def build_resume_parse_strategy(settings) -> MockResumeParseStrategy | GitHubResumeParseStrategy:
    """Select resume parse strategy based on configuration."""
    if settings.github_token and not settings.ai_summary_fallback_mock:
        return GitHubResumeParseStrategy(settings.github_token, settings.github_model)
    return MockResumeParseStrategy()
