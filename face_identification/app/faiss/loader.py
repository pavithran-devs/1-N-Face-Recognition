"""FAISS index serialization and disk I/O."""

import json
import os

from loguru import logger

import faiss


def save_index(index: faiss.Index, id_map: list[str], index_path: str) -> None:
    """
    Saves a FAISS index and its mapping metadata (list of UUIDs) to disk.
    """
    try:
        # Save index binary
        faiss.write_index(index, index_path)
        logger.info("FAISS index binary saved to: {}", index_path)

        # Save ID map metadata (e.g. index_path + ".meta")
        meta_path = index_path + ".meta"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(id_map, f, indent=2)
        logger.info("FAISS index metadata saved to: {}", meta_path)
    except Exception as exc:
        logger.error("Failed to save FAISS index: {}", exc)
        raise


def load_index(index_path: str) -> tuple[faiss.Index | None, list[str]]:
    """
    Loads a FAISS index and its mapping metadata from disk.
    Returns:
        Tuple: (faiss.Index, list of UUIDs) or (None, []) if not found.
    """
    meta_path = index_path + ".meta"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        logger.warning(
            "FAISS index files not found. Path: {} or {}",
            index_path,
            meta_path,
        )
        return None, []

    try:
        # Load index
        index = faiss.read_index(index_path)
        logger.info("Loaded FAISS index binary from: {}", index_path)

        # Load metadata
        with open(meta_path, encoding="utf-8") as f:
            id_map = json.load(f)
        logger.info("Loaded FAISS index metadata containing {} items.", len(id_map))

        return index, id_map
    except Exception as exc:
        logger.error("Failed to load FAISS index: {}", exc)
        return None, []
