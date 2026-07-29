"""Add reporting tables

Revision ID: f5884c4e25d7
Revises: a1b2c3d4e5f7
Create Date: 2026-07-30 00:12:12.297783
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f5884c4e25d7'
down_revision: Union[str, None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('generated_reports',
    sa.Column('report_type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('format', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('date_range_start', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_range_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('download_count', sa.Integer(), nullable=False),
    sa.Column('generated_by_id', sa.String(length=255), nullable=True),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_reports_id'), 'generated_reports', ['id'], unique=False)
    op.create_index(op.f('ix_generated_reports_report_type'), 'generated_reports', ['report_type'], unique=False)

    op.create_table('scheduled_reports',
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('report_type', sa.String(length=50), nullable=False),
    sa.Column('format', sa.String(length=10), nullable=False),
    sa.Column('cron_expression', sa.String(length=100), nullable=False),
    sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('recipients', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.String(length=255), nullable=True),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_reports_id'), 'scheduled_reports', ['id'], unique=False)
    op.create_index(op.f('ix_scheduled_reports_report_type'), 'scheduled_reports', ['report_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scheduled_reports_report_type'), table_name='scheduled_reports')
    op.drop_index(op.f('ix_scheduled_reports_id'), table_name='scheduled_reports')
    op.drop_table('scheduled_reports')
    op.drop_index(op.f('ix_generated_reports_report_type'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_id'), table_name='generated_reports')
    op.drop_table('generated_reports')
