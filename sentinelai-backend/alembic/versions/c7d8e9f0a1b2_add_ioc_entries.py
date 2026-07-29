"""add ioc_entries table

Revision ID: c7d8e9f0a1b2
Revises: a1b2c3d4e5f6
Create Date: 2024-07-28 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c7d8e9f0a1b2"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ioc_entries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("ioc_type", sa.String(50), nullable=False),
        sa.Column("ioc_value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_event", sa.String(255), nullable=True),
        sa.Column("source_log", sa.String(255), nullable=True),
        sa.Column("source_ip", sa.String(45), nullable=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occurrences", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("source_ids", postgresql.JSONB, nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("kill_chain_phase", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ioc_entries_id"), "ioc_entries", ["id"])
    op.create_index(op.f("ix_ioc_entries_ioc_type"), "ioc_entries", ["ioc_type"])
    op.create_index(op.f("ix_ioc_entries_normalized_value"), "ioc_entries", ["normalized_value"])
    op.create_index(op.f("ix_ioc_entries_source_ip"), "ioc_entries", ["source_ip"])


def downgrade() -> None:
    op.drop_index(op.f("ix_ioc_entries_source_ip"), table_name="ioc_entries")
    op.drop_index(op.f("ix_ioc_entries_normalized_value"), table_name="ioc_entries")
    op.drop_index(op.f("ix_ioc_entries_ioc_type"), table_name="ioc_entries")
    op.drop_index(op.f("ix_ioc_entries_id"), table_name="ioc_entries")
    op.drop_table("ioc_entries")
