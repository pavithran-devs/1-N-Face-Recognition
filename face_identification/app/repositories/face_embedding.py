"""Repository for the FaceEmbedding model."""

from uuid import UUID

from sqlalchemy import delete, select

from app.models.face_embedding import FaceEmbedding
from app.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[FaceEmbedding]):
    model = FaceEmbedding

    async def get_by_candidate_uuid(self, candidate_uuid: UUID) -> list[FaceEmbedding]:
        """Return all embeddings belonging to a candidate."""
        result = await self._session.execute(
            select(FaceEmbedding).where(FaceEmbedding.candidate_uuid == candidate_uuid)
        )
        return list(result.scalars().all())

    async def get_latest_by_candidate_uuid(self, candidate_uuid: UUID) -> FaceEmbedding | None:
        """Return the most recently created embedding for a candidate."""
        result = await self._session.execute(
            select(FaceEmbedding)
            .where(FaceEmbedding.candidate_uuid == candidate_uuid)
            .order_by(FaceEmbedding.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def delete_by_candidate_uuid(self, candidate_uuid: UUID) -> int:
        """Delete all embeddings for a candidate. Returns the count deleted."""
        result = await self._session.execute(
            delete(FaceEmbedding).where(FaceEmbedding.candidate_uuid == candidate_uuid)
        )
        await self._session.flush()
        return result.rowcount  # type: ignore[return-value]

    async def count_by_candidate_uuid(self, candidate_uuid: UUID) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(FaceEmbedding)
            .where(FaceEmbedding.candidate_uuid == candidate_uuid)
        )
        return result.scalar_one()
