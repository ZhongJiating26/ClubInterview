"""club_school_code

Revision ID: h8i3j4k5l6m1
Revises: g7h2i3j4k5l1
Create Date: 2025-12-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8i3j4k5l6m1'
down_revision: Union[str, Sequence[str], None] = 'g7h2i3j4k5l1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - club表 school_id 改为 school_code (varchar)"""
    # 先删除旧索引
    op.drop_index(op.f('idx_club_school_id'), table_name='club')
    # 删除旧字段
    op.drop_column('club', 'school_id')
    # 添加新字段
    op.add_column('club', sa.Column('school_code', sa.String(50), nullable=False))
    # 创建新索引
    op.create_index(op.f('idx_club_school_code'), 'club', ['school_code'], unique=False)


def downgrade() -> None:
    """Downgrade schema - 恢复 school_id"""
    op.drop_index(op.f('idx_club_school_code'), table_name='club')
    op.drop_column('club', 'school_code')
    op.add_column('club', sa.Column('school_id', sa.BigInteger(), nullable=False))
    op.create_index(op.f('idx_club_school_id'), 'club', ['school_id'], unique=False)
