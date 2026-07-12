"""Unit tests for CandidateRepository and EmbeddingRepository using in-memory SQLite."""
import uuid

import pytest
import pytest_asyncio

from app.models.candidate import Candidate
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository


async def _create_candidate(session, candidate_id: str = "EMP001") -> Candidate:
    repo = CandidateRepository(session)
    return await repo.create(
        candidate_id=candidate_id,
        name="Alice Smith",
        email=f"{candidate_id}@example.com",
    )


class TestCandidateRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session):
        c = await _create_candidate(db_session)
        repo = CandidateRepository(db_session)
        fetched = await repo.get_by_id(c.id)
        assert fetched is not None
        assert fetched.candidate_id == "EMP001"

    @pytest.mark.asyncio
    async def test_get_by_candidate_id(self, db_session):
        await _create_candidate(db_session)
        repo = CandidateRepository(db_session)
        found = await repo.get_by_candidate_id("EMP001")
        assert found is not None

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self, db_session):
        repo = CandidateRepository(db_session)
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_exists_by_candidate_id(self, db_session):
        await _create_candidate(db_session)
        repo = CandidateRepository(db_session)
        assert await repo.exists_by_candidate_id("EMP001") is True
        assert await repo.exists_by_candidate_id("UNKNOWN") is False

    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session):
        await _create_candidate(db_session, "EMP001")
        await _create_candidate(db_session, "EMP002")
        repo = CandidateRepository(db_session)
        results = await repo.search_by_name("Alice")
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_update(self, db_session):
        c = await _create_candidate(db_session)
        repo = CandidateRepository(db_session)
        updated = await repo.update(c.id, name="Bob Jones")
        assert updated is not None
        assert updated.name == "Bob Jones"

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        c = await _create_candidate(db_session)
        repo = CandidateRepository(db_session)
        deleted = await repo.delete(c.id)
        assert deleted is True
        assert await repo.get_by_id(c.id) is None

    @pytest.mark.asyncio
    async def test_pagination(self, db_session):
        for i in range(5):
            await _create_candidate(db_session, f"EMP{i:03d}")
        repo = CandidateRepository(db_session)
        page1 = await repo.get_all(offset=0, limit=3)
        page2 = await repo.get_all(offset=3, limit=3)
        assert len(page1) == 3
        assert len(page2) == 2


class TestEmbeddingRepository:
    @pytest.mark.asyncio
    async def test_create_and_get_by_candidate(self, db_session):
        c = await _create_candidate(db_session)
        repo = EmbeddingRepository(db_session)
        emb = await repo.create(
            candidate_uuid=c.id,
            embedding=[0.1] * 512,
            embedding_dimension=512,
            model_name="buffalo_l",
            normalized=True,
        )
        results = await repo.get_by_candidate_uuid(c.id)
        assert len(results) == 1
        assert results[0].id == emb.id

    @pytest.mark.asyncio
    async def test_delete_by_candidate(self, db_session):
        c = await _create_candidate(db_session)
        repo = EmbeddingRepository(db_session)
        await repo.create(
            candidate_uuid=c.id, embedding=[0.1] * 512,
            embedding_dimension=512, model_name="buffalo_l", normalized=True,
        )
        deleted = await repo.delete_by_candidate_uuid(c.id)
        assert deleted == 1
        remaining = await repo.get_by_candidate_uuid(c.id)
        assert len(remaining) == 0
