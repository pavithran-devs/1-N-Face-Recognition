"""Embedding generate / regenerate endpoints."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_embedding_service
from app.schemas.face_embedding import EmbeddingResponse
from app.services.embedding import EmbeddingService

router = APIRouter(prefix="/embedding", tags=["Embeddings"])


@router.post("/generate/{candidate_uuid}", response_model=EmbeddingResponse, status_code=201)
async def generate_embedding(
    candidate_uuid: uuid.UUID,
    service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    image: UploadFile = File(..., description="Face image (JPEG/PNG/BMP)"),
) -> EmbeddingResponse:
    """Generate and persist a new embedding for an existing candidate."""
    image_bytes = await image.read()
    embedding = await service.generate(candidate_uuid, image_bytes)
    return EmbeddingResponse.model_validate(embedding)


@router.put("/regenerate/{candidate_uuid}", response_model=EmbeddingResponse)
async def regenerate_embedding(
    candidate_uuid: uuid.UUID,
    service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    image: UploadFile = File(..., description="New face image (JPEG/PNG/BMP)"),
) -> EmbeddingResponse:
    """Delete all existing embeddings and generate a fresh one."""
    image_bytes = await image.read()
    embedding = await service.regenerate(candidate_uuid, image_bytes)
    return EmbeddingResponse.model_validate(embedding)


@router.get("/{candidate_uuid}", response_model=list[EmbeddingResponse])
async def get_embeddings(
    candidate_uuid: uuid.UUID,
    service: Annotated[EmbeddingService, Depends(get_embedding_service)],
) -> list[EmbeddingResponse]:
    """List all embeddings for a candidate."""
    embeddings = await service.get_embeddings(candidate_uuid)
    return [EmbeddingResponse.model_validate(e) for e in embeddings]
