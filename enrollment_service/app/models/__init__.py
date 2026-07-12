"""ORM models — import here to ensure they are registered with SQLAlchemy metadata."""
from app.models.candidate import Candidate
from app.models.face_embedding import FaceEmbedding

__all__ = ["Candidate", "FaceEmbedding"]
