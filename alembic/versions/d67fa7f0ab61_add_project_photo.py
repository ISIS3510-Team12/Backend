"""add project photo

Revision ID: d67fa7f0ab61
Revises: 36ea094edc8b
Create Date: 2026-11-26 21:17:34.380019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'd67fa7f0ab61'
down_revision: Union[str, Sequence[str], None] = '36ea094edc8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('projectphoto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('uploader_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('client_upload_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('caption', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('bucket', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('thumbnail_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uploader_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'uploader_id', 'client_upload_id')
    )
    op.create_index(op.f('ix_projectphoto_id'), 'projectphoto', ['id'], unique=False)
    op.create_index(op.f('ix_projectphoto_project_id'), 'projectphoto', ['project_id'], unique=False)
    op.create_index(op.f('ix_projectphoto_uploader_id'), 'projectphoto', ['uploader_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_projectphoto_uploader_id'), table_name='projectphoto')
    op.drop_index(op.f('ix_projectphoto_project_id'), table_name='projectphoto')
    op.drop_index(op.f('ix_projectphoto_id'), table_name='projectphoto')
    op.drop_table('projectphoto')
