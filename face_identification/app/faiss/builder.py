"""FAISS index construction utility."""

import time
from typing import Literal

import numpy as np
from loguru import logger

import faiss


def build_faiss_index(
    embeddings: np.ndarray,
    index_type: Literal["IndexFlatIP", "IndexIVFFlat", "HNSW"] = "IndexFlatIP",
    dimension: int = 512,
) -> faiss.Index:
    """
    Builds a FAISS index using L2-normalised embeddings.
    Uses Inner Product metric for cosine similarity on normalised vectors.

    Args:
        embeddings: Float32 array of shape (N, dimension).
        index_type: One of "IndexFlatIP", "IndexIVFFlat", "HNSW".
        dimension:  Dimensionality of embeddings (default 512).

    Returns:
        Built and trained faiss.Index object.
    """
    n_samples = len(embeddings)
    if n_samples == 0:
        raise ValueError("Cannot build FAISS index with empty embeddings array.")

    # Ensure float32 type
    embeddings_f32 = embeddings.astype(np.float32)

    # 1. Normalise embeddings in-place for cosine similarity using Inner Product
    faiss.normalize_L2(embeddings_f32)

    logger.info(
        "Building FAISS index of type: {} with {} items (dim={})",
        index_type,
        n_samples,
        dimension,
    )
    start_time = time.perf_counter()

    if index_type == "IndexFlatIP":
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings_f32)

    elif index_type == "IndexIVFFlat":
        # IndexIVFFlat requires a quantizer and training.
        # Rule of thumb: nlist (number of centroids) is roughly sqrt(N).
        # Must have at least nlist samples to train.
        nlist = int(min(max(4 * np.sqrt(n_samples), 2), 256))

        # Guard: IVFFlat requires at least nlist points to train, ideally more
        if n_samples < nlist:
            logger.warning(
                "Not enough samples ({}) to train IVFFlat with nlist={}. "
                "Falling back to IndexFlatIP.",
                n_samples,
                nlist,
            )
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings_f32)
        else:
            quantizer = faiss.IndexFlatIP(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
            # Train using the vectors themselves
            index.train(embeddings_f32)
            index.add(embeddings_f32)

    elif index_type == "HNSW":
        # HNSW search with 32 connections per node (standard for high recall)
        # Using Inner Product metric (equivalent to cosine since inputs are normalized)
        M = 32
        index = faiss.IndexHNSWFlat(dimension, M, faiss.METRIC_INNER_PRODUCT)
        index.add(embeddings_f32)

    else:
        raise ValueError(f"Unsupported FAISS index type: {index_type}")

    elapsed = (time.perf_counter() - start_time) * 1000
    logger.info("FAISS index built successfully in {:.2f} ms.", elapsed)
    return index
