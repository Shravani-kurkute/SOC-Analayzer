"""add correlation tables

Revision ID: b4c3f1a2d9e8
Revises: f41d01764319
Create Date: 2024-07-28 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b4c3f1a2d9e8"
down_revision: str | None = "f41d01764319"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "correlation_groups",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("correlation_id", sa.String(100), nullable=False),
        sa.Column("group_type", sa.String(50), nullable=False),
        sa.Column("source_ip", sa.String(45), nullable=True),
        sa.Column("destination_ip", sa.String(45), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attack_chain", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_correlation_groups_id"), "correlation_groups", ["id"])
    op.create_index(op.f("ix_correlation_groups_correlation_id"), "correlation_groups", ["correlation_id"])
    op.create_index(op.f("ix_correlation_groups_group_type"), "correlation_groups", ["group_type"])
    op.create_index(op.f("ix_correlation_groups_source_ip"), "correlation_groups", ["source_ip"])
    op.create_index(op.f("ix_correlation_groups_destination_ip"), "correlation_groups", ["destination_ip"])
    op.create_index(op.f("ix_correlation_groups_username"), "correlation_groups", ["username"])
    op.create_index(op.f("ix_correlation_groups_hostname"), "correlation_groups", ["hostname"])
    op.create_index(op.f("ix_correlation_groups_start_time"), "correlation_groups", ["start_time"])
    op.create_index(op.f("ix_correlation_groups_end_time"), "correlation_groups", ["end_time"])

    op.create_table(
        "correlation_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("group_id", sa.String(), nullable=False),
        sa.Column("parsed_event_id", sa.String(255), nullable=True),
        sa.Column("log_entry_id", sa.String(255), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_source", sa.String(100), nullable=True),
        sa.Column("source_ip", sa.String(45), nullable=True),
        sa.Column("destination_ip", sa.String(45), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String(50), nullable=True),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("raw_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["correlation_groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_correlation_events_id"), "correlation_events", ["id"])
    op.create_index(op.f("ix_correlation_events_group_id"), "correlation_events", ["group_id"])
    op.create_index(op.f("ix_correlation_events_event_type"), "correlation_events", ["event_type"])
    op.create_index(op.f("ix_correlation_events_timestamp"), "correlation_events", ["timestamp"])


def downgrade() -> None:
    op.drop_table("correlation_events")
    op.drop_table("correlation_groups")
