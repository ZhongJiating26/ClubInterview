"""remove_school_unused_fields

Revision ID: d4e5f6g7h2i1
Revises: c3d4e5f6g7h1
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h2i1'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6g7h1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 删除school表的冗余字段"""
    op.drop_column('school', 'province')
    op.drop_column('school', 'city')
    op.drop_column('school', 'status')


def downgrade() -> None:
    """Downgrade schema - 恢复字段"""
    op.add_column('school', sa.Column('province', sa.String(50), nullable=True))
    op.add_column('school', sa.Column('city', sa.String(50), nullable=True))
    op.add_column('school', sa.Column('status', sa.Integer(), nullable=False, server_default='1'))
