"""Candidate ORM model."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.face_embedding import FaceEmbedding


class Candidate(UUIDMixin, TimestampMixin, Base):
    """Represents an enrolled candidate."""

    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("candidate_id", name="uq_candidates_candidate_id"),
        UniqueConstraint("email", name="uq_candidates_email"),
    )

    candidate_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Human-readable unique identifier (e.g. employee ID)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )
    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # One candidate → many embeddings (cascade delete)
    embeddings: Mapped[list["FaceEmbedding"]] = relationship(
        "FaceEmbedding",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} candidate_id={self.candidate_id!r} name={self.name!r}>"
