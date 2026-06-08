"""GitHub Models API adapter for candidate summary generation."""

import httpx


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
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://models.inference.ai.azure.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": "You are a recruitment analyst."},
                        {"role": "user", "content": f"Summarize this candidate:\n{context}"},
                    ],
                    "max_tokens": 500,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
