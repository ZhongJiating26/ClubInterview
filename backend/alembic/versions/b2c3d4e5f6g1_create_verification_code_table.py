"""create_verification_code_table

Revision ID: b2c3d4e5f6g1
Revises: 1f153bcd10b7
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g1'
down_revision: Union[str, Sequence[str], None] = '1f153bcd10b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 创建验证码表"""
    op.create_table(
        'verification_code',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('scene', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('expired_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('idx_verification_code_phone'), 'verification_code', ['phone'], unique=False)
    op.create_index(op.f('idx_verification_code_is_deleted'), 'verification_code', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Downgrade schema - 删除验证码表"""
    op.drop_index(op.f('idx_verification_code_is_deleted'), table_name='verification_code')
    op.drop_index(op.f('idx_verification_code_phone'), table_name='verification_code')
    op.drop_table('verification_code')
