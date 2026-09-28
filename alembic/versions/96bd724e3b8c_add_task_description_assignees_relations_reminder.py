"""add task description, assignees, related tasks, reminder enabled

Revision ID: 96bd724e3b8c
Revises: f64d9ce92891
Create Date: 2026-09-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '96bd724e3b8c'
down_revision: Union[str, Sequence[str], None] = 'f64d9ce92891'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('task', sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Existing reminders are treated as enabled; then drop the default to match the model.
    op.add_column('reminder', sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column('reminder', 'enabled', server_default=None)
    op.drop_column('reminder', 'kind')

    op.create_table('taskassignee',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('task_id', 'user_id')
    )
    op.create_table('taskrelation',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('related_task_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['related_task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('task_id', 'related_task_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('taskrelation')
    op.drop_table('taskassignee')

    # Backfill required by the original NOT NULL column.
    op.add_column('reminder', sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=''))
    op.alter_column('reminder', 'kind', server_default=None)
    op.drop_column('reminder', 'enabled')

    op.drop_column('task', 'description')
