"""ImportService — validates and persists imported candidate records."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.schemas.import_ import ImportSummary
from app.validators.import_validator import validate_import_record


class ImportService:
    def __init__(self, session: AsyncSession) -> None:
        self._cand_repo = CandidateRepository(session)
        self._emb_repo = EmbeddingRepository(session)

    async def import_records(self, records: list[dict]) -> ImportSummary:
        """
        Import a list of candidate records (from JSON or CSV).
        Skips duplicates; collects per-record errors.
        """
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

            # Duplicate check
            if await self._cand_repo.exists_by_candidate_id(record["candidate_id"]):
                errors.append(f"{label}: candidate_id already exists, skipped.")
                skipped += 1
                continue
            if await self._cand_repo.exists_by_email(record["email"]):
                errors.append(f"{label}: email already exists, skipped.")
                skipped += 1
                continue

            try:
                from datetime import date
                dob = None
                if record.get("dob"):
                    dob = date.fromisoformat(record["dob"])

                candidate = await self._cand_repo.create(
                    candidate_id=record["candidate_id"],
                    name=record["name"],
                    email=record["email"],
                    dob=dob,
                )

                for emb_record in record.get("embeddings", []):
                    embedding = emb_record.get("embedding", [])
                    if isinstance(embedding, str):
                        # CSV format: semicolon-separated floats
                        embedding = [float(x) for x in embedding.split(";") if x]
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

        return ImportSummary(
            imported_count=imported,
            skipped_count=skipped,
            errors=errors,
        )
