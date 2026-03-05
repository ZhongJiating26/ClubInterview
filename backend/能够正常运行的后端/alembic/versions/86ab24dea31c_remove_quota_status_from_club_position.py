"""remove_quota_status_from_club_position

Revision ID: 86ab24dea31c
Revises: fa5811cdbf42
Create Date: 2026-01-04 10:03:15.730029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '86ab24dea31c'
down_revision: Union[str, Sequence[str], None] = 'fa5811cdbf42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove quota and status columns from club_position."""
    op.drop_column('club_position', 'quota')
    op.drop_column('club_position', 'status')


def downgrade() -> None:
    """Add back quota and status columns."""
    op.add_column('club_position', sa.Column('quota', sa.Integer(), nullable=True))
    op.add_column('club_position', sa.Column('status', sa.String(20), nullable=True, server_default='OPEN'))
