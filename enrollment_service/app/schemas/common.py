"""Shared Pydantic schemas: pagination, health, error responses."""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class PaginationMeta(BaseModel):
    total: int
    offset: int
    limit: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[DataT]):
    data: list[DataT]
    pagination: PaginationMeta


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    pipeline_loaded: bool


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail
