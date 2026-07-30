"""add threat_intel tables

Revision ID: d834257b0bb6
Revises: 3d063bd306bb
Create Date: 2026-07-29 12:38:48.464027
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd834257b0bb6'
down_revision: Union[str, None] = '3d063bd306bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('lookup_history',
    sa.Column('threat_intel_id', sa.String(length=36), nullable=False),
    sa.Column('ioc_type', sa.String(length=50), nullable=False),
    sa.Column('ioc_value', sa.Text(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.Column('response_time_ms', sa.Integer(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('looked_up_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lookup_history_id'), 'lookup_history', ['id'], unique=False)
    op.create_index(op.f('ix_lookup_history_threat_intel_id'), 'lookup_history', ['threat_intel_id'], unique=False)
    op.create_table('threat_intel',
    sa.Column('ioc_type', sa.String(length=50), nullable=False),
    sa.Column('ioc_value', sa.Text(), nullable=False),
    sa.Column('normalized_value', sa.Text(), nullable=False),
    sa.Column('reputation_score', sa.Float(), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('malicious_count', sa.Integer(), nullable=False),
    sa.Column('harmless_count', sa.Integer(), nullable=False),
    sa.Column('suspicious_count', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('asn', sa.String(length=100), nullable=True),
    sa.Column('asn_org', sa.String(length=255), nullable=True),
    sa.Column('is_malicious', sa.Boolean(), nullable=False),
    sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_analysis', sa.DateTime(timezone=True), nullable=True),
    sa.Column('raw_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threat_intel_id'), 'threat_intel', ['id'], unique=False)
    op.create_index(op.f('ix_threat_intel_ioc_type'), 'threat_intel', ['ioc_type'], unique=False)
    op.create_index(op.f('ix_threat_intel_normalized_value'), 'threat_intel', ['normalized_value'], unique=False)
    op.create_table('threat_provider_results',
    sa.Column('threat_intel_id', sa.String(length=36), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('reputation', sa.String(length=50), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('malicious', sa.Boolean(), nullable=False),
    sa.Column('categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('raw_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('looked_up_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threat_provider_results_id'), 'threat_provider_results', ['id'], unique=False)
    op.create_index(op.f('ix_threat_provider_results_threat_intel_id'), 'threat_provider_results', ['threat_intel_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_threat_provider_results_threat_intel_id'), table_name='threat_provider_results')
    op.drop_index(op.f('ix_threat_provider_results_id'), table_name='threat_provider_results')
    op.drop_table('threat_provider_results')
    op.drop_index(op.f('ix_threat_intel_normalized_value'), table_name='threat_intel')
    op.drop_index(op.f('ix_threat_intel_ioc_type'), table_name='threat_intel')
    op.drop_index(op.f('ix_threat_intel_id'), table_name='threat_intel')
    op.drop_table('threat_intel')
    op.drop_index(op.f('ix_lookup_history_threat_intel_id'), table_name='lookup_history')
    op.drop_index(op.f('ix_lookup_history_id'), table_name='lookup_history')
    op.drop_table('lookup_history')
