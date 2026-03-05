"""school_id_to_school_code

Revision ID: f6g7h2i3j4k1
Revises: e5f6g7h2i3j1
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6g7h2i3j4k1'
down_revision: Union[str, Sequence[str], None] = 'e5f6g7h2i3j1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - school_id 改为 school_code (string)"""
    # 删除旧的 school_id 字段
    op.drop_column('user_account', 'school_id')
    # 添加新的 school_code 字段
    op.add_column('user_account', sa.Column('school_code', sa.String(50), nullable=True))


def downgrade() -> None:
    """Downgrade schema - 恢复 school_id"""
    op.drop_column('user_account', 'school_code')
    op.add_column('user_account', sa.Column('school_id', sa.Integer(), nullable=True))
