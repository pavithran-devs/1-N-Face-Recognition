"""CandidateService — business logic for candidate CRUD."""
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.candidate import Candidate
from app.repositories.candidate import CandidateRepository
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.schemas.common import PaginationMeta


class CandidateService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CandidateRepository(session)

    async def create(self, data: CandidateCreate) -> Candidate:
        if await self._repo.exists_by_candidate_id(data.candidate_id):
            raise ConflictError(
                f"Candidate with candidate_id '{data.candidate_id}' already exists."
            )
        if await self._repo.exists_by_email(data.email):
            raise ConflictError(
                f"Candidate with email '{data.email}' already exists."
            )
        return await self._repo.create(
            candidate_id=data.candidate_id,
            name=data.name,
            email=data.email,
            dob=data.dob,
        )

    async def get_by_id(self, candidate_id: uuid.UUID) -> Candidate:
        candidate = await self._repo.get_by_id(candidate_id)
        if candidate is None:
            raise NotFoundError(f"Candidate {candidate_id} not found.")
        return candidate

    async def get_by_candidate_id(self, candidate_id: str) -> Candidate:
        candidate = await self._repo.get_by_candidate_id(candidate_id)
        if candidate is None:
            raise NotFoundError(f"Candidate '{candidate_id}' not found.")
        return candidate

    async def list_all(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[list[Candidate], PaginationMeta]:
        total = await self._repo.get_total_count()
        items = await self._repo.get_all(offset=offset, limit=limit)
        meta = PaginationMeta(
            total=total,
            offset=offset,
            limit=limit,
            has_next=(offset + limit) < total,
            has_prev=offset > 0,
        )
        return items, meta

    async def search(
        self, query: str, field: str = "name", offset: int = 0, limit: int = 100
    ) -> tuple[list[Candidate], PaginationMeta]:
        if field == "name":
            items = await self._repo.search_by_name(query, offset=offset, limit=limit)
        else:
            items = await self._repo.search_by_candidate_id(query, offset=offset, limit=limit)
        total = await self._repo.search_count(query, field=field)
        meta = PaginationMeta(
            total=total, offset=offset, limit=limit,
            has_next=(offset + limit) < total, has_prev=offset > 0,
        )
        return items, meta

    async def update(self, candidate_id: uuid.UUID, data: CandidateUpdate) -> Candidate:
        changes = data.model_dump(exclude_none=True)
        if not changes:
            return await self.get_by_id(candidate_id)
        # Check email uniqueness if it's being changed
        if "email" in changes:
            existing = await self._repo.get_by_email(changes["email"])
            if existing and existing.id != candidate_id:
                raise ConflictError(f"Email '{changes['email']}' is already in use.")
        updated = await self._repo.update(candidate_id, **changes)
        if updated is None:
            raise NotFoundError(f"Candidate {candidate_id} not found.")
        return updated

    async def delete(self, candidate_id: uuid.UUID) -> None:
        deleted = await self._repo.delete(candidate_id)
        if not deleted:
            raise NotFoundError(f"Candidate {candidate_id} not found.")
