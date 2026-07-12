"""FAISS index similarity search."""

from dataclasses import dataclass

import numpy as np
from loguru import logger

import faiss


@dataclass
class SearchResult:
    candidate_uuid: str
    similarity: float
    rank: int


def search_faiss_index(
    index: faiss.Index,
    id_map: list[str],
    query_embedding: np.ndarray,
    top_k: int = 5,
) -> list[SearchResult]:
    """
    Search the FAISS index for the top-k nearest neighbors.
    Normalises the query embedding first for cosine similarity matching.

    Args:
        index:           Loaded faiss.Index object.
        id_map:          Mapping of local integer offsets to database candidate UUIDs.
        query_embedding: 512-dimensional query embedding as ndarray of shape (512,) or (1, 512).
        top_k:           Number of top results to return.

    Returns:
        List of SearchResult items.
    """
    # 1. Check index validity
    if index is None or not id_map:
        logger.warning("Empty or uninitialized FAISS index.")
        return []

    # 2. Reshape query to (1, D)
    query_f32 = query_embedding.astype(np.float32).reshape(1, -1)

    # 3. L2 Normalise query vector (crucial for cosine similarity via inner product)
    faiss.normalize_L2(query_f32)

    # 4. Limit top_k to index size
    actual_top_k = min(top_k, index.ntotal)
    if actual_top_k <= 0:
        return []

    # 5. Search
    # distances (inner products), indices of neighbors
    distances, indices = index.search(query_f32, actual_top_k)

    results: list[SearchResult] = []
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0], strict=True), start=1):
        # FAISS returns -1 for empty slots or failures
        if idx == -1 or idx >= len(id_map):
            continue

        cand_uuid = id_map[idx]
        similarity = float(dist)

        results.append(
            SearchResult(
                candidate_uuid=cand_uuid,
                similarity=similarity,
                rank=rank,
            )
        )

    return results
