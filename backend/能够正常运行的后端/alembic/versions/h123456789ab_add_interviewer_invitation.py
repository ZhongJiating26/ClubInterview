"""add interviewer_invitation table

Revision ID: h123456789ab
Revises: g123456789ab
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'h123456789ab'
down_revision: Union[str, Sequence[str], None] = 'g123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### 面试官邀请表 ###
    op.create_table(
        'interviewer_invitation',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('club_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('invite_code', mysql.VARCHAR(length=50), nullable=False),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('expired_at', mysql.DATETIME(), nullable=True),
        sa.Column('inviter_id', mysql.INTEGER(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invite_code'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interviewer_invitation_is_deleted'), 'interviewer_invitation', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_interviewer_invitation_club_id'), 'interviewer_invitation', ['club_id'], unique=False)
    op.create_index(op.f('ix_interviewer_invitation_user_id'), 'interviewer_invitation', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_interviewer_invitation_user_id'), table_name='interviewer_invitation')
    op.drop_index(op.f('ix_interviewer_invitation_club_id'), table_name='interviewer_invitation')
    op.drop_index(op.f('ix_interviewer_invitation_is_deleted'), table_name='interviewer_invitation')
    op.drop_table('interviewer_invitation')
