"""SQLAlchemy implementation of the score repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.domain.score import ScoreEntity
from app.db.models.score import ScoreModel
from app.shared.base_repository import AbstractRepository


class ScoreRepository(AbstractRepository[ScoreEntity]):
    """Persists and retrieves score entities via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: str) -> ScoreEntity | None:
        """Return the score with the given identifier or None."""
        model = await self._session.get(ScoreModel, entity_id)
        if model is None:
            return None
        return self._to_entity(model)

    async def find_by_candidate_id(self, candidate_id: str) -> list[ScoreEntity]:
        """Return all scores for the given candidate ordered by newest first."""
        statement = (
            select(ScoreModel)
            .where(ScoreModel.candidate_id == candidate_id)
            .order_by(ScoreModel.created_at.desc())
        )
        result = await self._session.execute(statement)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def save(self, entity: ScoreEntity) -> ScoreEntity:
        """Persist the score and return the saved entity."""
        model = await self._session.get(ScoreModel, entity.id)
        if model is None:
            model = ScoreModel(
                id=entity.id,
                candidate_id=entity.candidate_id,
                category=entity.category,
                score=entity.score,
                reviewer_id=entity.reviewer_id,
                note=entity.note,
                created_at=entity.created_at,
            )
            self._session.add(model)
        else:
            model.category = entity.category
            model.score = entity.score
            model.reviewer_id = entity.reviewer_id
            model.note = entity.note
        await self._session.flush()
        return self._to_entity(model)

    def _to_entity(self, model: ScoreModel) -> ScoreEntity:
        """Map an ORM row to a domain entity."""
        return ScoreEntity(
            id=model.id,
            candidate_id=model.candidate_id,
            category=model.category,
            score=model.score,
            reviewer_id=model.reviewer_id,
            note=model.note,
            created_at=model.created_at,
        )
