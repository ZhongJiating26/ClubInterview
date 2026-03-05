"""remove_is_verified_from_school

Revision ID: e5f6g7h2i3j1
Revises: d4e5f6g7h2i1
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h2i3j1'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6g7h2i1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 删除school表的is_verified字段"""
    op.drop_column('school', 'is_verified')


def downgrade() -> None:
    """Downgrade schema - 恢复字段"""
    op.add_column('school', sa.Column('is_verified', sa.Integer(), nullable=False, server_default='1'))
