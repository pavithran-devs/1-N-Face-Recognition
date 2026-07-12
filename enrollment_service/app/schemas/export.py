"""Schemas for export responses."""
from pydantic import BaseModel


class ExportSummary(BaseModel):
    exported_count: int
    file_path: str
    format: str
