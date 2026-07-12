"""Generic async repository base class."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):  # noqa: UP046
    """Generic CRUD repository using an injected AsyncSession."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **kwargs: Any) -> ModelT:
        """Persist a new record and return it."""
        instance = self.model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, record_id: UUID) -> ModelT | None:
        """Return a record by primary-key UUID, or None if not found."""
        result = await self._session.execute(
            select(self.model).where(self.model.id == record_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[ModelT]:
        """Return a paginated list of all records."""
        result = await self._session.execute(select(self.model).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        """Return the total number of records in the table."""
        result = await self._session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()

    async def update(self, record_id: UUID, **kwargs: Any) -> ModelT | None:
        """Update fields on an existing record; return the updated record or None."""
        instance = await self.get_by_id(record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, record_id: UUID) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        instance = await self.get_by_id(record_id)
        if instance is None:
            return False
        await self._session.delete(instance)
        await self._session.flush()
        return True
