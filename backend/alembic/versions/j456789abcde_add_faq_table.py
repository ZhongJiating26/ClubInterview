"""add faq table

Revision ID: j456789abcde
Revises: j3456789abcd
Create Date: 2026-01-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'j456789abcde'
down_revision: Union[str, Sequence[str], None] = 'j3456789abcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'faq',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('club_id', mysql.INTEGER(), nullable=True),
        sa.Column('category', mysql.VARCHAR(length=50), nullable=False),
        sa.Column('question', mysql.VARCHAR(length=255), nullable=False),
        sa.Column('answer', mysql.TEXT(), nullable=False),
        sa.Column('order_no', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('is_pinned', mysql.TINYINT(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_faq_is_deleted'), 'faq', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_faq_club_id'), 'faq', ['club_id'], unique=False)
    op.create_index(op.f('ix_faq_category'), 'faq', ['category'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_faq_category'), table_name='faq')
    op.drop_index(op.f('ix_faq_club_id'), table_name='faq')
    op.drop_index(op.f('ix_faq_is_deleted'), table_name='faq')
    op.drop_table('faq')
