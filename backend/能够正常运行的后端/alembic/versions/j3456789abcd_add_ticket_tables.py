"""add ticket tables

Revision ID: j3456789abcd
Revises: j23456789abc
Create Date: 2026-01-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'j3456789abcd'
down_revision: Union[str, Sequence[str], None] = 'j23456789abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 工单主表
    op.create_table(
        'ticket',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('club_id', mysql.INTEGER(), nullable=True),
        sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
        sa.Column('category', mysql.VARCHAR(length=50), nullable=False),
        sa.Column('content', mysql.TEXT(), nullable=False),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('priority', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('assignee_id', mysql.INTEGER(), nullable=True),
        sa.Column('resolved_at', mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_ticket_is_deleted'), 'ticket', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_ticket_user_id'), 'ticket', ['user_id'], unique=False)

    # 工单回复表
    op.create_table(
        'ticket_reply',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('ticket_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('content', mysql.TEXT(), nullable=False),
        sa.Column('is_from_staff', mysql.TINYINT(), autoincrement=False, nullable=False),
        sa.Column('attachment_url', mysql.VARCHAR(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_ticket_reply_is_deleted'), 'ticket_reply', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_ticket_reply_ticket_id'), 'ticket_reply', ['ticket_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_ticket_reply_ticket_id'), table_name='ticket_reply')
    op.drop_index(op.f('ix_ticket_reply_is_deleted'), table_name='ticket_reply')
    op.drop_table('ticket_reply')

    op.drop_index(op.f('ix_ticket_user_id'), table_name='ticket')
    op.drop_index(op.f('ix_ticket_is_deleted'), table_name='ticket')
    op.drop_table('ticket')
