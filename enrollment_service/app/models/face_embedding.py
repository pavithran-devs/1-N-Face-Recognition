"""FaceEmbedding ORM model."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class FaceEmbedding(UUIDMixin, TimestampMixin, Base):
    """Stores the 512-d ArcFace embedding for a candidate."""

    __tablename__ = "face_embeddings"

    candidate_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    embedding: Mapped[list[float]] = mapped_column(
        ARRAY(FLOAT),
        nullable=False,
        comment="512-dimensional L2-normalised ArcFace embedding",
    )
    embedding_dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=512,
    )
    model_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="buffalo_l",
    )
    normalized: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Always True — embeddings are L2-normalised before storage",
    )

    # back-reference
    candidate: Mapped["Candidate"] = relationship(
        "Candidate",
        back_populates="embeddings",
    )

    def __repr__(self) -> str:
        return (
            f"<FaceEmbedding id={self.id} candidate_uuid={self.candidate_uuid} "
            f"dim={self.embedding_dimension}>"
        )
