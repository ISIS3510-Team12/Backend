"""allow a single photo attachment per task

Revision ID: b7d2f4a9c1e3
Revises: e4ad9cb1728c
Create Date: 2026-10-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7d2f4a9c1e3'
down_revision: Union[str, Sequence[str], None] = 'e4ad9cb1728c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DELETE FROM attachment
        WHERE kind = 'photo'
          AND id NOT IN (
              SELECT DISTINCT ON (task_id) id
              FROM attachment
              WHERE kind = 'photo'
              ORDER BY task_id, last_modified_date DESC, id DESC
          )
        """
    )
    op.create_index(
        'uq_attachment_task_photo',
        'attachment',
        ['task_id'],
        unique=True,
        postgresql_where=sa.text("kind = 'photo'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'uq_attachment_task_photo',
        table_name='attachment',
        postgresql_where=sa.text("kind = 'photo'"),
    )
