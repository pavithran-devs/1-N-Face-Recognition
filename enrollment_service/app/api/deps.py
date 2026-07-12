"""
FastAPI dependency injection providers.

All service constructors receive an AsyncSession and (where needed) the pipeline
singleton that is stored on app.state at startup.
"""
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db_session
from app.recognition.pipeline import FaceRecognitionPipeline
from app.services.candidate import CandidateService
from app.services.embedding import EmbeddingService
from app.services.enrollment import EnrollmentService
from app.services.export import ExportService
from app.services.import_ import ImportService


# ── Database session ──────────────────────────────────────────────────────────

async def get_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AsyncSession, None]:
    yield session


# ── Pipeline singleton from app.state ─────────────────────────────────────────

def get_pipeline(request: Request) -> FaceRecognitionPipeline:
    pipeline: FaceRecognitionPipeline = request.app.state.pipeline
    return pipeline


# ── Service factories ─────────────────────────────────────────────────────────

def get_candidate_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CandidateService:
    return CandidateService(session)


def get_enrollment_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    pipeline: Annotated[FaceRecognitionPipeline, Depends(get_pipeline)],
) -> EnrollmentService:
    return EnrollmentService(session, pipeline)


def get_embedding_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    pipeline: Annotated[FaceRecognitionPipeline, Depends(get_pipeline)],
) -> EmbeddingService:
    return EmbeddingService(session, pipeline)


def get_export_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ExportService:
    return ExportService(session)


def get_import_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ImportService:
    return ImportService(session)
