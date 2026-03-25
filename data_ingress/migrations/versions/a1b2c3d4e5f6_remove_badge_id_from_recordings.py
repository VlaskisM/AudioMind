"""remove_badge_id_from_recordings

Revision ID: a1b2c3d4e5f6
Revises: 05de11df7f1c
Create Date: 2026-03-22 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '05de11df7f1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('recordings', 'badge_id')


def downgrade() -> None:
    op.add_column('recordings', sa.Column('badge_id', sa.String(), nullable=True))
