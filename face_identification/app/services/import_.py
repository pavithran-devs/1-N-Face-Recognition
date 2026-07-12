"""ImportService — validates and persists imported candidate records."""

import csv
import io
from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.faiss.manager import FAISSManager
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.schemas.import_ import ImportSummary
from app.validators.import_validator import validate_import_record


class ImportService:
    """Manages importing candidate details and embeddings from CSV/JSON formats."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cand_repo = CandidateRepository(session)
        self._emb_repo = EmbeddingRepository(session)
        self._faiss_manager = FAISSManager()

    async def import_json(self, records: list[dict[str, Any]]) -> ImportSummary:
        """Imports candidate records from a parsed JSON structure."""
        return await self._import_records_list(records)

    async def import_csv(self, csv_content: str) -> ImportSummary:
        """Imports candidate records from a CSV file content."""
        records: list[dict[str, Any]] = []
        try:
            f = io.StringIO(csv_content.strip())
            reader = csv.DictReader(f)

            # Map flattened CSV rows back to candidate dict structure
            # CSV fields: id, candidate_id, name, email, dob, created_at, updated_at,
            #             embedding_id, embedding, embedding_dimension, model_name, normalized
            candidate_map: dict[str, dict[str, Any]] = {}

            for row in reader:
                cand_id = row.get("candidate_id")
                if not cand_id:
                    continue

                if cand_id not in candidate_map:
                    candidate_map[cand_id] = {
                        "candidate_id": cand_id,
                        "name": row.get("name", ""),
                        "email": row.get("email", ""),
                        "dob": row.get("dob") or None,
                        "embeddings": [],
                    }

                # Check if there is an embedding in this row
                embedding_str = row.get("embedding")
                if embedding_str:
                    candidate_map[cand_id]["embeddings"].append(
                        {
                            "embedding": embedding_str,
                            "embedding_dimension": int(row.get("embedding_dimension") or 512),
                            "model_name": row.get("model_name", "buffalo_l"),
                            "normalized": row.get("normalized", "True").lower() == "true",
                        }
                    )

            records = list(candidate_map.values())
        except Exception as exc:
            logger.error("Failed to parse CSV import content: {}", exc)
            return ImportSummary(
                imported_count=0, skipped_count=0, errors=[f"CSV parsing failed: {exc}"]
            )

        return await self._import_records_list(records)

    async def _import_records_list(self, records: list[dict[str, Any]]) -> ImportSummary:
        """Helper to iterate, validate, duplicate-check, and persist candidate records."""
        imported = 0
        skipped = 0
        errors: list[str] = []

        for i, record in enumerate(records):
            label = record.get("candidate_id", f"record[{i}]")
            try:
                validate_import_record(record)
            except Exception as exc:
                errors.append(f"{label}: validation error — {exc}")
                skipped += 1
                continue

            # Duplicate check (by candidate_id and email)
            # In Phase 2, if a candidate already exists, we will skip it or append new embeddings
            existing_candidate = await self._cand_repo.get_by_candidate_id(record["candidate_id"])
            if existing_candidate is not None:
                # Candidate exists, we can import new embeddings for them if they aren't already duplicate
                # For simplicity, skip if candidate ID already exists to match Phase 1 exactly.
                errors.append(f"{label}: candidate_id already exists, skipped.")
                skipped += 1
                continue

            if await self._cand_repo.exists_by_email(record["email"]):
                errors.append(f"{label}: email already exists, skipped.")
                skipped += 1
                continue

            try:
                dob = None
                dob_str = record.get("dob")
                if dob_str:
                    dob = date.fromisoformat(dob_str.split("T")[0])

                candidate = await self._cand_repo.create(
                    candidate_id=record["candidate_id"],
                    name=record["name"],
                    email=record["email"],
                    dob=dob,
                )

                for emb_record in record.get("embeddings", []):
                    embedding = emb_record.get("embedding", [])
                    if isinstance(embedding, str):
                        embedding = [float(x) for x in embedding.split(";") if x.strip()]

                    await self._emb_repo.create(
                        candidate_uuid=candidate.id,
                        embedding=embedding,
                        embedding_dimension=len(embedding),
                        model_name=emb_record.get("model_name", "buffalo_l"),
                        normalized=emb_record.get("normalized", True),
                    )

                imported += 1
            except Exception as exc:
                errors.append(f"{label}: failed to import — {exc}")
                skipped += 1

        # Rebuild FAISS index automatically if we imported any new records
        if imported > 0:
            logger.info("Imported {} candidates. Triggering index rebuild...", imported)
            await self._faiss_manager.rebuild(self._session)

        return ImportSummary(
            imported_count=imported,
            skipped_count=skipped,
            errors=errors,
        )
