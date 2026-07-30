"""add threat_intel tables

Revision ID: ff715ffd0bd0
Revises: d834257b0bb6
Create Date: 2026-07-29 12:40:26.057736
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ff715ffd0bd0'
down_revision: Union[str, None] = 'd834257b0bb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('lookup_history', 'threat_intel_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)


def downgrade() -> None:
    op.alter_column('lookup_history', 'threat_intel_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)
