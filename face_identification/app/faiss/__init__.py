"""FAISS integration module packaging."""

from app.faiss.builder import build_faiss_index
from app.faiss.loader import load_index, save_index
from app.faiss.manager import FAISSManager
from app.faiss.search import SearchResult, search_faiss_index

__all__ = [
    "build_faiss_index",
    "load_index",
    "save_index",
    "SearchResult",
    "search_faiss_index",
    "FAISSManager",
]
