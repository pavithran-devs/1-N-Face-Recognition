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

    # Rebuild and sync from database on startup unconditionally (skipped in testing)
    import os
    import sys

    is_testing = os.getenv("TESTING", "").lower() == "true" or "pytest" in sys.modules

    if is_testing:
        logger.info("Skipping FAISS index startup rebuild (testing mode active).")
    else:
        logger.info("Syncing FAISS index with PostgreSQL database on startup...")
        async with AsyncSessionLocal() as session:
            try:
                success, size = await faiss_manager.rebuild(session)
                if success:
                    logger.info(
                        "FAISS index auto-rebuilt and synced from database on startup. Size: {}",
                        size,
                    )
                else:
                    logger.warning("Auto-rebuild failed or database has no records.")
            except Exception as exc:
                logger.error("Exception during startup FAISS rebuild: {}", exc)

    logger.info("Startup complete — Face Identification API ready.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down Face Identification Service.")
