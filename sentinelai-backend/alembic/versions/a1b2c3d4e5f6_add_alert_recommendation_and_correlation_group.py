"""add alert recommendation and correlation_group_id fields

Revision ID: a1b2c3d4e5f6
Revises: b4c3f1a2d9e8
Create Date: 2024-07-28 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "b4c3f1a2d9e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("correlation_group_id", sa.String(255), nullable=True))
    op.add_column("alerts", sa.Column("recommendation", sa.Text(), nullable=True))
    op.create_index(op.f("ix_alerts_correlation_group_id"), "alerts", ["correlation_group_id"])


def downgrade() -> None:
    op.drop_column("alerts", "recommendation")
    op.drop_column("alerts", "correlation_group_id")
