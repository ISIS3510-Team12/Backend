"""make-task-project-id-nullable

Revision ID: f64d9ce92891
Revises: 0362b439e0a3
Create Date: 2026-09-25 12:13:39.723835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f64d9ce92891'
down_revision: Union[str, Sequence[str], None] = '0362b439e0a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('task', 'project_id', existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('task', 'project_id', existing_type=sa.INTEGER(), nullable=False)
