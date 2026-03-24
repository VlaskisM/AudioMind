"""add_status_and_metadata_to_recordings

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('recordings', sa.Column('status', sa.String(20), nullable=False, server_default='uploaded'))
    op.add_column('recordings', sa.Column('original_filename', sa.String(), nullable=True))
    op.add_column('recordings', sa.Column('error_message', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('recordings', 'error_message')
    op.drop_column('recordings', 'original_filename')
    op.drop_column('recordings', 'status')
