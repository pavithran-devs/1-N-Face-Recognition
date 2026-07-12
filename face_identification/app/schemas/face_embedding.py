"""Pydantic schemas for the FaceEmbedding resource."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class EmbeddingResponse(BaseModel):
    id: uuid.UUID
    candidate_uuid: uuid.UUID
    embedding_dimension: int
    model_name: str
    normalized: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EmbeddingDetailResponse(EmbeddingResponse):
    """Includes the raw embedding vector."""

    embedding: list[float]

    model_config = {"from_attributes": True}
