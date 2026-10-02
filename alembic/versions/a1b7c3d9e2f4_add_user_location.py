"""add user location

Revision ID: a1b7c3d9e2f4
Revises: be47b5982fb7
Create Date: 2026-10-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b7c3d9e2f4'
down_revision: Union[str, Sequence[str], None] = 'be47b5982fb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('userlocation',
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('notify_within', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('userlocation')
