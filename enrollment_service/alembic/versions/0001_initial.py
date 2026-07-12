"""Initial tables: candidates and face_embeddings

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, UUID

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── candidates ────────────────────────────────────────────────────────────
    op.create_table(
        "candidates",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", name="uq_candidates_candidate_id"),
        sa.UniqueConstraint("email", name="uq_candidates_email"),
    )
    op.create_index("ix_candidates_id", "candidates", ["id"])
    op.create_index("ix_candidates_candidate_id", "candidates", ["candidate_id"])
    op.create_index("ix_candidates_name", "candidates", ["name"])
    op.create_index("ix_candidates_email", "candidates", ["email"])

    # ── face_embeddings ───────────────────────────────────────────────────────
    op.create_table(
        "face_embeddings",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", ARRAY(FLOAT()), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("normalized", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_uuid"],
            ["candidates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_face_embeddings_id", "face_embeddings", ["id"])
    op.create_index(
        "ix_face_embeddings_candidate_uuid", "face_embeddings", ["candidate_uuid"]
    )


def downgrade() -> None:
    op.drop_table("face_embeddings")
    op.drop_table("candidates")
