"""Unit tests for Candidate and Embedding Repositories."""

import datetime

import pytest

from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository

pytestmark = pytest.mark.asyncio


async def test_candidate_repository_crud(db_session) -> None:
    repo = CandidateRepository(db_session)

    # 1. Create
    candidate = await repo.create(
        candidate_id="CAND010",
        name="Logan",
        email="logan@xmen.com",
        dob=datetime.date(1975, 4, 12),
    )
    assert candidate.id is not None
    assert candidate.name == "Logan"

    # 2. Get by ID
    fetched = await repo.get_by_id(candidate.id)
    assert fetched is not None
    assert fetched.candidate_id == "CAND010"

    # 3. Get by Candidate ID
    fetched_by_cid = await repo.get_by_candidate_id("CAND010")
    assert fetched_by_cid is not None
    assert fetched_by_cid.email == "logan@xmen.com"

    # 4. Search by Name
    search_res = await repo.search_by_name("log")
    assert len(search_res) == 1
    assert search_res[0].name == "Logan"

    # Search by Candidate ID
    search_by_cid = await repo.search_by_candidate_id("CAND010")
    assert len(search_by_cid) == 1
    assert search_by_cid[0].name == "Logan"

    # 5. Search Count
    cnt = await repo.search_count("log", field="name")
    assert cnt == 1
    cnt_cid = await repo.search_count("CAND", field="candidate_id")
    assert cnt_cid == 1

    # 6. Exists
    assert await repo.exists_by_candidate_id("CAND010") is True
    assert await repo.exists_by_email("logan@xmen.com") is True

    # 7. Update
    updated = await repo.update(candidate.id, name="Wolverine")
    assert updated is not None
    assert updated.name == "Wolverine"

    # 8. Delete
    deleted = await repo.delete(candidate.id)
    assert deleted is True
    assert await repo.get_by_id(candidate.id) is None


async def test_embedding_repository_crud(db_session) -> None:
    cand_repo = CandidateRepository(db_session)
    emb_repo = EmbeddingRepository(db_session)

    candidate = await cand_repo.create(
        candidate_id="CAND020",
        name="Jean Grey",
        email="jean@xmen.com",
    )

    # 1. Create embedding
    embedding = await emb_repo.create(
        candidate_uuid=candidate.id,
        embedding=[0.1] * 512,
        embedding_dimension=512,
        model_name="buffalo_l",
        normalized=True,
    )
    assert embedding.id is not None

    # 2. Get by candidate uuid
    embs = await emb_repo.get_by_candidate_uuid(candidate.id)
    assert len(embs) == 1
    assert embs[0].embedding == [0.1] * 512

    # 3. Count
    count = await emb_repo.count_by_candidate_uuid(candidate.id)
    assert count == 1

    # 4. Get latest
    latest = await emb_repo.get_latest_by_candidate_uuid(candidate.id)
    assert latest is not None
    assert latest.id == embedding.id

    # 5. Delete by candidate uuid
    del_count = await emb_repo.delete_by_candidate_uuid(candidate.id)
    assert del_count == 1
    assert await emb_repo.count_by_candidate_uuid(candidate.id) == 0
