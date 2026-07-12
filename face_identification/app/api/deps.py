"""FastAPI Dependency Injection helpers."""

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db_session
from app.faiss.manager import FAISSManager
from app.recognition.pipeline import FaceRecognitionPipeline
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.services.import_ import ImportService


def get_faiss_manager() -> FAISSManager:
    """Returns the singleton FAISS index manager."""
    return FAISSManager()


def get_pipeline(request: Request) -> FaceRecognitionPipeline:
    """Returns the pre-warmed face recognition pipeline from application state."""
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        raise RuntimeError("FaceRecognitionPipeline is not loaded in application state.")
    return pipeline


def get_candidate_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CandidateRepository:
    """Returns a CandidateRepository instance."""
    return CandidateRepository(session)


def get_embedding_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EmbeddingRepository:
    """Returns an EmbeddingRepository instance."""
    return EmbeddingRepository(session)


def get_import_service(session: AsyncSession = Depends(get_db_session)) -> ImportService:
    """Returns an ImportService instance."""
    return ImportService(session)
