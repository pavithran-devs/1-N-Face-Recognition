"""JSON exporter — writes candidate records (with embeddings) to a .json file."""
import json
from datetime import datetime
from pathlib import Path

from app.exporters.base import BaseExporter


class JsonExporter(BaseExporter):
    def export(self, records: list[dict], filename: str | None = None) -> Path:
        if filename is None:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            filename = f"export_{ts}.json"
        out_path = self._export_dir / filename
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2, ensure_ascii=False)
        return out_path
