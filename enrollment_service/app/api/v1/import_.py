"""Import endpoints: JSON and CSV."""
import csv
import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_import_service
from app.schemas.import_ import ImportSummary
from app.services.import_ import ImportService

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/json", response_model=ImportSummary)
async def import_json(
    service: Annotated[ImportService, Depends(get_import_service)],
    file: UploadFile = File(..., description="JSON file with a list of candidate records."),
) -> ImportSummary:
    """Import candidates from a JSON file."""
    content = await file.read()
    try:
        records = json.loads(content)
    except json.JSONDecodeError as exc:
        from app.exceptions import ValidationError
        raise ValidationError(f"Invalid JSON: {exc}") from exc

    if not isinstance(records, list):
        from app.exceptions import ValidationError
        raise ValidationError("JSON root must be an array of candidate records.")

    return await service.import_records(records)


@router.post("/csv", response_model=ImportSummary)
async def import_csv(
    service: Annotated[ImportService, Depends(get_import_service)],
    file: UploadFile = File(..., description="CSV file with candidate records."),
) -> ImportSummary:
    """Import candidates from a CSV file."""
    content = await file.read()
    text = content.decode("utf-8-sig")  # handle BOM
    reader = csv.DictReader(io.StringIO(text))
    records: list[dict] = []
    for row in reader:
        # Reconstruct embeddings list from flattened CSV columns
        embedding_str = row.pop("embedding", "")
        record = dict(row)
        if embedding_str:
            record["embeddings"] = [
                {
                    "embedding": embedding_str,
                    "model_name": row.get("model_name", "buffalo_l"),
                    "normalized": row.get("normalized", "true").lower() == "true",
                }
            ]
        records.append(record)

    return await service.import_records(records)
