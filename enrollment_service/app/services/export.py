"""ExportService — delegates to JSON/CSV exporters."""
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.exceptions import NotFoundError
from app.repositories.candidate import CandidateRepository
from app.repositories.face_embedding import EmbeddingRepository
from app.schemas.export import ExportSummary


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self._cand_repo = CandidateRepository(session)
        self._emb_repo = EmbeddingRepository(session)
        self._settings = get_settings()

    async def export_all_json(self) -> ExportSummary:
        from app.exporters.json_exporter import JsonExporter

        candidates = await self._cand_repo.get_all(limit=100_000)
        records = await self._build_records(candidates)
        exporter = JsonExporter(self._settings.export_dir)
        file_path = exporter.export(records)
        return ExportSummary(
            exported_count=len(records),
            file_path=str(file_path),
            format="json",
        )

    async def export_all_csv(self) -> ExportSummary:
        from app.exporters.csv_exporter import CsvExporter

        candidates = await self._cand_repo.get_all(limit=100_000)
        records = await self._build_records(candidates)
        exporter = CsvExporter(self._settings.export_dir)
        file_path = exporter.export(records)
        return ExportSummary(
            exported_count=len(records),
            file_path=str(file_path),
            format="csv",
        )

    async def export_single_json(self, candidate_uuid: uuid.UUID) -> ExportSummary:
        from app.exporters.json_exporter import JsonExporter

        candidate = await self._cand_repo.get_by_id(candidate_uuid)
        if candidate is None:
            raise NotFoundError(f"Candidate {candidate_uuid} not found.")
        records = await self._build_records([candidate])
        exporter = JsonExporter(self._settings.export_dir)
        file_path = exporter.export(records, filename=f"{candidate_uuid}.json")
        return ExportSummary(exported_count=1, file_path=str(file_path), format="json")

    async def export_single_csv(self, candidate_uuid: uuid.UUID) -> ExportSummary:
        from app.exporters.csv_exporter import CsvExporter

        candidate = await self._cand_repo.get_by_id(candidate_uuid)
        if candidate is None:
            raise NotFoundError(f"Candidate {candidate_uuid} not found.")
        records = await self._build_records([candidate])
        exporter = CsvExporter(self._settings.export_dir)
        file_path = exporter.export(records, filename=f"{candidate_uuid}.csv")
        return ExportSummary(exported_count=1, file_path=str(file_path), format="csv")

    async def _build_records(self, candidates: list) -> list[dict]:
        records = []
        for c in candidates:
            embeddings = await self._emb_repo.get_by_candidate_uuid(c.id)
            records.append({
                "id": str(c.id),
                "candidate_id": c.candidate_id,
                "name": c.name,
                "email": c.email,
                "dob": c.dob.isoformat() if c.dob else None,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
                "embeddings": [
                    {
                        "id": str(e.id),
                        "embedding": e.embedding,
                        "embedding_dimension": e.embedding_dimension,
                        "model_name": e.model_name,
                        "normalized": e.normalized,
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in embeddings
                ],
            })
        return records
