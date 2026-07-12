"""Schemas for import requests and responses."""
from pydantic import BaseModel


class ImportSummary(BaseModel):
    imported_count: int
    skipped_count: int
    errors: list[str]
