"""Unit tests for AI summary text normalization."""

from app.shared.summary_text import normalize_ai_summary


def test_normalize_ai_summary_strips_markdown_and_title() -> None:
    """Markdown bold and hiring brief titles are removed."""
    raw = "**Hiring Brief: Aisha Patel**\nAisha Patel is a strong engineer."
    assert normalize_ai_summary(raw) == "Aisha Patel is a strong engineer."
