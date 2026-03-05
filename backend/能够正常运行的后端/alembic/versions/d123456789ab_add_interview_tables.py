"""add interview module tables

Revision ID: d123456789ab
Revises: c555b412e954
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd123456789ab'
down_revision: Union[str, Sequence[str], None] = 'c555b412e954'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### 面试场次表 ###
    op.create_table(
        'interview_session',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('club_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('description', mysql.TEXT(), nullable=True),
        sa.Column('place', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('start_time', mysql.DATETIME(), nullable=False),
        sa.Column('end_time', mysql.DATETIME(), nullable=False),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interview_session_is_deleted'), 'interview_session', ['is_deleted'], unique=False)

    # ### 候选人排期表 ###
    op.create_table(
        'interview_candidate',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('session_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('signup_session_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('candidate_user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('planned_start_time', mysql.DATETIME(), nullable=True),
        sa.Column('planned_end_time', mysql.DATETIME(), nullable=True),
        sa.Column('actual_start_time', mysql.DATETIME(), nullable=True),
        sa.Column('actual_end_time', mysql.DATETIME(), nullable=True),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('final_score', mysql.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interview_candidate_is_deleted'), 'interview_candidate', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_interview_candidate_session_id'), 'interview_candidate', ['session_id'], unique=False)

    # ### 面试记录表 ###
    op.create_table(
        'interview_record',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('session_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('signup_session_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('candidate_user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('interviewer_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('total_score', mysql.FLOAT(), nullable=True),
        sa.Column('summary', mysql.TEXT(), nullable=True),
        sa.Column('record_text', mysql.TEXT(), nullable=True),
        sa.Column('recording_url', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('face_image_url', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('transcript_status', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('transcript_text', mysql.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interview_record_is_deleted'), 'interview_record', ['is_deleted'], unique=False)

    # ### 评分项表 ###
    op.create_table(
        'score_item',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('template_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('session_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('weight', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('max_score', mysql.FLOAT(), nullable=False),
        sa.Column('order_no', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_score_item_is_deleted'), 'score_item', ['is_deleted'], unique=False)

    # ### 面试评分明细表 ###
    op.create_table(
        'interview_score',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('record_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('score_item_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('item_name', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('item_weight', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('item_max_score', mysql.FLOAT(), autoincrement=False, nullable=False),
        sa.Column('score', mysql.FLOAT(), nullable=False),
        sa.Column('remark', mysql.VARCHAR(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_interview_score_is_deleted'), 'interview_score', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_interview_score_record_id'), 'interview_score', ['record_id'], unique=False)

    # ### 录取结果表 ###
    op.create_table(
        'admission_result',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.Column('updated_at', mysql.DATETIME(), nullable=True),
        sa.Column('is_deleted', mysql.TINYINT(), autoincrement=False, nullable=True),
        sa.Column('deleted_at', mysql.DATETIME(), nullable=True),
        sa.Column('interview_candidate_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('signup_session_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('candidate_user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('department_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('position_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('result', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('final_score_snapshot', mysql.FLOAT(), nullable=True),
        sa.Column('decided_by', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('decided_at', mysql.DATETIME(), nullable=True),
        sa.Column('remark', mysql.VARCHAR(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_admission_result_is_deleted'), 'admission_result', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_admission_result_is_deleted'), table_name='admission_result')
    op.drop_table('admission_result')

    op.drop_index(op.f('ix_interview_score_record_id'), table_name='interview_score')
    op.drop_index(op.f('ix_interview_score_is_deleted'), table_name='interview_score')
    op.drop_table('interview_score')

    op.drop_index(op.f('ix_score_item_is_deleted'), table_name='score_item')
    op.drop_table('score_item')

    op.drop_index(op.f('ix_interview_record_is_deleted'), table_name='interview_record')
    op.drop_table('interview_record')

    op.drop_index(op.f('ix_interview_candidate_session_id'), table_name='interview_candidate')
    op.drop_index(op.f('ix_interview_candidate_is_deleted'), table_name='interview_candidate')
    op.drop_table('interview_candidate')

    op.drop_index(op.f('ix_interview_session_is_deleted'), table_name='interview_session')
    op.drop_table('interview_session')
