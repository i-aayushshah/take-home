"""GitHub Models API adapter for candidate summary generation."""

import httpx

from app.api.v1.candidates.domain.exceptions import AISummaryError
from app.shared.summary_text import normalize_ai_summary

GITHUB_MODELS_URL = "https://models.github.ai/inference/chat/completions"
GITHUB_API_VERSION = "2022-11-28"


class GitHubModelsStrategy:
    """Calls GitHub Models chat completions for candidate summaries."""

    def __init__(self, token: str, model: str) -> None:
        self._token = token
        self._model = model

    async def generate(self, context: str) -> str:
        """Generate a candidate summary from the supplied context.

        Args:
            context: Serialized candidate profile data.

        Returns:
            Generated summary text from the GitHub Models API.

        Raises:
            AISummaryError: When the GitHub Models API returns an error response.
        """
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
                                    "You are a recruitment analyst. Write a concise, professional "
                                    "hiring brief in 3-5 sentences of plain prose. "
                                    "Start directly with the summary. Do not include a title, heading, "
                                    "markdown, asterisks, bullet points, or labels."
                                ),
                            },
                            {"role": "user", "content": f"Summarize this candidate:\n{context}"},
                        ],
                        "max_tokens": 500,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise AISummaryError(self._format_http_error(exc)) from exc
            except httpx.RequestError as exc:
                raise AISummaryError(f"GitHub Models request failed: {exc}") from exc

        payload = response.json()
        try:
            raw = payload["choices"][0]["message"]["content"]
            return normalize_ai_summary(raw)
        except (KeyError, IndexError, TypeError) as exc:
            raise AISummaryError("GitHub Models returned an unexpected response format.") from exc

    def _format_http_error(self, exc: httpx.HTTPStatusError) -> str:
        """Build a user-facing message from a GitHub Models HTTP error."""
        status = exc.response.status_code
        detail = self._extract_error_detail(exc.response)

        if status == 401:
            return "GitHub token is invalid or expired. Create a new PAT with models:read scope."
        if status == 403:
            return "GitHub token lacks models:read permission."
        if status == 400:
            return (
                detail
                or f"Invalid GitHub Models request (model: {self._model}). "
                "Try GITHUB_MODEL=openai/gpt-4o in .env."
            )
        if status == 429:
            return "GitHub Models rate limit reached. Wait a moment and retry."
        return detail or f"GitHub Models API error ({status})."

    def _extract_error_detail(self, response: httpx.Response) -> str | None:
        """Parse an error message from the GitHub Models response body."""
        try:
            payload = response.json()
        except ValueError:
            return None

        if isinstance(payload, dict):
            if isinstance(payload.get("error"), dict):
                message = payload["error"].get("message")
                if message:
                    return str(message)
            if payload.get("message"):
                return str(payload["message"])
            if payload.get("detail"):
                return str(payload["detail"])
        return None
