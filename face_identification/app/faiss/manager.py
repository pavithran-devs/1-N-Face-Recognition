"""Thread-safe FAISS index manager with database auto-rebuild integration."""

import os
import threading
import time

import numpy as np
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import faiss
from app.config.settings import get_settings
from app.faiss.builder import build_faiss_index
from app.faiss.loader import load_index, save_index
from app.faiss.search import SearchResult, search_faiss_index
from app.models.candidate import Candidate


class FAISSManager:
    """
    Manages loading, searching, and rebuilding the FAISS index.
    Thread-safe implementation with atomic swaps.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        # Check if already initialized to prevent double init
        if hasattr(self, "_initialized"):
            return

        self._settings = get_settings()
        self._index: faiss.Index | None = None
        self._id_map: list[str] = []
        self._index_lock = threading.RLock()  # Reentrant Lock
        self._initialized = True
        self._last_built: float = 0.0

        # Try to load index from disk on startup
        self.load_from_disk()

    def load_from_disk(self) -> bool:
        """Loads index and metadata from disk. Returns True if successful."""
        with self._index_lock:
            index, id_map = load_index(self._settings.faiss_index_path)
            if index is not None:
                self._index = index
                self._id_map = id_map
                self._last_built = os.path.getmtime(self._settings.faiss_index_path)
                logger.info("Successfully loaded FAISS index from disk. Size: {}", index.ntotal)
                return True
            return False

    @property
    def size(self) -> int:
        with self._index_lock:
            return self._index.ntotal if self._index is not None else 0

    def get_status(self) -> dict:
        """Returns details about the current FAISS index state."""
        with self._index_lock:
            return {
                "active": self._index is not None,
                "size": self.size,
                "index_type": self._settings.faiss_index_type,
                "last_built": self._last_built,
                "file_exists": os.path.exists(self._settings.faiss_index_path),
            }

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        """Performs vector search in the active index."""
        with self._index_lock:
            if self._index is None:
                logger.warning("Search requested but FAISS index is not built.")
                return []
            return search_faiss_index(self._index, self._id_map, query_embedding, top_k)

    async def rebuild(self, db_session: AsyncSession) -> tuple[bool, int]:
        """
        Queries all candidate embeddings from the database, builds a new FAISS index,
        writes it to disk, and performs an atomic in-memory swap.
        """
        logger.info("Starting FAISS index rebuild from database...")
        start_time = time.perf_counter()

        try:
            # 1. Fetch all candidates that have embeddings
            query = select(Candidate).options(selectinload(Candidate.embeddings))
            result = await db_session.execute(query)
            candidates = result.scalars().all()

            embeddings_list = []
            id_map_list = []

            for cand in candidates:
                for embedding_record in cand.embeddings:
                    if len(embedding_record.embedding) == self._settings.embedding_dimension:
                        embeddings_list.append(embedding_record.embedding)
                        # We map the vector offset to the Candidate UUID
                        id_map_list.append(str(cand.id))

            if not embeddings_list:
                logger.warning("No embeddings found in the database. FAISS index cannot be built.")
                return True, 0

            # 2. Build FAISS index from the gathered embeddings matrix
            embeddings_array = np.array(embeddings_list, dtype=np.float32)
            new_index = build_faiss_index(
                embeddings_array,
                index_type=self._settings.faiss_index_type,
                dimension=self._settings.embedding_dimension,
            )

            # 3. Save to disk
            save_index(new_index, id_map_list, self._settings.faiss_index_path)

            # 4. Atomic in-memory swap
            with self._index_lock:
                self._index = new_index
                self._id_map = id_map_list
                self._last_built = time.time()

            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(
                "FAISS index rebuild completed successfully in {:.2f} ms. Size: {}",
                elapsed,
                self.size,
            )
            return True, self.size

        except Exception as exc:
            logger.error("Failed to rebuild FAISS index: {}", exc)
            return False, 0
