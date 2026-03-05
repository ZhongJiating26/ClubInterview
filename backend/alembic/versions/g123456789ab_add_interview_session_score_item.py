"""add interview_session_score_item table

Revision ID: g123456789ab
Revises: f123456789ab
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'g123456789ab'
down_revision: Union[str, Sequence[str], None] = 'f123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'interview_session_score_item',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('session_id', mysql.INTEGER(), nullable=False),
        sa.Column('score_item_id', mysql.INTEGER(), nullable=False),
        sa.Column('order_no', mysql.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interview_session_score_item_is_deleted'), 'interview_session_score_item', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_interview_session_score_item_session_id'), 'interview_session_score_item', ['session_id'], unique=False)
    op.create_index(op.f('ix_interview_session_score_item_score_item_id'), 'interview_session_score_item', ['score_item_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_interview_session_score_item_score_item_id'), table_name='interview_session_score_item')
    op.drop_index(op.f('ix_interview_session_score_item_session_id'), table_name='interview_session_score_item')
    op.drop_index(op.f('ix_interview_session_score_item_is_deleted'), table_name='interview_session_score_item')
    op.drop_table('interview_session_score_item')
