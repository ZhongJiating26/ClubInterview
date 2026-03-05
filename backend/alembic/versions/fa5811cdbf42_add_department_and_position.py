"""add_department_and_position

Revision ID: fa5811cdbf42
Revises: h8i3j4k5l6m1
Create Date: 2026-01-04 08:40:10.615528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fa5811cdbf42'
down_revision: Union[str, Sequence[str], None] = 'h8i3j4k5l6m1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 创建 department 表
    op.create_table(
        'department',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_department_is_deleted'), 'department', ['is_deleted'], unique=False)

    # 创建 club_position 表
    op.create_table(
        'club_position',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirement', sa.Text(), nullable=True),
        sa.Column('quota', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, default='OPEN'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_club_position_is_deleted'), 'club_position', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('club_position')
    op.drop_table('department')
