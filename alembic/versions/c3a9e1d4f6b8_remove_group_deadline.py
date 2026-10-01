"""remove group deadline

Revision ID: c3a9e1d4f6b8
Revises: e4ad9cb1728c
Create Date: 2026-10-01 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3a9e1d4f6b8'
down_revision: Union[str, Sequence[str], None] = 'e4ad9cb1728c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('group', 'deadline')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'group',
        sa.Column(
            'deadline',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.alter_column('group', 'deadline', server_default=None)
