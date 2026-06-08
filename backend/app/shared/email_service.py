"""SMTP email delivery for candidate notifications."""

import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.api.v1.candidates.domain.candidate import CandidateAggregate
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.config import Settings
from app.shared.email_templates import (
    interview_email_body,
    interview_email_subject,
    reviewer_interview_email_body,
    reviewer_interview_email_subject,
    status_email_body,
    status_email_subject,
    verification_email_body,
    verification_email_subject,
)

logger = logging.getLogger(__name__)

NOTIFY_STATUSES = {CandidateStatus.REVIEWED, CandidateStatus.HIRED, CandidateStatus.REJECTED}


class EmailService:
    """Sends templated status emails when SMTP is configured."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_verification_email(self, to_address: str, verify_url: str) -> None:
        """Send the reviewer email verification link."""
        if not self._is_enabled():
            return
        subject = verification_email_subject()
        html = verification_email_body(verify_url=verify_url)
        await self._send_safe(to_address, subject, html)

    async def send_status_notification(
        self,
        candidate: CandidateAggregate,
        new_status: CandidateStatus,
    ) -> None:
        """Send a status-change email when enabled and applicable."""
        if new_status not in NOTIFY_STATUSES:
            return
        if not self._is_enabled():
            return

        subject = status_email_subject(new_status, candidate.name)
        html = status_email_body(
            candidate_name=candidate.name,
            role_applied=candidate.role_applied,
            status=new_status,
        )
        await self._send_safe(candidate.email, subject, html)

    async def send_interview_notification(
        self,
        *,
        candidate: CandidateAggregate,
        reviewer_email: str | None,
        reviewer_name: str | None,
        scheduled_at: datetime,
        interview_type: str,
        location_or_link: str | None,
        notes: str | None,
        updated: bool = False,
    ) -> None:
        """Notify the candidate and assigned reviewer about an interview."""
        if not self._is_enabled():
            return

        when = scheduled_at.strftime("%A, %B %d, %Y at %I:%M %p UTC")

        candidate_subject = interview_email_subject(candidate.name, updated=updated)
        candidate_html = interview_email_body(
            candidate_name=candidate.name,
            role_applied=candidate.role_applied,
            scheduled_at=when,
            interview_type=interview_type,
            location_or_link=location_or_link,
            notes=notes,
            updated=updated,
        )
        await self._send_safe(candidate.email, candidate_subject, candidate_html)

        if reviewer_email:
            reviewer_subject = reviewer_interview_email_subject(candidate.name, updated=updated)
            reviewer_html = reviewer_interview_email_body(
                reviewer_name=reviewer_name or reviewer_email.split("@")[0],
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                role_applied=candidate.role_applied,
                scheduled_at=when,
                interview_type=interview_type,
                location_or_link=location_or_link,
                notes=notes,
                updated=updated,
            )
            await self._send_safe(reviewer_email, reviewer_subject, reviewer_html)

    def _is_enabled(self) -> bool:
        """Return True when outbound email is configured."""
        if not self._settings.email_enabled:
            logger.info("Email disabled (EMAIL_ENABLED=false).")
            return False
        if not self._settings.smtp_host:
            logger.warning("EMAIL_ENABLED=true but SMTP_HOST is empty; skipping email.")
            return False
        return True

    def _resolve_from_address(self) -> str:
        """Pick a From address compatible with the SMTP provider."""
        configured = (self._settings.smtp_from or "").strip()
        user = (self._settings.smtp_user or "").strip()
        if user and "gmail" in self._settings.smtp_host.lower():
            if configured and configured != user:
                logger.warning(
                    "Gmail requires SMTP_FROM to match SMTP_USER; using %s instead of %s.",
                    user,
                    configured,
                )
            return user
        return configured or user or "noreply@techkraft.com"

    async def _send_safe(self, to_address: str, subject: str, html_body: str) -> None:
        """Send email and log failures without raising."""
        try:
            await asyncio.to_thread(self._send_smtp, to_address, subject, html_body)
        except Exception:
            logger.exception("Failed to send email to %s (subject: %s)", to_address, subject)

    def _send_smtp(self, to_address: str, subject: str, html_body: str) -> None:
        """Deliver an HTML email via SMTP (blocking)."""
        from_address = self._resolve_from_address()
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_address
        message["To"] = to_address
        message.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=15) as server:
            if self._settings.smtp_use_tls:
                server.starttls()
            if self._settings.smtp_user:
                server.login(self._settings.smtp_user, self._settings.smtp_password)
            server.sendmail(from_address, [to_address], message.as_string())

        logger.info("Email sent to %s (subject: %s)", to_address, subject)
