"""API endpoints for importing candidate datasets."""

import json
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_faiss_manager, get_import_service
from app.schemas.import_ import ImportSummary

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/json", response_model=ImportSummary)
async def import_json_endpoint(
    file: UploadFile = File(...),
    import_service: Any = Depends(get_import_service),
) -> ImportSummary:
    """Imports candidate records from an uploaded JSON file."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")

    try:
        content = await file.read()
        records = json.loads(content.decode("utf-8"))
        if not isinstance(records, list):
            raise HTTPException(status_code=400, detail="JSON root must be a list of records.")

        logger.info("Received JSON import request with {} records.", len(records))
        summary = await import_service.import_json(records)
        return summary
    except json.JSONDecodeError as exc:
        logger.error("JSON decode error during import: {}", exc)
        raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error during JSON import: {}", exc)
        raise HTTPException(status_code=500, detail=f"JSON import failed: {exc}") from exc


@router.post("/csv", response_model=ImportSummary)
async def import_csv_endpoint(
    file: UploadFile = File(...),
    import_service: Any = Depends(get_import_service),
) -> ImportSummary:
    """Imports candidate records from an uploaded CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        content = await file.read()
        csv_text = content.decode("utf-8")
        logger.info("Received CSV import request.")
        summary = await import_service.import_csv(csv_text)
        return summary
    except Exception as exc:
        logger.exception("Unexpected error during CSV import: {}", exc)
        raise HTTPException(status_code=500, detail=f"CSV import failed: {exc}") from exc


@router.post("/postgres")
async def import_postgres_endpoint(
    db: AsyncSession = Depends(get_db_session),
    faiss_manager: Any = Depends(get_faiss_manager),
) -> dict:
    """
    Triggers FAISS index sync/rebuild from current PostgreSQL records.
    Aligns with GET /index/rebuild requirement.
    """
    try:
        logger.info("Received request to sync FAISS index with Postgres database.")
        success, size = await faiss_manager.rebuild(db)
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to rebuild FAISS index from Postgres."
            )
        return {"status": "success", "message": "Index synced with PostgreSQL.", "index_size": size}
    except Exception as exc:
        logger.exception("Failed during Postgres import sync: {}", exc)
        raise HTTPException(status_code=500, detail=f"Postgres sync failed: {exc}") from exc
