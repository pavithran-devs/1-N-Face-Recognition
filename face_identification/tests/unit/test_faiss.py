"""Unit tests for the FAISS Index builder, searcher, and manager."""

import os
import tempfile

import numpy as np
import pytest

from app.faiss.builder import build_faiss_index
from app.faiss.loader import load_index, save_index
from app.faiss.search import search_faiss_index


@pytest.fixture
def fake_embeddings() -> np.ndarray:
    # Build 10 random 512-d float vectors
    vectors = np.random.rand(10, 512).astype(np.float32)
    # L2 normalize
    for i in range(10):
        vectors[i] /= np.linalg.norm(vectors[i])
    return vectors


def test_build_flat_ip_index(fake_embeddings) -> None:
    index = build_faiss_index(fake_embeddings, index_type="IndexFlatIP")
    assert index.is_trained is True
    assert index.ntotal == 10


def test_build_hnsw_index(fake_embeddings) -> None:
    index = build_faiss_index(fake_embeddings, index_type="HNSW")
    assert index.is_trained is True
    assert index.ntotal == 10


def test_build_ivf_flat_fallback(fake_embeddings) -> None:
    # nlist for IVFFlat is larger than n_samples (10), so it should log a warning
    # and fallback to IndexFlatIP
    index = build_faiss_index(fake_embeddings, index_type="IndexIVFFlat")
    assert index.ntotal == 10


def test_search_index(fake_embeddings) -> None:
    index = build_faiss_index(fake_embeddings, index_type="IndexFlatIP")
    id_map = [f"UUID_{i}" for i in range(10)]

    # Query with one of the exact vectors
    query = fake_embeddings[3]
    results = search_faiss_index(index, id_map, query, top_k=3)

    assert len(results) == 3
    # Top match should be the exact match (index 3) with similarity near 1.0 (Inner Product)
    assert results[0].candidate_uuid == "UUID_3"
    assert results[0].similarity > 0.99
    assert results[0].rank == 1


def test_save_and_load_index(fake_embeddings) -> None:
    index = build_faiss_index(fake_embeddings, index_type="IndexFlatIP")
    id_map = [f"UUID_{i}" for i in range(10)]

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "test_index.bin")
        save_index(index, id_map, index_path)

        assert os.path.exists(index_path)
        assert os.path.exists(index_path + ".meta")

        loaded_idx, loaded_map = load_index(index_path)
        assert loaded_idx is not None
        assert loaded_idx.ntotal == 10
        assert loaded_map == id_map
