"""API endpoints for Candidate Face Identification."""

import time
import uuid
from typing import Any

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_candidate_repository, get_db_session, get_faiss_manager, get_pipeline
from app.config.settings import get_settings
from app.core.telemetry import TelemetryTracker
from app.exceptions import ImageValidationError, QualityCheckError
from app.recognition.pipeline import FaceRecognitionPipeline, PipelineError

router = APIRouter(tags=["identify"])
settings = get_settings()
telemetry = TelemetryTracker()


def process_identification(
    image: np.ndarray,
    pipeline: FaceRecognitionPipeline,
    faiss_manager: Any,
    db_session: AsyncSession,
    cand_repo: Any,
    threshold: float,
    top_k: int,
) -> dict:
    """Helper executing pipeline -> similarity search -> postgres fetch details."""
    api_start = time.perf_counter()

    # 1. Run pipeline
    pipeline_res = pipeline.process(image)
    if isinstance(pipeline_res, PipelineError):
        # Trigger quality validation exception mapped to HTTP 422
        raise QualityCheckError(
            message=pipeline_res.message,
            quality_code=pipeline_res.quality.code.value,
            details=pipeline_res.quality.details,
        )

    # Success timings (ms)
    t_det = pipeline_res.timings.get("detection", 0.0) * 1000
    t_emb = pipeline_res.timings.get("embedding", 0.0) * 1000

    # 2. Vector search
    search_start = time.perf_counter()
    matches = faiss_manager.search(pipeline_res.embedding, top_k=top_k)
    t_search = (time.perf_counter() - search_start) * 1000

    # 3. Match logic
    matched = False

    if matches:
        top_match = matches[0]
        # Log similarity score
        logger.info(
            "Top FAISS candidate UUID: {} similarity: {:.4f} threshold: {:.4f}",
            top_match.candidate_uuid,
            top_match.similarity,
            threshold,
        )

        if top_match.similarity >= threshold:
            # Match succeeded! Fetch details from DB
            # Run query synchronously or asynchronously
            matched = True

            # Since CandidateRepository is async, we yield it from deps
            # We will handle candidate detail fetch in the async controller, or here if we have sessions.
            # However, this helper is called in async endpoints, so we should make it return raw search match
            # and let the endpoint do the async repository fetching.
            # To keep clean separation, let's return matches, query embedding results, and timings.

    return {
        "pipeline_result": pipeline_res,
        "matches": matches,
        "matched": matched,
        "timings": {
            "detection": t_det,
            "embedding": t_emb,
            "search": t_search,
        },
        "api_start": api_start,
    }


async def fetch_candidate_details(
    db: AsyncSession,
    cand_repo: Any,
    match_data: dict,
    threshold: float,
) -> dict:
    """Async candidate loader mapping UUID to JSON response."""
    matches = match_data["matches"]
    matched = match_data["matched"]
    timings = match_data["timings"]
    api_start = match_data["api_start"]

    if not matched or not matches:
        t_api = (time.perf_counter() - api_start) * 1000
        telemetry.record_search(
            hit=False,
            detection_ms=timings["detection"],
            embedding_ms=timings["embedding"],
            search_ms=timings["search"],
            total_api_ms=t_api,
        )
        return {"matched": False, "message": "Unknown Candidate"}

    top_match = matches[0]
    cand_uuid = uuid.UUID(top_match.candidate_uuid)

    # Fetch details
    candidate = await cand_repo.get_by_id(cand_uuid)
    if not candidate:
        logger.error("FAISS index contains Candidate UUID {} but not found in Postgres.", cand_uuid)
        t_api = (time.perf_counter() - api_start) * 1000
        telemetry.record_search(
            hit=False,
            detection_ms=timings["detection"],
            embedding_ms=timings["embedding"],
            search_ms=timings["search"],
            total_api_ms=t_api,
        )
        return {"matched": False, "message": "Unknown Candidate"}

    t_api = (time.perf_counter() - api_start) * 1000
    telemetry.record_search(
        hit=True,
        detection_ms=timings["detection"],
        embedding_ms=timings["embedding"],
        search_ms=timings["search"],
        total_api_ms=t_api,
    )

    logger.info(
        "Matched candidate ID: {} Name: {} Similarity: {:.4f} Rank: 1 Latency: {:.1f}ms",
        candidate.candidate_id,
        candidate.name,
        top_match.similarity,
        t_api,
    )

    return {
        "matched": True,
        "candidate_id": candidate.candidate_id,
        "name": candidate.name,
        "dob": candidate.dob.isoformat() if candidate.dob else None,
        "email": candidate.email,
        "similarity": float(f"{top_match.similarity:.4f}"),
        "rank": 1,
    }


@router.post("/identify")
async def identify_endpoint(
    file: UploadFile = File(...),
    threshold: float | None = Form(default=None),
    top_k: int | None = Form(default=None),
    db: AsyncSession = Depends(get_db_session),
    pipeline: FaceRecognitionPipeline = Depends(get_pipeline),
    faiss_manager: Any = Depends(get_faiss_manager),
    cand_repo: Any = Depends(get_candidate_repository),
) -> dict:
    """
    Identifies a candidate from an uploaded face image.
    Performs detection, quality check, alignment, embedding extraction, and index lookup.
    """
    # 1. Read and validate file content
    content_type = file.content_type
    if content_type not in settings.allowed_image_types:
        # Check filename as fallback
        ext = file.filename.split(".")[-1].lower() if file.filename else ""
        if ext not in ("jpg", "jpeg", "png", "bmp"):
            raise ImageValidationError(f"Unsupported content type '{content_type}'.")

    image_bytes = await file.read()
    if len(image_bytes) > settings.max_image_size_mb * 1024 * 1024:
        raise ImageValidationError(f"File size exceeds maximum {settings.max_image_size_mb}MB.")

    # 2. Decode BGR
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ImageValidationError("Could not decode image.")

    # 3. Parameters
    t_val = threshold if threshold is not None else settings.similarity_threshold
    k_val = top_k if top_k is not None else settings.top_k_default

    # 4. Search and load details
    match_data = process_identification(image, pipeline, faiss_manager, db, cand_repo, t_val, k_val)
    return await fetch_candidate_details(db, cand_repo, match_data, t_val)


@router.post("/camera/identify")
async def camera_identify_endpoint(
    file: UploadFile = File(...),
    threshold: float | None = Form(default=None),
    top_k: int | None = Form(default=None),
    db: AsyncSession = Depends(get_db_session),
    pipeline: FaceRecognitionPipeline = Depends(get_pipeline),
    faiss_manager: Any = Depends(get_faiss_manager),
    cand_repo: Any = Depends(get_candidate_repository),
) -> dict:
    """
    Identifies a candidate from a live camera capture frame.
    Equivalent logic to /identify but optimized for fast streaming clients (tablets/webcams).
    """
    # Reuses same logic as identify
    image_bytes = await file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ImageValidationError("Could not decode camera image frame.")

    t_val = threshold if threshold is not None else settings.similarity_threshold
    k_val = top_k if top_k is not None else settings.top_k_default

    match_data = process_identification(image, pipeline, faiss_manager, db, cand_repo, t_val, k_val)
    return await fetch_candidate_details(db, cand_repo, match_data, t_val)
