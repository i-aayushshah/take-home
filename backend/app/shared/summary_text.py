"""Helpers for normalizing AI-generated summary text."""

import re


def normalize_ai_summary(text: str) -> str:
    """Strip markdown formatting and normalize whitespace from LLM output."""
    cleaned = text.strip()
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__(.+?)__", r"\1", cleaned)
    cleaned = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", cleaned)
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^[-*]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(
        r"^Hiring Brief:\s*.+?\s*(?:\n|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
