"""add mitre_techniques, mitre_mappings, coverage_statistics tables

Revision ID: d9e8f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2024-07-29 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d9e8f0a1b2c3"
down_revision: str | None = "c7d8e9f0a1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mitre_techniques",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("technique_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tactic", sa.String(100), nullable=False),
        sa.Column("tactic_id", sa.String(20), nullable=True),
        sa.Column("platform", postgresql.JSONB, nullable=True),
        sa.Column("permissions_required", postgresql.JSONB, nullable=True),
        sa.Column("detection", sa.Text(), nullable=True),
        sa.Column("is_subtechnique", sa.Boolean(), nullable=False),
        sa.Column("parent_technique_id", sa.String(20), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("mitre_version", sa.String(10), nullable=False),
        sa.Column("detection_rules", postgresql.JSONB, nullable=True),
        sa.Column("ioc_indicators", postgresql.JSONB, nullable=True),
        sa.Column("kill_chain_phase", sa.String(50), nullable=True),
        sa.Column("data_sources", postgresql.JSONB, nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("technique_id"),
    )
    op.create_index(op.f("ix_mitre_techniques_id"), "mitre_techniques", ["id"])
    op.create_index(op.f("ix_mitre_techniques_technique_id"), "mitre_techniques", ["technique_id"])
    op.create_index(op.f("ix_mitre_techniques_tactic"), "mitre_techniques", ["tactic"])

    op.create_table(
        "mitre_mappings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("technique_id", sa.String(20), nullable=False),
        sa.Column("mapped_type", sa.String(50), nullable=False),
        sa.Column("mapped_id", sa.String(255), nullable=False),
        sa.Column("mapped_name", sa.String(500), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("mapped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mitre_mappings_id"), "mitre_mappings", ["id"])
    op.create_index(op.f("ix_mitre_mappings_technique_id"), "mitre_mappings", ["technique_id"])
    op.create_index(op.f("ix_mitre_mappings_mapped_type"), "mitre_mappings", ["mapped_type"])
    op.create_index(op.f("ix_mitre_mappings_mapped_id"), "mitre_mappings", ["mapped_id"])

    op.create_table(
        "coverage_statistics",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("tactic", sa.String(100), nullable=False),
        sa.Column("total_techniques", sa.Integer(), nullable=False),
        sa.Column("mapped_techniques", sa.Integer(), nullable=False),
        sa.Column("coverage_percent", sa.Float(), nullable=False),
        sa.Column("total_detections", sa.Integer(), nullable=False),
        sa.Column("mapped_detections", sa.Integer(), nullable=False),
        sa.Column("avg_confidence", sa.Float(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coverage_statistics_id"), "coverage_statistics", ["id"])
    op.create_index(op.f("ix_coverage_statistics_tactic"), "coverage_statistics", ["tactic"])


def downgrade() -> None:
    op.drop_index(op.f("ix_coverage_statistics_tactic"), table_name="coverage_statistics")
    op.drop_index(op.f("ix_coverage_statistics_id"), table_name="coverage_statistics")
    op.drop_table("coverage_statistics")
    op.drop_index(op.f("ix_mitre_mappings_mapped_id"), table_name="mitre_mappings")
    op.drop_index(op.f("ix_mitre_mappings_mapped_type"), table_name="mitre_mappings")
    op.drop_index(op.f("ix_mitre_mappings_technique_id"), table_name="mitre_mappings")
    op.drop_index(op.f("ix_mitre_mappings_id"), table_name="mitre_mappings")
    op.drop_table("mitre_mappings")
    op.drop_index(op.f("ix_mitre_techniques_tactic"), table_name="mitre_techniques")
    op.drop_index(op.f("ix_mitre_techniques_technique_id"), table_name="mitre_techniques")
    op.drop_index(op.f("ix_mitre_techniques_id"), table_name="mitre_techniques")
    op.drop_table("mitre_techniques")
