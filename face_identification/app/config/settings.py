"""Application settings loaded from environment / .env file."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="postgres")
    db_name: str = Field(default="enrollment_db")

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def sync_database_url(self) -> str:
        """Used by Alembic migrations (sync driver)."""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # ── InsightFace Models ────────────────────────────────────────────────────
    scrfd_model_path: str = Field(default="/home/pavithranraj/.insightface/models/buffalo_l")
    arcface_model_path: str = Field(default="/home/pavithranraj/.insightface/models/buffalo_l")
    insightface_model_pack: str = Field(default="buffalo_l")

    # ── FAISS Vector Search ───────────────────────────────────────────────────
    faiss_index_type: Literal["IndexFlatIP", "IndexIVFFlat", "HNSW"] = Field(default="IndexFlatIP")
    faiss_index_path: str = Field(default="faiss_index.bin")
    similarity_threshold: float = Field(default=0.65)
    top_k_default: int = Field(default=5)

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=60)

    # ── Server ────────────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)

    # ── Image Validation ──────────────────────────────────────────────────────
    max_image_size_mb: int = Field(default=10)
    allowed_image_types: list[str] = Field(default=["image/jpeg", "image/png", "image/bmp"])

    # ── Embedding ─────────────────────────────────────────────────────────────
    embedding_dimension: int = Field(default=512)


@lru_cache
def get_settings() -> Settings:
    return Settings()
