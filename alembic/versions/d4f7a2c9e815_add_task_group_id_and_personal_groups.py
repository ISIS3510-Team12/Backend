"""add task group id and personal groups

Revision ID: d4f7a2c9e815
Revises: c3a9e1d4f6b8
Create Date: 2026-10-01 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4f7a2c9e815'
down_revision: Union[str, Sequence[str], None] = 'c3a9e1d4f6b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERSONAL_NAME = 'Personal'
PERSONAL_DESCRIPTION = 'Personal tasks'


def upgrade() -> None:
    op.add_column('task', sa.Column('group_id', sa.Integer(), nullable=True))
    bind = op.get_bind()
    bind.execute(
        sa.text(
            'UPDATE task SET group_id = project.group_id '
            'FROM project WHERE task.project_id = project.id'
        )
    )
    user_ids = bind.execute(
        sa.text(
            'SELECT u.user_id FROM "user" u WHERE NOT EXISTS ('
            'SELECT 1 FROM usergroup ug JOIN "group" g ON g.id = ug.group_id '
            'WHERE ug.user_id = u.user_id AND g.name = :name)'
        ),
        {'name': PERSONAL_NAME},
    ).scalars().all()
    for user_id in user_ids:
        group_id = bind.execute(
            sa.text(
                'INSERT INTO "group" (name, description) '
                'VALUES (:name, :description) RETURNING id'
            ),
            {'name': PERSONAL_NAME, 'description': PERSONAL_DESCRIPTION},
        ).scalar_one()
        bind.execute(
            sa.text(
                'INSERT INTO usergroup (user_id, group_id) '
                'VALUES (:user_id, :group_id)'
            ),
            {'user_id': user_id, 'group_id': group_id},
        )
    bind.execute(
        sa.text(
            'UPDATE task SET group_id = personal.group_id '
            'FROM (SELECT ug.user_id, ug.group_id FROM usergroup ug '
            'JOIN "group" g ON g.id = ug.group_id WHERE g.name = :name) personal '
            'WHERE task.user_id = personal.user_id AND task.group_id IS NULL'
        ),
        {'name': PERSONAL_NAME},
    )
    op.alter_column('task', 'group_id', existing_type=sa.Integer(), nullable=False)
    op.create_index(op.f('ix_task_group_id'), 'task', ['group_id'], unique=False)
    op.create_foreign_key('fk_task_group_id_group', 'task', 'group', ['group_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_task_group_id_group', 'task', type_='foreignkey')
    op.drop_index(op.f('ix_task_group_id'), table_name='task')
    op.drop_column('task', 'group_id')
    bind = op.get_bind()
    params = {'name': PERSONAL_NAME}
    bind.execute(
        sa.text(
            'DELETE FROM usergroup WHERE group_id IN '
            '(SELECT id FROM "group" WHERE name = :name)'
        ),
        params,
    )
    bind.execute(sa.text('DELETE FROM "group" WHERE name = :name'), params)
