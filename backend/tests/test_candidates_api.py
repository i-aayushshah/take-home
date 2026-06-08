"""Candidate API integration tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.candidates.domain.enums import CandidateStatus
from app.db.models.candidate import CandidateModel
from app.shared.time import utc_now
from tests.conftest import auth_headers, register_and_login


@pytest.mark.asyncio
async def test_get_candidate_detail_returns_expected_shape(
    client: AsyncClient,
    seeded_candidate: str,
) -> None:
    """Seeded candidate detail returns 200 with profile and score fields."""
    token = await register_and_login(client, "reviewer1@techkraft.com")
    response = await client.get(
        f"/api/v1/candidates/{seeded_candidate}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == seeded_candidate
    assert payload["name"] == "Test Candidate"
    assert payload["email"] == "candidate@example.com"
    assert payload["role_applied"] == "Backend Engineer"
    assert payload["status"] == "new"
    assert payload["skills"] == ["Python", "FastAPI"]
    assert payload["description"] == "Experienced backend engineer."
    assert len(payload["work_experience"]) == 1
    assert payload["internal_notes"] is None
    assert payload["scores"] == []


@pytest.mark.asyncio
async def test_reviewer_only_sees_own_scores(
    client: AsyncClient,
    seeded_candidate: str,
) -> None:
    """Reviewer B cannot see scores submitted by reviewer A."""
    token_a = await register_and_login(client, "reviewer.a@techkraft.com")
    token_b = await register_and_login(client, "reviewer.b@techkraft.com")

    submit = await client.post(
        f"/api/v1/candidates/{seeded_candidate}/scores",
        headers=auth_headers(token_a),
        json={"category": "technical", "score": 4, "note": "Strong Python"},
    )
    assert submit.status_code == 200

    detail_b = await client.get(
        f"/api/v1/candidates/{seeded_candidate}",
        headers=auth_headers(token_b),
    )
    assert detail_b.status_code == 200
    assert detail_b.json()["scores"] == []

    detail_a = await client.get(
        f"/api/v1/candidates/{seeded_candidate}",
        headers=auth_headers(token_a),
    )
    assert detail_a.status_code == 200
    assert len(detail_a.json()["scores"]) == 1
    assert detail_a.json()["scores"][0]["score"] == 4


@pytest.mark.asyncio
async def test_submit_score_persists_fields(
    client: AsyncClient,
    seeded_candidate: str,
) -> None:
    """Authenticated score submission persists category, score, and note."""
    token = await register_and_login(client, "scorer@techkraft.com")
    response = await client.post(
        f"/api/v1/candidates/{seeded_candidate}/scores",
        headers=auth_headers(token),
        json={"category": "communication", "score": 5, "note": "Clear communicator"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_id"] == seeded_candidate
    assert payload["category"] == "communication"
    assert payload["score"] == 5
    assert payload["note"] == "Clear communicator"
    assert payload["reviewer_id"]


@pytest.mark.asyncio
async def test_list_candidates_status_filter_uses_sql_total(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Filtered list total reflects SQL count, not client-side filtering."""
    async with session_factory() as session:
        session.add_all(
            [
                CandidateModel(
                    id=str(uuid.uuid4()),
                    name="New One",
                    email="new1@example.com",
                    role_applied="Engineer",
                    status=CandidateStatus.NEW,
                    skills=["Python"],
                    created_at=utc_now(),
                ),
                CandidateModel(
                    id=str(uuid.uuid4()),
                    name="New Two",
                    email="new2@example.com",
                    role_applied="Engineer",
                    status=CandidateStatus.NEW,
                    skills=["Go"],
                    created_at=utc_now(),
                ),
                CandidateModel(
                    id=str(uuid.uuid4()),
                    name="Reviewed One",
                    email="reviewed@example.com",
                    role_applied="Engineer",
                    status=CandidateStatus.REVIEWED,
                    skills=["Rust"],
                    created_at=utc_now(),
                ),
            ]
        )
        await session.commit()

    token = await register_and_login(client, "lister@techkraft.com")
    response = await client.get(
        "/api/v1/candidates?status=new&limit=1&offset=0",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["limit"] == 1
    assert payload["offset"] == 0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["status"] == "new"


@pytest.mark.asyncio
async def test_soft_deleted_candidate_returns_not_found(
    client: AsyncClient,
    seeded_candidate: str,
    admin_headers: dict[str, str],
) -> None:
    """Soft-deleted candidates are no longer returned in detail view."""
    delete_response = await client.delete(
        f"/api/v1/candidates/{seeded_candidate}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    token = await register_and_login(client, "viewer@techkraft.com")
    detail = await client.get(
        f"/api/v1/candidates/{seeded_candidate}",
        headers=auth_headers(token),
    )
    assert detail.status_code == 404
