"""Application lifecycle events: startup model loading, shutdown cleanup."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.database.engine import AsyncSessionLocal
from app.faiss.manager import FAISSManager
from app.recognition.pipeline import FaceRecognitionPipeline


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    logger.info("Starting Face Identification Service v1.0.0")

    # 1. Initialize FaceRecognitionPipeline
    pipeline = FaceRecognitionPipeline()
    try:
        pipeline.load()
    except Exception as exc:
        logger.error(
            "Pipeline failed to pre-warm models: {}. Continuing without recognition models.", exc
        )
    app.state.pipeline = pipeline

    # 2. Initialize FAISS index
    faiss_manager = FAISSManager()

    # Rebuild from database on startup if index is not present on disk
    if not faiss_manager.get_status()["active"] or faiss_manager.size == 0:
        logger.info(
            "FAISS index not found on disk or empty. Attempting auto-rebuild from PostgreSQL on startup..."
        )
        async with AsyncSessionLocal() as session:
            try:
                success, size = await faiss_manager.rebuild(session)
                if success:
                    logger.info("FAISS index auto-rebuilt from database on startup. Size: {}", size)
                else:
                    logger.warning("Auto-rebuilt failed or database has no records.")
            except Exception as exc:
                logger.error("Exception during startup FAISS rebuild: {}", exc)

    logger.info("Startup complete — Face Identification API ready.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down Face Identification Service.")
