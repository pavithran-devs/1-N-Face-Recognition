"""Abstract exporter interface."""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseExporter(ABC):
    """Abstract base class for data exporters."""

    def __init__(self, export_dir: Path) -> None:
        self._export_dir = Path(export_dir)
        self._export_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, records: list[dict], filename: str | None = None) -> Path:
        """
        Export records to a file.

        Args:
            records:  List of candidate dicts (as produced by ExportService._build_records).
            filename: Optional output filename; auto-generated if None.

        Returns:
            Path to the written file.
        """
        ...
