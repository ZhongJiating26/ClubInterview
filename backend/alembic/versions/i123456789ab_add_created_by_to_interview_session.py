"""add created_by to interview_session

Revision ID: i123456789ab
Revises: h123456789ab
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'i123456789ab'
down_revision: Union[str, Sequence[str], None] = 'h123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 添加 created_by 字段到 interview_session 表
    op.add_column(
        'interview_session',
        sa.Column('created_by', mysql.INTEGER(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interview_session', 'created_by')
