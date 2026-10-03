"""add task detail session

Revision ID: b5c8e1f3a7d2
Revises: a1b7c3d9e2f4
Create Date: 2026-10-02 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b5c8e1f3a7d2'
down_revision: Union[str, Sequence[str], None] = 'a1b7c3d9e2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('taskdetailsession',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('opened_at', sa.DateTime(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=False),
    sa.Column('progress_updated', sa.Boolean(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taskdetailsession_id'), 'taskdetailsession', ['id'], unique=False)
    op.create_index(op.f('ix_taskdetailsession_task_id'), 'taskdetailsession', ['task_id'], unique=False)
    op.create_index(op.f('ix_taskdetailsession_user_id'), 'taskdetailsession', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_taskdetailsession_user_id'), table_name='taskdetailsession')
    op.drop_index(op.f('ix_taskdetailsession_task_id'), table_name='taskdetailsession')
    op.drop_index(op.f('ix_taskdetailsession_id'), table_name='taskdetailsession')
    op.drop_table('taskdetailsession')
