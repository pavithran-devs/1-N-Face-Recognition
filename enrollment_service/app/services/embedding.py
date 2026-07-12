"""EmbeddingService — generate and regenerate face embeddings."""
import uuid

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, QualityCheckError
from app.exceptions import PipelineError as PipelineAppError
from app.models.face_embedding import FaceEmbedding
from app.recognition.pipeline import FaceRecognitionPipeline, PipelineError
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.utils.imaging import bytes_to_bgr


class EmbeddingService:
    def __init__(
        self, session: AsyncSession, pipeline: FaceRecognitionPipeline
    ) -> None:
        self._emb_repo = EmbeddingRepository(session)
        self._cand_repo = CandidateRepository(session)
        self._pipeline = pipeline

    async def generate(
        self, candidate_uuid: uuid.UUID, image_bytes: bytes
    ) -> FaceEmbedding:
        """Generate and persist an embedding for an existing candidate."""
        candidate = await self._cand_repo.get_by_id(candidate_uuid)
        if candidate is None:
            raise NotFoundError(f"Candidate {candidate_uuid} not found.")

        image = bytes_to_bgr(image_bytes)
        result = self._pipeline.process(image)

        if isinstance(result, PipelineError):
            raise QualityCheckError(
                result.message,
                quality_code=result.quality.code.value,
            )

        return await self._emb_repo.create(
            candidate_uuid=candidate_uuid,
            embedding=result.embedding.tolist(),
            embedding_dimension=result.embedding_dim,
            model_name=result.model_name,
            normalized=result.normalized,
        )

    async def regenerate(
        self, candidate_uuid: uuid.UUID, image_bytes: bytes
    ) -> FaceEmbedding:
        """Delete all existing embeddings for a candidate, then generate a new one."""
        deleted = await self._emb_repo.delete_by_candidate_uuid(candidate_uuid)
        return await self.generate(candidate_uuid, image_bytes)

    async def get_embeddings(self, candidate_uuid: uuid.UUID) -> list[FaceEmbedding]:
        return await self._emb_repo.get_by_candidate_uuid(candidate_uuid)
