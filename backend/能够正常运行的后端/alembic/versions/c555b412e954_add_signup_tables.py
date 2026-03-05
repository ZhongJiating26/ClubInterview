"""add_signup_tables

Revision ID: c555b412e954
Revises: 86ab24dea31c
Create Date: 2026-01-04 10:28:17.955395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c555b412e954'
down_revision: Union[str, Sequence[str], None] = '86ab24dea31c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create signup related tables."""

    # 创建 recruitment_session 表
    op.create_table(
        'recruitment_session',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('max_candidates', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, default='DRAFT'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recruitment_session_is_deleted'), 'recruitment_session', ['is_deleted'], unique=False)

    # 创建 recruitment_session_position 表
    op.create_table(
        'recruitment_session_position',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('position_name', sa.String(length=100), nullable=False),
        sa.Column('position_description', sa.Text(), nullable=True),
        sa.Column('position_requirement', sa.Text(), nullable=True),
        sa.Column('recruit_quota', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recruitment_session_position_is_deleted'), 'recruitment_session_position', ['is_deleted'], unique=False)

    # 创建 signup_session 表
    op.create_table(
        'signup_session',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recruitment_session_id', sa.Integer(), nullable=False),
        sa.Column('self_intro', sa.Text(), nullable=True),
        sa.Column('extra_fields_json', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, default='PENDING'),
        sa.Column('audit_user_id', sa.Integer(), nullable=True),
        sa.Column('audit_time', sa.DateTime(), nullable=True),
        sa.Column('audit_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_signup_session_is_deleted'), 'signup_session', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_signup_session_user_id'), 'signup_session', ['user_id'], unique=False)
    op.create_index(op.f('ix_signup_session_recruitment_session_id'), 'signup_session', ['recruitment_session_id'], unique=False)

    # 创建 signup_item 表
    op.create_table(
        'signup_item',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('signup_session_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_signup_item_is_deleted'), 'signup_item', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_signup_item_signup_session_id'), 'signup_item', ['signup_session_id'], unique=False)

    # 创建 signup_attachment 表
    op.create_table(
        'signup_attachment',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('signup_session_id', sa.Integer(), nullable=False),
        sa.Column('file_url', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=20), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), nullable=True, default=0),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_signup_attachment_is_deleted'), 'signup_attachment', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_signup_attachment_signup_session_id'), 'signup_attachment', ['signup_session_id'], unique=False)


def downgrade() -> None:
    """Drop signup related tables."""
    op.drop_table('signup_attachment')
    op.drop_table('signup_item')
    op.drop_table('signup_session')
    op.drop_table('recruitment_session_position')
    op.drop_table('recruitment_session')
