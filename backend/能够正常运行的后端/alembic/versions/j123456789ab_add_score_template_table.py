"""add score_template table

Revision ID: j123456789ab
Revises: i123456789ab
Create Date: 2026-01-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'j123456789ab'
down_revision: Union[str, Sequence[str], None] = 'i123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'score_template',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('club_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_score_template_is_deleted'), 'score_template', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_score_template_club_id'), 'score_template', ['club_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_score_template_club_id'), table_name='score_template')
    op.drop_index(op.f('ix_score_template_is_deleted'), table_name='score_template')
    op.drop_table('score_template')
