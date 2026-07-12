"""
Shared pytest fixtures.

Uses aiosqlite + SQLAlchemy for an in-memory DB so tests don't need PostgreSQL.
The FaceRecognitionPipeline is mocked to avoid downloading InsightFace models.
"""
import asyncio
import json
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.types import TypeDecorator

from app.database.base import Base
from app.database.engine import get_db_session
from app.main import create_app
from app.recognition.pipeline import FaceRecognitionPipeline, PipelineResult
from app.recognition.quality.base import QualityCode, QualityResult


# ── In-memory SQLite engine for unit/API tests ────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class JSONEncodedList(TypeDecorator):
    """
    Stores a Python list as a JSON string in SQLite.
    Transparently replaces ARRAY(FLOAT) for the test database.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        return json.loads(value)


def _patch_array_columns_for_sqlite() -> None:
    """
    Walk all mapped columns in Base.metadata and replace any PostgreSQL ARRAY
    column types with JSONEncodedList so SQLite can handle them.
    """
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, ARRAY):
                column.type = JSONEncodedList()


_patch_array_columns_for_sqlite()


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    TestSession = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSession() as session:
        yield session


# ── Mock pipeline ─────────────────────────────────────────────────────────────

def make_mock_pipeline() -> FaceRecognitionPipeline:
    """Return a pipeline that always succeeds with a fake 512-d embedding."""
    mock = MagicMock(spec=FaceRecognitionPipeline)
    mock.is_loaded = True

    fake_embedding = np.random.rand(512).astype(np.float32)
    fake_embedding /= np.linalg.norm(fake_embedding)

    from app.recognition.detector.base import FaceDetection
    fake_detection = FaceDetection(
        bbox=np.array([10, 10, 110, 110], dtype=np.float32),
        landmarks=np.zeros((5, 2), dtype=np.float32),
        confidence=0.99,
    )

    mock.process.return_value = PipelineResult(
        embedding=fake_embedding,
        embedding_dim=512,
        model_name="mock_arcface",
        normalized=True,
        detection=fake_detection,
        quality=QualityResult.ok(),
        timings={"detection": 0.01, "quality": 0.001, "alignment": 0.005, "embedding": 0.02},
    )
    return mock


@pytest.fixture
def mock_pipeline() -> FaceRecognitionPipeline:
    return make_mock_pipeline()


# ── FastAPI test client ───────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_client(db_engine, mock_pipeline) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    # Override DB dependency to use in-memory SQLite
    TestSession = async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    from app.database.engine import get_db_session
    app.dependency_overrides[get_db_session] = override_get_db

    # Inject mock pipeline
    app.state.pipeline = mock_pipeline

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
