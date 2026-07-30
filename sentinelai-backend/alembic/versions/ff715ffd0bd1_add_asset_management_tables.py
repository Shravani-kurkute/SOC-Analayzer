"""add_asset_management_tables

Revision ID: ff715ffd0bd1
Revises: fcd8afce010d
Create Date: 2026-07-30 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ff715ffd0bd1'
down_revision: Union[str, None] = 'fcd8afce010d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('assets', sa.Column('environment', sa.String(length=50), nullable=True))
    op.add_column('assets', sa.Column('vendor', sa.String(length=255), nullable=True))
    op.add_column('assets', sa.Column('serial_number', sa.String(length=255), nullable=True))
    op.add_column('assets', sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('assets', sa.Column('discovery_source', sa.String(length=50), nullable=True))

    op.create_table('asset_risks',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('asset_id', sa.String(length=255), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('open_incidents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_alerts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('threat_intel_matches', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cve_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exposure_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('criticality_weight', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_asset_risks_asset_id', 'asset_risks', ['asset_id'])

    op.create_table('asset_owners',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('asset_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_asset_owners_asset_id', 'asset_owners', ['asset_id'])

    op.create_table('asset_groups',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('asset_tags',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('asset_id', sa.String(length=255), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_asset_tags_asset_id', 'asset_tags', ['asset_id'])

    op.create_table('asset_relationships',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('source_asset_id', sa.String(length=255), nullable=False),
        sa.Column('target_asset_id', sa.String(length=255), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_asset_relationships_source', 'asset_relationships', ['source_asset_id'])
    op.create_index('ix_asset_relationships_target', 'asset_relationships', ['target_asset_id'])

    op.create_table('asset_history',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('asset_id', sa.String(length=255), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_asset_history_asset_id', 'asset_history', ['asset_id'])


def downgrade() -> None:
    op.drop_table('asset_history')
    op.drop_table('asset_relationships')
    op.drop_table('asset_tags')
    op.drop_table('asset_groups')
    op.drop_table('asset_owners')
    op.drop_table('asset_risks')
    op.drop_column('assets', 'discovery_source')
    op.drop_column('assets', 'risk_score')
    op.drop_column('assets', 'serial_number')
    op.drop_column('assets', 'vendor')
    op.drop_column('assets', 'environment')
