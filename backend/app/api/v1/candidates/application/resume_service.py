"""Resume file storage for candidate applications."""

import re
from pathlib import Path

from fastapi import UploadFile

from app.config import Settings

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_RESUME_BYTES = 5 * 1024 * 1024


class ResumeService:
    """Stores and resolves resume files on disk."""

    def __init__(self, settings: Settings) -> None:
        self._upload_root = Path(settings.upload_dir) / "resumes"

    def _candidate_dir(self, candidate_id: str) -> Path:
        """Return the storage directory for a candidate's resume."""
        path = self._upload_root / candidate_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _safe_filename(self, filename: str) -> str:
        """Normalize an uploaded filename to a safe basename."""
        cleaned = re.sub(r"[^\w.\-]", "_", Path(filename).name)
        return cleaned[:200] or "resume.pdf"

    async def save_resume(self, candidate_id: str, upload: UploadFile) -> str:
        """Persist an uploaded resume and return the stored filename.

        Raises:
            ValueError: When the file type or size is invalid.
        """
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_RESUME_EXTENSIONS:
            raise ValueError("Resume must be PDF, DOC, or DOCX.")

        content = await upload.read()
        if len(content) > MAX_RESUME_BYTES:
            raise ValueError("Resume must be 5 MB or smaller.")

        filename = self._safe_filename(upload.filename or f"resume{suffix}")
        destination = self._candidate_dir(candidate_id) / filename
        destination.write_bytes(content)
        return filename

    def resolve_resume_path(self, candidate_id: str, filename: str) -> Path | None:
        """Return the absolute resume path when the file exists."""
        path = self._candidate_dir(candidate_id) / filename
        return path if path.is_file() else None
