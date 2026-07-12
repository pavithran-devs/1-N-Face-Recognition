"""Unit tests for CandidateService using in-memory SQLite."""
import pytest

from app.exceptions import ConflictError, NotFoundError
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.services.candidate import CandidateService


async def _svc(session) -> CandidateService:
    return CandidateService(session)


async def _enroll(session, candidate_id: str = "EMP001") -> object:
    svc = await _svc(session)
    return await svc.create(
        CandidateCreate(candidate_id=candidate_id, name="Alice", email=f"{candidate_id}@test.com")
    )


class TestCandidateService:
    @pytest.mark.asyncio
    async def test_create(self, db_session):
        svc = await _svc(db_session)
        c = await svc.create(CandidateCreate(
            candidate_id="EMP001", name="Alice", email="alice@test.com"
        ))
        assert c.candidate_id == "EMP001"

    @pytest.mark.asyncio
    async def test_duplicate_candidate_id_raises(self, db_session):
        await _enroll(db_session, "EMP001")
        svc = await _svc(db_session)
        with pytest.raises(ConflictError):
            await svc.create(CandidateCreate(
                candidate_id="EMP001", name="Bob", email="bob@test.com"
            ))

    @pytest.mark.asyncio
    async def test_duplicate_email_raises(self, db_session):
        await _enroll(db_session, "EMP001")
        svc = await _svc(db_session)
        with pytest.raises(ConflictError):
            await svc.create(CandidateCreate(
                candidate_id="EMP002", name="Bob", email="EMP001@test.com"
            ))

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        c = await _enroll(db_session)
        svc = await _svc(db_session)
        found = await svc.get_by_id(c.id)
        assert found.id == c.id

    @pytest.mark.asyncio
    async def test_not_found_raises(self, db_session):
        import uuid
        svc = await _svc(db_session)
        with pytest.raises(NotFoundError):
            await svc.get_by_id(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_update(self, db_session):
        c = await _enroll(db_session)
        svc = await _svc(db_session)
        updated = await svc.update(c.id, CandidateUpdate(name="Updated Name"))
        assert updated.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        import uuid
        c = await _enroll(db_session)
        svc = await _svc(db_session)
        await svc.delete(c.id)
        with pytest.raises(NotFoundError):
            await svc.get_by_id(c.id)

    @pytest.mark.asyncio
    async def test_list_all(self, db_session):
        for i in range(3):
            await _enroll(db_session, f"EMP{i:03d}")
        svc = await _svc(db_session)
        items, meta = await svc.list_all()
        assert meta.total == 3
        assert len(items) == 3

    @pytest.mark.asyncio
    async def test_search(self, db_session):
        await _enroll(db_session, "EMP001")
        svc = await _svc(db_session)
        results, meta = await svc.search("Alice", field="name")
        assert meta.total >= 1
