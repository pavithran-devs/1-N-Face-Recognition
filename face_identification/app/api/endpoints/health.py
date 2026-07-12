"""API endpoint for application health checking."""

from typing import Any

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_faiss_manager, get_pipeline
from app.recognition.pipeline import FaceRecognitionPipeline

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_endpoint(
    db: AsyncSession = Depends(get_db_session),
    pipeline: FaceRecognitionPipeline = Depends(get_pipeline),
    faiss_manager: Any = Depends(get_faiss_manager),
) -> dict:
    """
    Performs dynamic diagnostics on database connection, models pre-warming,
    and index memory states.
    """
    # 1. Database check
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        logger.error("Health check failed for database: {}", exc)

    # 2. Pipeline check
    pipeline_ok = pipeline.is_loaded

    # 3. FAISS check
    faiss_status = faiss_manager.get_status()

    overall_ok = db_ok and pipeline_ok and faiss_status["active"]

    return {
        "status": "healthy" if overall_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "face_models": "loaded" if pipeline_ok else "unloaded",
        "faiss_index": {
            "loaded": faiss_status["active"],
            "size": faiss_status["size"],
            "type": faiss_status["index_type"],
        },
    }
