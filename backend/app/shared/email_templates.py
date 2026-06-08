"""HTML email templates for candidate status and interview notifications."""

from app.api.v1.candidates.domain.enums import CandidateStatus

BRAND = {
    "bg": "#0f0f1a",
    "card": "#1a1a2e",
    "card_border": "#2d2d4a",
    "text": "#f4f4f8",
    "muted": "#9ca3af",
    "accent": "#818cf8",
    "accent_dark": "#6366f1",
    "success": "#34d399",
    "danger": "#f87171",
    "warning": "#fbbf24",
}


def _email_layout(
    *,
    headline: str,
    badge: str,
    badge_color: str,
    body_html: str,
    footer_note: str = "TechKraft Recruiting · Automated notification",
) -> str:
    """Wrap content in a branded HTML email shell (inline styles for clients)."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{BRAND['bg']};font-family:'Segoe UI',Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:{BRAND['bg']};">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;">
          <tr>
            <td style="padding-bottom:20px;text-align:center;">
              <span style="font-size:11px;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;color:{BRAND['accent']};">TechKraft</span>
              <span style="display:block;margin-top:4px;font-size:22px;font-weight:800;color:{BRAND['text']};">Recruit</span>
            </td>
          </tr>
          <tr>
            <td style="background:{BRAND['card']};border:1px solid {BRAND['card_border']};border-radius:16px;padding:32px 28px;">
              <span style="display:inline-block;margin-bottom:16px;padding:6px 12px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#fff;background:{badge_color};">{badge}</span>
              <h1 style="margin:0 0 20px;font-size:22px;font-weight:800;line-height:1.3;color:{BRAND['text']};">{headline}</h1>
              <div style="font-size:15px;line-height:1.7;color:{BRAND['muted']};">{body_html}</div>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 8px 0;text-align:center;font-size:12px;line-height:1.5;color:#6b7280;">{footer_note}</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _detail_row(label: str, value: str) -> str:
    """Render a labeled detail row for email bodies."""
    return (
        f'<p style="margin:0 0 12px;"><span style="color:{BRAND["muted"]};">{label}</span><br>'
        f'<strong style="color:{BRAND["text"]};">{value}</strong></p>'
    )


def status_email_subject(status: CandidateStatus, candidate_name: str) -> str:
    """Return the email subject for a status change."""
    if status == CandidateStatus.HIRED:
        return f"TechKraft Recruit — Offer extended for {candidate_name}"
    if status == CandidateStatus.REJECTED:
        return "TechKraft Recruit — Update on your application"
    if status == CandidateStatus.REVIEWED:
        return "TechKraft Recruit — Your application is under review"
    return f"TechKraft Recruit — Application update for {candidate_name}"


def status_email_body(
    *,
    candidate_name: str,
    role_applied: str,
    status: CandidateStatus,
) -> str:
    """Return a branded HTML body for a status notification."""
    if status == CandidateStatus.HIRED:
        badge, badge_color = "Offer extended", BRAND["success"]
        headline = f"Congratulations, {candidate_name}!"
        body = (
            f"<p style=\"margin:0 0 16px;\">We are pleased to extend an offer for the "
            f"<strong style=\"color:{BRAND['text']};\">{role_applied}</strong> role at TechKraft.</p>"
            f"<p style=\"margin:0;\">Our recruiting team will reach out shortly with offer details and next steps.</p>"
        )
    elif status == CandidateStatus.REJECTED:
        badge, badge_color = "Application update", BRAND["danger"]
        headline = "Thank you for applying"
        body = (
            f"<p style=\"margin:0 0 16px;\">Thank you for your interest in the "
            f"<strong style=\"color:{BRAND['text']};\">{role_applied}</strong> position.</p>"
            f"<p style=\"margin:0;\">After careful review, we will not be moving forward with your application "
            f"at this time. We encourage you to apply for future roles that match your experience.</p>"
        )
    elif status == CandidateStatus.REVIEWED:
        badge, badge_color = "Under review", BRAND["accent_dark"]
        headline = f"Hi {candidate_name}, your application is in review"
        body = (
            f"<p style=\"margin:0 0 16px;\">Your application for "
            f"<strong style=\"color:{BRAND['text']};\">{role_applied}</strong> has moved to the review stage.</p>"
            f"<p style=\"margin:0;\">Our hiring team is evaluating your profile. We will contact you if we need "
            f"additional information or to schedule next steps.</p>"
        )
    else:
        badge, badge_color = "Update", BRAND["warning"]
        headline = f"Application update for {candidate_name}"
        body = f"<p style=\"margin:0;\">There is a new update on your application for <strong>{role_applied}</strong>.</p>"

    return _email_layout(headline=headline, badge=badge, badge_color=badge_color, body_html=body)


def interview_email_subject(candidate_name: str, *, updated: bool = False) -> str:
    """Return the subject for an interview invitation or reschedule."""
    action = "Interview updated" if updated else "Interview scheduled"
    return f"TechKraft Recruit — {action} for {candidate_name}"


def interview_email_body(
    *,
    candidate_name: str,
    role_applied: str,
    scheduled_at: str,
    interview_type: str,
    location_or_link: str | None,
    notes: str | None,
    updated: bool = False,
) -> str:
    """Return branded HTML for an interview invitation or update."""
    type_label = interview_type.replace("_", " ").title()
    badge = "Interview updated" if updated else "Interview scheduled"
    headline = f"{'Updated' if updated else 'New'} interview — {role_applied}"

    body = (
        f"<p style=\"margin:0 0 20px;\">Hi <strong style=\"color:{BRAND['text']};\">{candidate_name}</strong>, "
        f"your interview for <strong style=\"color:{BRAND['text']};\">{role_applied}</strong> "
        f"{'has been updated' if updated else 'has been scheduled'}.</p>"
        f"{_detail_row('When', scheduled_at)}"
        f"{_detail_row('Format', type_label)}"
    )
    if location_or_link:
        body += _detail_row("Location / link", location_or_link)
    if notes:
        body += _detail_row("Notes", notes)
    body += (
        f'<p style="margin:16px 0 0;padding:14px 16px;border-radius:10px;'
        f'background:#141424;border:1px solid {BRAND["card_border"]};color:{BRAND["muted"]};">'
        f"Reply to this email if you need to reschedule.</p>"
    )

    return _email_layout(
        headline=headline,
        badge=badge,
        badge_color=BRAND["accent_dark"],
        body_html=body,
    )


def reviewer_interview_email_subject(candidate_name: str, *, updated: bool = False) -> str:
    """Return the subject for a reviewer assignment email."""
    action = "Interview updated" if updated else "New interview"
    return f"TechKraft Recruit — {action}: {candidate_name}"


def reviewer_interview_email_body(
    *,
    reviewer_name: str,
    candidate_name: str,
    candidate_email: str,
    role_applied: str,
    scheduled_at: str,
    interview_type: str,
    location_or_link: str | None,
    notes: str | None,
    updated: bool = False,
) -> str:
    """Return branded HTML for interviewer assignment."""
    type_label = interview_type.replace("_", " ").title()
    badge = "Assignment updated" if updated else "New assignment"
    headline = f"{'Updated' if updated else 'Scheduled'} interview — {candidate_name}"

    body = (
        f"<p style=\"margin:0 0 20px;\">Hi <strong style=\"color:{BRAND['text']};\">{reviewer_name}</strong>, "
        f"you are assigned to interview <strong style=\"color:{BRAND['text']};\">{candidate_name}</strong> "
        f"for the <strong style=\"color:{BRAND['text']};\">{role_applied}</strong> role.</p>"
        f"{_detail_row('Candidate email', candidate_email)}"
        f"{_detail_row('When', scheduled_at)}"
        f"{_detail_row('Format', type_label)}"
    )
    if location_or_link:
        body += _detail_row("Location / link", location_or_link)
    if notes:
        body += _detail_row("Notes", notes)
    body += (
        f'<p style="margin:16px 0 0;padding:14px 16px;border-radius:10px;'
        f'background:#141424;border:1px solid {BRAND["card_border"]};color:{BRAND["muted"]};">'
        f"Log in to the TechKraft dashboard to view the full candidate profile.</p>"
    )

    return _email_layout(
        headline=headline,
        badge=badge,
        badge_color=BRAND["success"],
        body_html=body,
    )
