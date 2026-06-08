"""SQLAlchemy implementation of the candidate repository."""

from app.shared.time import utc_now

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.domain.candidate import CandidateAggregate, CandidateFilters, WorkExperienceEntry
from app.db.models.candidate import CandidateModel
from app.shared.base_repository import AbstractRepository


class CandidateRepository(AbstractRepository[CandidateAggregate]):
    """Persists and retrieves candidate aggregates via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: str) -> CandidateAggregate | None:
        """Return the active candidate with the given identifier or None."""
        statement = select(CandidateModel).where(
            CandidateModel.id == entity_id,
            CandidateModel.deleted_at.is_(None),
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def save(self, entity: CandidateAggregate) -> CandidateAggregate:
        """Persist candidate changes and return the saved aggregate."""
        model = await self._session.get(CandidateModel, entity.id)
        if model is None:
            raise ValueError(f"Candidate not found: {entity.id}")
        model.name = entity.name
        model.email = entity.email
        model.role_applied = entity.role_applied
        model.status = entity.status
        model.skills = entity.skills
        model.description = entity.description
        model.work_experience = [self._experience_to_dict(entry) for entry in entity.work_experience]
        model.internal_notes = entity.internal_notes
        model.ai_summary = entity.ai_summary
        await self._session.flush()
        return self._to_entity(model)

    async def list_filtered(self, filters: CandidateFilters) -> tuple[list[CandidateAggregate], int]:
        """Return candidates and total count matching SQL-level filters."""
        where_clause = self._build_filter_clause(filters)
        count_statement = select(func.count()).select_from(CandidateModel).where(where_clause)
        total = await self._session.scalar(count_statement) or 0
        data_statement = (
            select(CandidateModel)
            .where(where_clause)
            .order_by(CandidateModel.created_at.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )
        result = await self._session.execute(data_statement)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models], total

    async def soft_delete(self, entity_id: str) -> None:
        """Mark a candidate as deleted without removing the database row."""
        model = await self._session.get(CandidateModel, entity_id)
        if model is None or model.deleted_at is not None:
            return
        model.deleted_at = utc_now()
        await self._session.flush()

    async def update_ai_summary(self, entity_id: str, summary: str) -> CandidateAggregate | None:
        """Persist an AI-generated summary for the candidate."""
        model = await self._session.get(CandidateModel, entity_id)
        if model is None or model.deleted_at is not None:
            return None
        model.ai_summary = summary
        await self._session.flush()
        return self._to_entity(model)

    def _build_filter_clause(self, filters: CandidateFilters):
        """Compose SQL WHERE clauses for candidate filtering."""
        clauses = [CandidateModel.deleted_at.is_(None)]
        if filters.status is not None:
            clauses.append(CandidateModel.status == filters.status)
        if filters.role_applied:
            clauses.append(CandidateModel.role_applied.ilike(f"%{filters.role_applied}%"))
        if filters.skill:
            clauses.append(CandidateModel.skills.contains([filters.skill]))
        if filters.keyword:
            pattern = f"%{filters.keyword}%"
            clauses.append(or_(CandidateModel.name.ilike(pattern), CandidateModel.email.ilike(pattern)))
        return and_(*clauses)

    def _to_entity(self, model: CandidateModel) -> CandidateAggregate:
        """Map an ORM row to a domain aggregate without scores."""
        return CandidateAggregate(
            id=model.id,
            name=model.name,
            email=model.email,
            role_applied=model.role_applied,
            status=model.status,
            skills=list(model.skills or []),
            description=model.description,
            work_experience=self._parse_work_experience(model.work_experience),
            internal_notes=model.internal_notes,
            ai_summary=model.ai_summary,
            created_at=model.created_at,
        )

    def _parse_work_experience(self, raw: list | None) -> tuple[WorkExperienceEntry, ...]:
        """Map stored JSON work history to domain entries."""
        if not raw:
            return ()
        entries: list[WorkExperienceEntry] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            entries.append(
                WorkExperienceEntry(
                    company=str(item.get("company", "")),
                    title=str(item.get("title", "")),
                    start=str(item.get("start", "")),
                    end=item.get("end"),
                    summary=item.get("summary"),
                )
            )
        return tuple(entries)

    def _experience_to_dict(self, entry: WorkExperienceEntry) -> dict:
        """Serialize a work experience entry for JSON storage."""
        return {
            "company": entry.company,
            "title": entry.title,
            "start": entry.start,
            "end": entry.end,
            "summary": entry.summary,
        }
