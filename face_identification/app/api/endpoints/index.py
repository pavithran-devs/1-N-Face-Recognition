"""API endpoints for FAISS Index management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_faiss_manager

router = APIRouter(prefix="/index", tags=["index"])


@router.post("/rebuild")
async def rebuild_index_endpoint(
    db: AsyncSession = Depends(get_db_session),
    faiss_manager: Any = Depends(get_faiss_manager),
) -> dict:
    """Rebuilds the FAISS index from database candidate embeddings."""
    try:
        logger.info("Manually triggered index rebuild.")
        success, size = await faiss_manager.rebuild(db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to rebuild FAISS index.")
        return {"status": "success", "message": "FAISS index rebuilt successfully.", "size": size}
    except Exception as exc:
        logger.exception("Index rebuild failed: {}", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/status")
async def get_index_status_endpoint(
    faiss_manager: Any = Depends(get_faiss_manager),
) -> dict:
    """Returns the current state, size, index type, and modification details of the FAISS index."""
    return faiss_manager.get_status()
