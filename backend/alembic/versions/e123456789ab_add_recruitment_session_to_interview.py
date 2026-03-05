"""add recruitment_session_id to interview_session

Revision ID: e123456789ab
Revises: d123456789ab
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e123456789ab'
down_revision: Union[str, Sequence[str], None] = 'd123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 添加 recruitment_session_id 字段到 interview_session 表
    op.add_column(
        'interview_session',
        sa.Column('recruitment_session_id', mysql.INTEGER(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interview_session', 'recruitment_session_id')
