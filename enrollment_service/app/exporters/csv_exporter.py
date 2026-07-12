"""CSV exporter — flattened rows with embedding as semicolon-separated floats."""
import csv
from datetime import datetime
from pathlib import Path

from app.exporters.base import BaseExporter

_FIELDNAMES = [
    "id", "candidate_id", "name", "email", "dob",
    "created_at", "updated_at",
    # Embedding columns (first embedding only per row)
    "embedding_id", "embedding", "embedding_dimension", "model_name", "normalized",
]


class CsvExporter(BaseExporter):
    def export(self, records: list[dict], filename: str | None = None) -> Path:
        if filename is None:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            filename = f"export_{ts}.csv"
        out_path = self._export_dir / filename

        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES, extrasaction="ignore")
            writer.writeheader()

            for record in records:
                embeddings = record.get("embeddings", [])
                if not embeddings:
                    # Write candidate row with empty embedding columns
                    writer.writerow({**record, "embedding_id": "", "embedding": "",
                                     "embedding_dimension": "", "model_name": "",
                                     "normalized": ""})
                else:
                    # One row per embedding
                    for emb in embeddings:
                        embedding_str = ";".join(f"{v:.8f}" for v in emb["embedding"])
                        writer.writerow({
                            **record,
                            "embedding_id": emb.get("id", ""),
                            "embedding": embedding_str,
                            "embedding_dimension": emb.get("embedding_dimension", ""),
                            "model_name": emb.get("model_name", ""),
                            "normalized": emb.get("normalized", True),
                        })
        return out_path
