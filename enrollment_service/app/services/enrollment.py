"""EnrollmentService — orchestrates full candidate + embedding enrollment."""
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, ImageValidationError, QualityCheckError
from app.exceptions import PipelineError as PipelineAppError
from app.models.candidate import Candidate
from app.models.face_embedding import FaceEmbedding
from app.recognition.pipeline import FaceRecognitionPipeline, PipelineError
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.schemas.candidate import CandidateCreate
from app.utils.imaging import base64_to_bgr, bytes_to_bgr
from app.validators.image import validate_image_bytes


@dataclass
class EnrollmentResult:
    candidate: Candidate
    embedding: FaceEmbedding
    quality_code: str
    timings: dict[str, float]


class EnrollmentService:
    def __init__(
        self, session: AsyncSession, pipeline: FaceRecognitionPipeline
    ) -> None:
        self._cand_repo = CandidateRepository(session)
        self._emb_repo = EmbeddingRepository(session)
        self._pipeline = pipeline

    async def enroll_from_bytes(
        self, image_bytes: bytes, candidate_data: CandidateCreate
    ) -> EnrollmentResult:
        """
        Full enrollment from raw image bytes (file upload).
        Steps: validate image → check uniqueness → run pipeline → persist.
        """
        # 1. Validate image
        validate_image_bytes(image_bytes)

        # 2. Check for duplicates
        if await self._cand_repo.exists_by_candidate_id(candidate_data.candidate_id):
            raise ConflictError(
                f"Candidate '{candidate_data.candidate_id}' already enrolled."
            )
        if await self._cand_repo.exists_by_email(candidate_data.email):
            raise ConflictError(
                f"Email '{candidate_data.email}' already enrolled."
            )

        # 3. Run recognition pipeline
        try:
            image = bytes_to_bgr(image_bytes)
        except ValueError as exc:
            raise ImageValidationError(f"Could not decode image bytes: {exc}") from exc

        try:
            result = self._pipeline.process(image)
        except RuntimeError as exc:
            raise PipelineAppError(f"Recognition pipeline is not ready: {exc}") from exc

        if isinstance(result, PipelineError):
            raise QualityCheckError(
                result.message,
                quality_code=result.quality.code.value,
            )

        # 4. Persist candidate
        candidate = await self._cand_repo.create(
            candidate_id=candidate_data.candidate_id,
            name=candidate_data.name,
            email=candidate_data.email,
            dob=candidate_data.dob,
        )

        # 5. Persist embedding
        embedding = await self._emb_repo.create(
            candidate_uuid=candidate.id,
            embedding=result.embedding.tolist(),
            embedding_dimension=result.embedding_dim,
            model_name=result.model_name,
            normalized=result.normalized,
        )

        return EnrollmentResult(
            candidate=candidate,
            embedding=embedding,
            quality_code=result.quality.code.value,
            timings=result.timings,
        )

    async def enroll_from_base64(
        self, image_b64: str, candidate_data: CandidateCreate
    ) -> EnrollmentResult:
        """Full enrollment from a base64 image (webcam capture)."""
        import base64 as _b64
        import binascii
        # Strip data URI header if present
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        try:
            image_bytes = _b64.b64decode(image_b64)
        except (binascii.Error, ValueError) as exc:
            raise ImageValidationError(
                f"Invalid base64 image data: {exc}"
            ) from exc
        return await self.enroll_from_bytes(image_bytes, candidate_data)
