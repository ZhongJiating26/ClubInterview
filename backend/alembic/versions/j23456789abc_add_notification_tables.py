"""add notification tables

Revision ID: j23456789abc
Revises: j123456789ab
Create Date: 2026-01-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'j23456789abc'
down_revision: Union[str, Sequence[str], None] = 'j123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 通知表
    op.create_table(
        'notification',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('type', mysql.VARCHAR(length=50), nullable=False),
        sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
        sa.Column('content', mysql.TEXT(), nullable=False),
        sa.Column('biz_id', mysql.INTEGER(), nullable=True),
        sa.Column('sent_at', mysql.DATETIME(), nullable=True),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_notification_is_deleted'), 'notification', ['is_deleted'], unique=False)

    # 用户通知关联表
    op.create_table(
        'notification_user',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('notification_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('read_status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('read_at', mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_notification_user_is_deleted'), 'notification_user', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_notification_user_notification_id'), 'notification_user', ['notification_id'], unique=False)
    op.create_index(op.f('ix_notification_user_user_id'), 'notification_user', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_notification_user_user_id'), table_name='notification_user')
    op.drop_index(op.f('ix_notification_user_notification_id'), table_name='notification_user')
    op.drop_index(op.f('ix_notification_user_is_deleted'), table_name='notification_user')
    op.drop_table('notification_user')

    op.drop_index(op.f('ix_notification_is_deleted'), table_name='notification')
    op.drop_table('notification')
