"""remove_centroid_columns

Revision ID: b7e21a2c3d4f
Revises: 9e8f4ca438df
Create Date: 2026-07-17 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e21a2c3d4f'
down_revision: Union[str, None] = '9e8f4ca438df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('face_embeddings', 'num_images_enrolled')
    op.drop_column('face_embeddings', 'is_centroid')


def downgrade() -> None:
    op.add_column('face_embeddings', sa.Column('is_centroid', sa.Boolean(), nullable=True, comment='True if the embedding is a multi-image centroid'))
    op.add_column('face_embeddings', sa.Column('num_images_enrolled', sa.Integer(), nullable=True, comment='Number of images used to compute the embedding'))
    op.execute("UPDATE face_embeddings SET is_centroid = FALSE WHERE is_centroid IS NULL")
    op.execute("UPDATE face_embeddings SET num_images_enrolled = 1 WHERE num_images_enrolled IS NULL")
