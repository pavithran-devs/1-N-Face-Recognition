"""Repository for the Candidate model."""

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    model = Candidate

    # ── Lookup helpers ────────────────────────────────────────────────────────

    async def get_by_candidate_id(self, candidate_id: str) -> Candidate | None:
        result = await self._session.execute(
            select(Candidate)
            .where(Candidate.candidate_id == candidate_id)
            .options(selectinload(Candidate.embeddings))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Candidate | None:
        result = await self._session.execute(
            select(Candidate)
            .where(Candidate.email == email)
            .options(selectinload(Candidate.embeddings))
        )
        return result.scalar_one_or_none()

    # ── Search ────────────────────────────────────────────────────────────────

    async def search_by_name(
        self, query: str, offset: int = 0, limit: int = 100
    ) -> list[Candidate]:
        """Case-insensitive name search using ILIKE."""
        result = await self._session.execute(
            select(Candidate)
            .where(Candidate.name.ilike(f"%{query}%"))
            .options(selectinload(Candidate.embeddings))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_candidate_id(
        self, query: str, offset: int = 0, limit: int = 100
    ) -> list[Candidate]:
        """Case-insensitive candidate_id search."""
        result = await self._session.execute(
            select(Candidate)
            .where(Candidate.candidate_id.ilike(f"%{query}%"))
            .options(selectinload(Candidate.embeddings))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_count(self, query: str, field: str = "name") -> int:
        """Return count for a search query on the given field."""
        column = Candidate.name if field == "name" else Candidate.candidate_id
        result = await self._session.execute(
            select(func.count()).select_from(Candidate).where(column.ilike(f"%{query}%"))
        )
        return result.scalar_one()

    async def exists_by_candidate_id(self, candidate_id: str) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(Candidate)
            .where(Candidate.candidate_id == candidate_id)
        )
        return result.scalar_one() > 0

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(func.count()).select_from(Candidate).where(Candidate.email == email)
        )
        return result.scalar_one() > 0
