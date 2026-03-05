"""update_school_table

Revision ID: c3d4e5f6g7h1
Revises: b2c3d4e5f6g1
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h1'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 修改school表"""
    # 添加 is_verified 字段
    op.add_column('school', sa.Column('is_verified', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Downgrade schema - 删除 is_verified 字段"""
    op.drop_column('school', 'is_verified')
