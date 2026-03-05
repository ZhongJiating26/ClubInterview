"""create_club_table

Revision ID: g7h2i3j4k5l1
Revises: f6g7h2i3j4k1
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g7h2i3j4k5l1'
down_revision: Union[str, Sequence[str], None] = 'f6g7h2i3j4k1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 创建club表"""
    op.create_table(
        'club',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('school_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cert_file_url', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='REVIEW'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('idx_club_school_id'), 'club', ['school_id'], unique=False)
    op.create_index(op.f('idx_club_status'), 'club', ['status'], unique=False)
    op.create_index(op.f('idx_club_is_deleted'), 'club', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Downgrade schema - 删除club表"""
    op.drop_index(op.f('idx_club_is_deleted'), table_name='club')
    op.drop_index(op.f('idx_club_status'), table_name='club')
    op.drop_index(op.f('idx_club_school_id'), table_name='club')
    op.drop_table('club')
